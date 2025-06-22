#!/usr/bin/env python3
"""
Test script to verify bot-dashboard connection
"""
import requests
import json
from datetime import datetime

def test_dashboard_connection():
    """Test dashboard connectivity"""
    try:
        response = requests.get("http://localhost:8080/api/ping", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is running and responding")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Dashboard responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard connection failed: {e}")
        return False

def test_sync_endpoint():
    """Test the sync endpoint"""
    try:
        test_picks = [
            {
                "pick_number": 1,
                "pick_type": "vip",
                "bet_details": "Lakers -5.5 vs Warriors",
                "odds": "-110",
                "analysis": "Test pick from connection test",
                "posted_at": datetime.now().isoformat(),
                "confidence_score": 8,
                "edge_percentage": 5.2,
                "result": "win",
                "profit_loss": 50.0
            }
        ]
        
        response = requests.post(
            "http://localhost:8080/api/sync-discord",
            json=test_picks,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Sync endpoint working")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Sync failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Sync test failed: {e}")
        return False

def test_add_pick():
    """Test adding a pick"""
    try:
        pick_data = {
            "pick_type": "free",
            "pick_number": 999,
            "bet_details": "Test Pick - Connection Test",
            "odds": "-110",
            "analysis": "Test pick added via connection test",
            "confidence_score": 7,
            "edge_percentage": 3.0
        }
        
        response = requests.post(
            "http://localhost:8080/api/picks/add",
            json=pick_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Add pick endpoint working")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Add pick failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Add pick test failed: {e}")
        return False

def main():
    print("🔍 Testing GotLockz Bot-Dashboard Connection")
    print("=" * 50)
    
    # Test dashboard connection
    dashboard_ok = test_dashboard_connection()
    
    if dashboard_ok:
        # Test sync endpoint
        sync_ok = test_sync_endpoint()
        
        # Test add pick endpoint
        add_ok = test_add_pick()
        
        print("\n" + "=" * 50)
        print("📊 Test Results:")
        print(f"Dashboard Connection: {'✅' if dashboard_ok else '❌'}")
        print(f"Sync Endpoint: {'✅' if sync_ok else '❌'}")
        print(f"Add Pick Endpoint: {'✅' if add_ok else '❌'}")
        
        if all([dashboard_ok, sync_ok, add_ok]):
            print("\n🎉 All tests passed! Bot and dashboard are properly connected.")
        else:
            print("\n⚠️ Some tests failed. Check the errors above.")
    else:
        print("\n❌ Dashboard is not running. Please start the dashboard first.")

if __name__ == "__main__":
    main() 