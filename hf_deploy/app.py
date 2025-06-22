import gradio as gr
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('gotlockz.db')
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/ping')
def ping():
    return jsonify({
        "message": "Dashboard is running",
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/bot-status')
def bot_status():
    return jsonify({
        "bot_running": True,
        "dashboard_running": True,
        "timestamp": datetime.now().isoformat()
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

@app.route('/api/sync-discord', methods=['POST'])
def sync_discord():
    data = request.json
    conn = sqlite3.connect('gotlockz.db')
    cursor = conn.cursor()
    
    for pick in data:
        cursor.execute('''
            INSERT OR REPLACE INTO picks (pick_number, pick_type, bet_details, odds, analysis, confidence_score, edge_percentage, result, profit_loss, posted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pick.get('pick_number'),
            pick.get('pick_type'),
            pick.get('bet_details'),
            pick.get('odds', '-110'),
            pick.get('analysis', ''),
            pick.get('confidence_score', 7),
            pick.get('edge_percentage', 3.0),
            pick.get('result'),
            pick.get('profit_loss'),
            pick.get('posted_at', datetime.now().isoformat())
        ))
    
    conn.commit()
    conn.close()
    return jsonify({"message": f"Synced {len(data)} picks successfully"})

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=7860)

# Gradio interface
def create_gradio_interface():
    with gr.Blocks(title="GotLockz Dashboard") as demo:
        gr.HTML("""
        <div style="text-align: center; padding: 20px;">
            <h1>🏆 GotLockz Dashboard</h1>
            <p>Betting picks tracking and analytics</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div style="padding: 20px; background: #f0f0f0; border-radius: 10px;">
                    <h3>📊 Dashboard Features</h3>
                    <ul>
                        <li>Real-time pick tracking</li>
                        <li>Performance analytics</li>
                        <li>Discord bot integration</li>
                        <li>API endpoints available</li>
                    </ul>
                </div>
                """)
            
            with gr.Column():
                gr.HTML("""
                <div style="padding: 20px; background: #e8f5e8; border-radius: 10px;">
                    <h3>🔗 API Endpoints</h3>
                    <ul>
                        <li><code>/api/ping</code> - Health check</li>
                        <li><code>/api/picks</code> - Get picks</li>
                        <li><code>/api/sync-discord</code> - Sync from Discord</li>
                        <li><code>/api/bot-status</code> - Bot status</li>
                    </ul>
                </div>
                """)
    
    return demo

# Create and launch Gradio app
demo = create_gradio_interface()
demo.launch(server_name="0.0.0.0", server_port=7860)
