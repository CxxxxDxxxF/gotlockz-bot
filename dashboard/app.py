#!/usr/bin/env python3
"""
dashboard/app.py

Flask web dashboard for GotLockz bot performance tracking.
Shows pick success rates, ROI, and analytics.
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    """Initialize the database with tables."""
    conn = sqlite3.connect('gotlockz.db')
    cursor = conn.cursor()
    
    # Picks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pick_number INTEGER,
            pick_type TEXT,
            bet_details TEXT,
            odds TEXT,
            analysis TEXT,
            posted_at TIMESTAMP,
            result TEXT DEFAULT 'pending',
            profit_loss REAL DEFAULT 0.0,
            confidence_score INTEGER,
            edge_percentage REAL
        )
    ''')
    
    # Performance metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            total_picks INTEGER,
            wins INTEGER,
            losses INTEGER,
            pushes INTEGER,
            total_profit REAL,
            roi_percentage REAL
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get overall statistics."""
    conn = sqlite3.connect('gotlockz.db')
    cursor = conn.cursor()
    
    # Overall stats
    cursor.execute('''
        SELECT 
            COUNT(*) as total_picks,
            SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
            SUM(CASE WHEN result = 'push' THEN 1 ELSE 0 END) as pushes,
            SUM(profit_loss) as total_profit
        FROM picks 
        WHERE result != 'pending'
    ''')
    
    stats = cursor.fetchone()
    total_picks, wins, losses, pushes, total_profit = stats
    
    # Calculate ROI
    roi = (total_profit / (total_picks * 100)) * 100 if total_picks > 0 else 0
    
    # Recent picks
    cursor.execute('''
        SELECT pick_type, bet_details, odds, result, profit_loss, posted_at
        FROM picks 
        ORDER BY posted_at DESC 
        LIMIT 10
    ''')
    
    recent_picks = []
    for row in cursor.fetchall():
        recent_picks.append({
            'type': row[0],
            'bet': row[1],
            'odds': row[2],
            'result': row[3],
            'profit_loss': row[4],
            'posted_at': row[5]
        })
    
    conn.close()
    
    return jsonify({
        'total_picks': total_picks,
        'wins': wins,
        'losses': losses,
        'pushes': pushes,
        'total_profit': total_profit,
        'roi_percentage': roi,
        'win_rate': (wins / total_picks * 100) if total_picks > 0 else 0,
        'recent_picks': recent_picks
    })

@app.route('/api/picks/<pick_type>')
def get_picks_by_type(pick_type):
    """Get picks by type (vip, lotto, free)."""
    conn = sqlite3.connect('gotlockz.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT pick_number, bet_details, odds, result, profit_loss, confidence_score, edge_percentage
        FROM picks 
        WHERE pick_type = ? AND result != 'pending'
        ORDER BY posted_at DESC
    ''', (pick_type,))
    
    picks = []
    for row in cursor.fetchall():
        picks.append({
            'pick_number': row[0],
            'bet': row[1],
            'odds': row[2],
            'result': row[3],
            'profit_loss': row[4],
            'confidence': row[5],
            'edge': row[6]
        })
    
    conn.close()
    return jsonify(picks)

@app.route('/api/performance/daily')
def get_daily_performance():
    """Get daily performance over the last 30 days."""
    conn = sqlite3.connect('gotlockz.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            DATE(posted_at) as date,
            COUNT(*) as picks,
            SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
            SUM(profit_loss) as profit
        FROM picks 
        WHERE posted_at >= DATE('now', '-30 days')
        GROUP BY DATE(posted_at)
        ORDER BY date
    ''')
    
    daily_data = []
    for row in cursor.fetchall():
        daily_data.append({
            'date': row[0],
            'picks': row[1],
            'wins': row[2],
            'profit': row[3],
            'win_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0
        })
    
    conn.close()
    return jsonify(daily_data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
