import gradio as gr
import spaces
import json
from datetime import datetime

# Simple in-memory storage for demo
picks_data = []

@spaces.GPU
def get_stats():
    """Get dashboard statistics"""
    total_picks = len(picks_data)
    wins = len([p for p in picks_data if p.get('result') == 'win'])
    losses = len([p for p in picks_data if p.get('result') == 'loss'])
    pending = len([p for p in picks_data if not p.get('result')])
    
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    total_pl = sum([p.get('profit_loss', 0) for p in picks_data])
    
    return f"""📈 **Dashboard Statistics**\n\n🏆 Total Picks: {total_picks}\n✅ Wins: {wins}\n❌ Losses: {losses}\n⏳ Pending: {pending}\n📊 Win Rate: {win_rate:.1f}%\n💰 Total P/L: ${total_pl:.2f}"""

@spaces.GPU
def get_picks():
    """Get all picks"""
    if not picks_data:
        return "📋 No picks found yet.\n\nAdd some picks to get started!"
    
    result = "📊 Recent Picks:\n\n"
    for pick in picks_data[-10:]:  # Show last 10 picks
        result += f"**Pick #{pick['pick_number']}** ({pick['pick_type'].upper()})\n"
        result += f"Bet: {pick['bet_details']}\n"
        result += f"Odds: {pick.get('odds', '-110')}\n"
        result += f"Confidence: {pick.get('confidence_score', 7)}/10\n"
        if pick.get('result'):
            result += f"Result: {pick['result'].upper()}\n"
        result += f"Posted: {pick.get('posted_at', 'N/A')}\n"
        result += "---\n"
    
    return result

@spaces.GPU
def add_pick(pick_number, pick_type, bet_details, odds, analysis):
    """Add a new pick"""
    try:
        pick = {
            'pick_number': int(pick_number),
            'pick_type': pick_type.lower(),
            'bet_details': bet_details,
            'odds': odds or "-110",
            'analysis': analysis or "",
            'confidence_score': 7,
            'edge_percentage': 3.0,
            'posted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        picks_data.append(pick)
        return f"✅ Pick #{pick_number} ({pick_type}) added successfully!"
    except Exception as e:
        return f"❌ Error adding pick: {str(e)}"

@spaces.GPU
def sync_discord_picks(picks_json):
    """Sync picks from Discord"""
    try:
        picks = json.loads(picks_json)
        for pick in picks:
            pick['posted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            picks_data.append(pick)
        return f"✅ Synced {len(picks)} picks from Discord successfully!"
    except Exception as e:
        return f"❌ Error syncing picks: {str(e)}"

@spaces.GPU
def update_pick_result(pick_number, pick_type, result, profit_loss):
    """Update pick result"""
    try:
        for pick in picks_data:
            if pick['pick_number'] == int(pick_number) and pick['pick_type'] == pick_type.lower():
                pick['result'] = result
                pick['profit_loss'] = float(profit_loss or 0)
                return f"✅ Pick #{pick_number} result updated to {result}"
        return f"❌ Pick #{pick_number} not found"
    except Exception as e:
        return f"❌ Error updating pick: {str(e)}"

# API functions for bot integration
@spaces.GPU
def api_ping():
    """API endpoint for health check"""
    return json.dumps({"status": "ok", "message": "GotLockz API is running"})

@spaces.GPU
def api_stats():
    """API endpoint to get stats as JSON"""
    total_picks = len(picks_data)
    wins = len([p for p in picks_data if p.get('result') == 'win'])
    losses = len([p for p in picks_data if p.get('result') == 'loss'])
    pending = len([p for p in picks_data if not p.get('result')])
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    total_pl = sum([p.get('profit_loss', 0) for p in picks_data])
    
    stats = {
        'total_picks': total_picks,
        'wins': wins,
        'losses': losses,
        'pending': pending,
        'win_rate': win_rate,
        'total_pl': total_pl
    }
    return json.dumps(stats)

@spaces.GPU
def api_picks():
    """API endpoint to get all picks as JSON"""
    return json.dumps(picks_data)

@spaces.GPU
def api_add_pick(pick_data):
    """API endpoint to add a pick via JSON"""
    try:
        pick = json.loads(pick_data)
        pick['posted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        picks_data.append(pick)
        return json.dumps({'status': 'success', 'message': 'Pick added'})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@spaces.GPU
def api_sync_discord(picks_data_json):
    """API endpoint to sync picks from Discord"""
    try:
        picks = json.loads(picks_data_json)
        for pick in picks:
            pick['posted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            picks_data.append(pick)
        return json.dumps({'status': 'success', 'message': f'Synced {len(picks)} picks'})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@spaces.GPU
def api_bot_status():
    """API endpoint for bot status"""
    return json.dumps({'bot_running': True})

# Create Gradio interface
with gr.Blocks(title="GotLockz Dashboard", theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
        <h1>🏆 GotLockz Dashboard</h1>
        <p>Betting picks tracking and analytics platform</p>
        <p><strong>API Endpoints:</strong> Use the API tab below for bot integration</p>
    </div>
    """)
    
    with gr.Tabs():
        # Dashboard Overview Tab
        with gr.TabItem("📊 Dashboard"):
            stats_output = gr.Markdown()
            gr.Button("📈 Refresh Stats", variant="primary").click(
                fn=get_stats,
                outputs=stats_output
            )
        
        # View Picks Tab
        with gr.TabItem("📋 View Picks"):
            picks_output = gr.Markdown()
            gr.Button("🔄 Refresh Picks", variant="primary").click(
                fn=get_picks,
                outputs=picks_output
            )
        
        # Add Pick Tab
        with gr.TabItem("➕ Add Pick"):
            with gr.Row():
                with gr.Column():
                    pick_number = gr.Number(label="Pick Number", minimum=1)
                    pick_type = gr.Dropdown(
                        choices=["vip", "free", "lotto"],
                        label="Pick Type",
                        value="vip"
                    )
                    bet_details = gr.Textbox(label="Bet Details", placeholder="e.g., Lakers -5.5 vs Warriors")
                    odds = gr.Textbox(label="Odds", placeholder="-110", value="-110")
                    analysis = gr.Textbox(label="Analysis", placeholder="Optional analysis...", lines=3)
                    
                    add_button = gr.Button("➕ Add Pick", variant="primary")
                    add_output = gr.Textbox(label="Result")
                    
                    add_button.click(
                        fn=add_pick,
                        inputs=[pick_number, pick_type, bet_details, odds, analysis],
                        outputs=add_output
                    )
        
        # Update Results Tab
        with gr.TabItem("📝 Update Results"):
            with gr.Row():
                with gr.Column():
                    result_pick_number = gr.Number(label="Pick Number", minimum=1)
                    result_pick_type = gr.Dropdown(
                        choices=["vip", "free", "lotto"],
                        label="Pick Type",
                        value="vip"
                    )
                    result = gr.Dropdown(
                        choices=["win", "loss", "push"],
                        label="Result",
                        value="win"
                    )
                    profit_loss = gr.Number(label="Profit/Loss ($)", value=0)
                    
                    update_button = gr.Button("📝 Update Result", variant="primary")
                    update_output = gr.Textbox(label="Result")
                    
                    update_button.click(
                        fn=update_pick_result,
                        inputs=[result_pick_number, result_pick_type, result, profit_loss],
                        outputs=update_output
                    )
        
        # Sync Discord Tab
        with gr.TabItem("🔄 Sync Discord"):
            gr.HTML("""
            <div style="padding: 20px; background: #fff3cd; border-radius: 10px; margin-bottom: 20px;">
                <h3>🔄 Discord Sync</h3>
                <p>Paste JSON data from Discord bot to sync picks:</p>
            </div>
            """)
            
            picks_json = gr.Textbox(
                label="Discord Picks JSON",
                placeholder='[{"pick_number": 1, "pick_type": "vip", "bet_details": "Lakers -5.5"}]',
                lines=5
            )
            sync_button = gr.Button("🔄 Sync Picks", variant="primary")
            sync_output = gr.Textbox(label="Sync Result")
            
            sync_button.click(
                fn=sync_discord_picks,
                inputs=picks_json,
                outputs=sync_output
            )
        
        # API Tab for bot integration
        with gr.TabItem("🔌 API"):
            gr.HTML("""
            <div style="padding: 20px; background: #e3f2fd; border-radius: 10px; margin-bottom: 20px;">
                <h3>🔌 API Endpoints for Bot Integration</h3>
                <p>Use these endpoints to integrate with your Discord bot:</p>
                <ul>
                    <li><strong>POST /api_ping</strong> - Health check</li>
                    <li><strong>POST /api_stats</strong> - Get stats as JSON</li>
                    <li><strong>POST /api_picks</strong> - Get all picks as JSON</li>
                    <li><strong>POST /api_add_pick</strong> - Add a pick via JSON</li>
                    <li><strong>POST /api_sync_discord</strong> - Sync picks from Discord</li>
                    <li><strong>POST /api_bot_status</strong> - Bot status check</li>
                </ul>
                <p><strong>Note:</strong> Use POST requests with empty data: {"data": []}</p>
            </div>
            """)
            
            # API Test Section
            with gr.Row():
                with gr.Column():
                    gr.HTML("<h4>Test API Endpoints</h4>")
                    
                    # Test ping
                    ping_button = gr.Button("🏓 Test Ping", variant="secondary")
                    ping_output = gr.Textbox(label="Ping Result")
                    ping_button.click(fn=api_ping, outputs=ping_output)
                    
                    # Test stats
                    stats_button = gr.Button("📊 Test Stats", variant="secondary")
                    stats_output = gr.Textbox(label="Stats Result")
                    stats_button.click(fn=api_stats, outputs=stats_output)
                    
                    # Test get picks
                    picks_api_button = gr.Button("📋 Test Get Picks", variant="secondary")
                    picks_api_output = gr.Textbox(label="Picks Result")
                    picks_api_button.click(fn=api_picks, outputs=picks_api_output)
                
                with gr.Column():
                    gr.HTML("<h4>Test Add Pick</h4>")
                    
                    test_pick_data = gr.Textbox(
                        label="Test Pick JSON",
                        value='{"pick_number": 999, "pick_type": "test", "bet_details": "Test Bet", "odds": "-110"}',
                        lines=3
                    )
                    test_add_button = gr.Button("➕ Test Add Pick", variant="secondary")
                    test_add_output = gr.Textbox(label="Add Result")
                    test_add_button.click(fn=api_add_pick, inputs=test_pick_data, outputs=test_add_output)

demo.launch() 