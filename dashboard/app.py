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
import psutil

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    """Initialize the database with tables."""
    conn = sqlite3.connect('gotlockz.db')
    cursor = conn.cursor()
    
    # Create picks table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pick_number INTEGER NOT NULL,
            pick_type TEXT NOT NULL,
            bet_details TEXT NOT NULL,
            odds TEXT,
            analysis TEXT,
            confidence_score INTEGER,
            edge_percentage REAL,
            result TEXT,
            profit_loss REAL,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/ping')
def ping():
    """Ping endpoint for bot connectivity test."""
    return jsonify({
        "message": "Dashboard is running",
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/bot-status')
def bot_status():
    """Get bot status and real-time information."""
    try:
        # Check if bot is running by looking for the process
        bot_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower() and any('bot.py' in cmd for cmd in proc.info['cmdline'] if cmd):
                    bot_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Get system stats
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        return jsonify({
            'bot_running': bot_running,
            'dashboard_running': True,
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available // (1024**3),  # GB
                'uptime': psutil.boot_time()
            },
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'bot_running': False,
            'dashboard_running': True,
            'error': str(e),
            'last_updated': datetime.now().isoformat()
        })

@app.route('/api/picks')
def get_picks():
    conn = sqlite3.connect('gotlockz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM picks ORDER BY posted_at DESC')
    picks = cursor.fetchall()
    conn.close()
    
    pick_list = []
    for pick in picks:
        pick_list.append({
            "id": pick[0],
            "pick_number": pick[1],
            "pick_type": pick[2],
            "bet_details": pick[3],
            "odds": pick[4],
            "analysis": pick[5],
            "confidence_score": pick[6],
            "edge_percentage": pick[7],
            "result": pick[8],
            "profit_loss": pick[9],
            "posted_at": pick[10]
        })
    
    return jsonify(pick_list)

@app.route('/api/picks/add', methods=['POST'])
def add_pick():
    """Add a new pick to the database."""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        conn = sqlite3.connect('gotlockz.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO picks (pick_number, pick_type, bet_details, odds, analysis, confidence_score, edge_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('pick_number'),
            data.get('pick_type'),
            data.get('bet_details'),
            data.get('odds', '-110'),
            data.get('analysis', ''),
            data.get('confidence_score', 7),
            data.get('edge_percentage', 3.0)
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Pick added successfully', 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/picks/update-result', methods=['POST'])
def update_pick_result():
    """Update the result of a pick."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        conn = sqlite3.connect('gotlockz.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE picks 
            SET result = ?, profit_loss = ?
            WHERE pick_number = ? AND pick_type = ?
        ''', (
            data.get('result'),
            data.get('profit_loss', 0.0),
            data.get('pick_number'),
            data.get('pick_type')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Pick result updated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get overall statistics."""
    conn = sqlite3.connect('gotlockz.db')
    cursor = conn.cursor()
    
    # Total picks
    cursor.execute('SELECT COUNT(*) FROM picks')
    total_picks = cursor.fetchone()[0]
    
    # Wins
    cursor.execute('SELECT COUNT(*) FROM picks WHERE result = "win"')
    wins = cursor.fetchone()[0]
    
    # Losses
    cursor.execute('SELECT COUNT(*) FROM picks WHERE result = "loss"')
    losses = cursor.fetchone()[0]
    
    # Pending
    cursor.execute('SELECT COUNT(*) FROM picks WHERE result IS NULL')
    pending = cursor.fetchone()[0]
    
    # Total profit/loss
    cursor.execute('SELECT SUM(profit_loss) FROM picks WHERE profit_loss IS NOT NULL')
    total_pl = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return jsonify({
        "total_picks": total_picks,
        "wins": wins,
        "losses": losses,
        "pending": pending,
        "win_rate": (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0,
        "total_profit_loss": total_pl
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
    """Get daily performance data for the chart."""
    try:
        period = request.args.get('period', '30d')
        
        # Calculate days based on period
        if period == '7d':
            days = 7
        elif period == '90d':
            days = 90
        else:  # 30d default
            days = 30
            
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        conn = sqlite3.connect('gotlockz.db')
        cursor = conn.cursor()
        
        # Get daily performance data
        cursor.execute('''
            SELECT 
                DATE(posted_at) as date,
                COUNT(*) as total_picks,
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(profit_loss) as daily_profit
            FROM picks 
            WHERE posted_at >= ? AND posted_at <= ?
            GROUP BY DATE(posted_at)
            ORDER BY date
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        daily_data = cursor.fetchall()
        conn.close()
        
        # Format data for chart
        performance_data = []
        for row in daily_data:
            date, total_picks, wins, daily_profit = row
            win_rate = (wins / total_picks * 100) if total_picks > 0 else 0
            
            performance_data.append({
                'date': date,
                'profit': daily_profit or 0,
                'win_rate': win_rate,
                'total_picks': total_picks
            })
        
        return jsonify(performance_data)
        
    except Exception as e:
        return jsonify([])

@app.route('/api/analytics')
def get_analytics():
    """Get comprehensive analytics data."""
    try:
        conn = sqlite3.connect('gotlockz.db')
        cursor = conn.cursor()
        
        # Get overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_picks,
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN result = 'push' THEN 1 ELSE 0 END) as pushes,
                SUM(profit_loss) as total_profit,
                AVG(confidence_score) as avg_confidence,
                AVG(edge_percentage) as avg_edge
            FROM picks
        ''')
        
        overall_stats = cursor.fetchone()
        
        # Get performance by pick type
        cursor.execute('''
            SELECT 
                pick_type,
                COUNT(*) as total,
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(profit_loss) as profit,
                AVG(confidence_score) as avg_confidence
            FROM picks 
            GROUP BY pick_type
        ''')
        
        type_stats = cursor.fetchall()
        
        # Get monthly performance
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', posted_at) as month,
                COUNT(*) as picks,
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(profit_loss) as profit
            FROM picks 
            GROUP BY strftime('%Y-%m', posted_at)
            ORDER BY month DESC
            LIMIT 12
        ''')
        
        monthly_stats = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'overall': {
                'total_picks': overall_stats[0] or 0,
                'wins': overall_stats[1] or 0,
                'losses': overall_stats[2] or 0,
                'pushes': overall_stats[3] or 0,
                'total_profit': overall_stats[4] or 0,
                'avg_confidence': overall_stats[5] or 0,
                'avg_edge': overall_stats[6] or 0
            },
            'by_type': [
                {
                    'type': row[0],
                    'total': row[1],
                    'wins': row[2],
                    'profit': row[3] or 0,
                    'avg_confidence': row[4] or 0
                } for row in type_stats
            ],
            'monthly': [
                {
                    'month': row[0],
                    'picks': row[1],
                    'wins': row[2],
                    'profit': row[3] or 0
                } for row in monthly_stats
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_pick_history():
    """Get detailed pick history with filtering."""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        pick_type = request.args.get('type', '')
        result = request.args.get('result', '')
        
        offset = (page - 1) * limit
        
        conn = sqlite3.connect('gotlockz.db')
        cursor = conn.cursor()
        
        # Build query with filters
        query = '''
            SELECT 
                pick_number, pick_type, bet_details, odds, result, 
                profit_loss, confidence_score, edge_percentage, posted_at, analysis
            FROM picks 
            WHERE 1=1
        '''
        params = []
        
        if pick_type:
            query += ' AND pick_type = ?'
            params.append(pick_type)
        
        if result:
            query += ' AND result = ?'
            params.append(result)
        
        query += ' ORDER BY posted_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        picks = cursor.fetchall()
        
        # Get total count for pagination
        count_query = 'SELECT COUNT(*) FROM picks WHERE 1=1'
        count_params = []
        
        if pick_type:
            count_query += ' AND pick_type = ?'
            count_params.append(pick_type)
        
        if result:
            count_query += ' AND result = ?'
            count_params.append(result)
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'picks': [
                {
                    'pick_number': row[0],
                    'pick_type': row[1],
                    'bet_details': row[2],
                    'odds': row[3],
                    'result': row[4],
                    'profit_loss': row[5] or 0,
                    'confidence_score': row[6] or 0,
                    'edge_percentage': row[7] or 0,
                    'posted_at': row[8],
                    'analysis': row[9] or ''
                } for row in picks
            ],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications')
def get_notifications():
    """Get notification settings and recent notifications."""
    try:
        # This would typically come from a notifications table
        # For now, return mock data
        return jsonify({
            'settings': {
                'email_notifications': True,
                'discord_notifications': True,
                'new_pick_alerts': True,
                'result_alerts': True,
                'performance_alerts': True
            },
            'recent_notifications': [
                {
                    'id': 1,
                    'type': 'new_pick',
                    'message': 'New VIP pick posted: Lakers -5.5',
                    'timestamp': datetime.now().isoformat(),
                    'read': False
                },
                {
                    'id': 2,
                    'type': 'result',
                    'message': 'Pick #123 resulted in WIN (+$50.00)',
                    'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'read': True
                }
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings')
def get_settings():
    """Get dashboard settings."""
    try:
        # This would typically come from a settings table
        return jsonify({
            'dashboard': {
                'auto_refresh': True,
                'refresh_interval': 30,
                'theme': 'dark',
                'chart_type': 'line'
            },
            'notifications': {
                'email': True,
                'discord': True,
                'browser': True
            },
            'display': {
                'show_confidence': True,
                'show_edge': True,
                'show_analysis': True
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/help')
def get_help():
    """Get help documentation."""
    try:
        return jsonify({
            'sections': [
                {
                    'title': 'Getting Started',
                    'content': 'Learn how to use the GotLockz Dashboard to track your betting performance.',
                    'items': [
                        'Understanding the Dashboard Layout',
                        'Reading Performance Charts',
                        'Adding and Managing Picks',
                        'Exporting Data'
                    ]
                },
                {
                    'title': 'Bot Integration',
                    'content': 'How the Discord bot works with the dashboard.',
                    'items': [
                        'Bot Status Monitoring',
                        'Automatic Pick Tracking',
                        'Real-time Updates',
                        'Troubleshooting'
                    ]
                },
                {
                    'title': 'Analytics',
                    'content': 'Understanding your betting performance metrics.',
                    'items': [
                        'Win Rate Analysis',
                        'Profit Tracking',
                        'ROI Calculations',
                        'Trend Analysis'
                    ]
                }
            ],
            'faq': [
                {
                    'question': 'How often does the dashboard update?',
                    'answer': 'The dashboard automatically refreshes every 30 seconds. You can also manually refresh using the refresh button.'
                },
                {
                    'question': 'Can I add picks manually?',
                    'answer': 'Yes! Use the "Add Pick" button to manually add picks to the database.'
                },
                {
                    'question': 'How do I export my data?',
                    'answer': 'Click the "Export Data" button to download your picks as a CSV file.'
                }
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync-discord', methods=['POST'])
def sync_discord():
    """Upsert picks from Discord into the dashboard database."""
    try:
        data = request.json
        if not data or not isinstance(data, list):
            return jsonify({'success': False, 'error': 'Invalid data'}), 400
        
        conn = sqlite3.connect('gotlockz.db')
        cursor = conn.cursor()
        for pick in data:
            # Upsert based on unique pick_number and pick_type
            cursor.execute('''
                SELECT COUNT(*) FROM picks WHERE pick_number = ? AND pick_type = ?
            ''', (pick.get('pick_number'), pick.get('pick_type')))
            exists = cursor.fetchone()[0]
            if exists:
                # Update existing pick
                cursor.execute('''
                    UPDATE picks SET
                        bet_details = ?, odds = ?, analysis = ?, posted_at = ?,
                        confidence_score = ?, edge_percentage = ?, result = ?, profit_loss = ?
                    WHERE pick_number = ? AND pick_type = ?
                ''', (
                    pick.get('bet_details'),
                    pick.get('odds'),
                    pick.get('analysis', ''),
                    pick.get('posted_at'),
                    pick.get('confidence_score', 0),
                    pick.get('edge_percentage', 0.0),
                    pick.get('result'),
                    pick.get('profit_loss', 0.0),
                    pick.get('pick_number'),
                    pick.get('pick_type')
                ))
            else:
                # Insert new pick
                cursor.execute('''
                    INSERT INTO picks (
                        pick_number, pick_type, bet_details, odds, analysis, posted_at,
                        confidence_score, edge_percentage, result, profit_loss
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pick.get('pick_number'),
                    pick.get('pick_type'),
                    pick.get('bet_details'),
                    pick.get('odds'),
                    pick.get('analysis', ''),
                    pick.get('posted_at'),
                    pick.get('confidence_score', 0),
                    pick.get('edge_percentage', 0.0),
                    pick.get('result'),
                    pick.get('profit_loss', 0.0)
                ))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Synced {len(data)} picks'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    # For Hugging Face Spaces, use port 7860
    port = int(os.environ.get('PORT', 7860))
    app.run(debug=False, host='0.0.0.0', port=port)
