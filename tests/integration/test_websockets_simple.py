"""
Simplified WebSocket Integration Tests
These tests work with your running FastAPI server on localhost:8000
"""
import pytest
import asyncio
from datetime import date, timedelta
import websockets
import json
import uuid
import socket


TEST_WS_URL = "ws://192.168.0.192:8000"

# Set default timeout for all tests in this module
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.timeout(20)  # 20 second timeout for all tests
]


def is_server_running(host='192.168.0.192', port=8000):
    """Check if server is running"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except:
        return False


# Skip all WebSocket tests if server is not running and add timeout
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.timeout(20),  # 20 second timeout for all tests
    pytest.mark.skipif(
        not is_server_running(),
        reason="WebSocket tests require server running at 192.168.0.192:8000. Start with: $env:APP_ENV='test'; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    )
]


def get_unique_id():
    """Generate unique ID for test isolation"""
    return uuid.uuid4().hex[:8]


class TestWebSocketBasics:
    """Basic WebSocket connection tests"""
    
    @pytest.mark.asyncio
    async def test_ping_pong(self):
        """Test WebSocket ping/pong keep-alive"""
        async with websockets.connect(f"{TEST_WS_URL}/api/v1/ws/queue") as websocket:
            # Send ping
            await websocket.send(json.dumps({
                "action": "ping"
            }))
            
            # Should receive pong
            message_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(message_str)
            assert message['type'] == 'pong'
            assert 'timestamp' in message
            print(f"✅ Ping/Pong works! Response: {message}")
    
    @pytest.mark.asyncio
    async def test_invalid_date_format(self):
        """Test WebSocket with invalid date format"""
        async with websockets.connect(f"{TEST_WS_URL}/api/v1/ws/queue") as websocket:
            # Send subscribe with invalid date
            await websocket.send(json.dumps({
                "action": "subscribe",
                "date": "invalid-date"
            }))
            
            # Should receive error
            message_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(message_str)
            assert 'error' in message
            assert 'Invalid date format' in message['error']
            print(f"✅ Invalid date handling works! Error: {message['error']}")
    
    @pytest.mark.asyncio
    async def test_missing_date(self):
        """Test WebSocket subscription without date"""
        async with websockets.connect(f"{TEST_WS_URL}/api/v1/ws/queue") as websocket:
            # Send subscribe without date
            await websocket.send(json.dumps({
                "action": "subscribe"
            }))
            
            # Should receive error
            message_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(message_str)
            assert 'error' in message
            assert 'Missing' in message['error'] or 'required' in message['error'].lower()
            print(f"✅ Missing date handling works! Error: {message['error']}")
    
    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """Test WebSocket with unknown action"""
        async with websockets.connect(f"{TEST_WS_URL}/api/v1/ws/queue") as websocket:
            await websocket.send(json.dumps({
                "action": "invalid_action"
            }))
            
            message_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(message_str)
            assert 'error' in message
            assert 'Unknown action' in message['error']
            print(f"✅ Unknown action handling works! Error: {message['error']}")
    
    @pytest.mark.asyncio
    async def test_subscribe_to_future_date(self):
        """Test subscribing to a date with no appointments"""
        far_future = (date.today() + timedelta(days=365)).isoformat()
        
        async with websockets.connect(f"{TEST_WS_URL}/api/v1/ws/queue") as websocket:
            await websocket.send(json.dumps({
                "action": "subscribe",
                "date": far_future
            }))
            
            message_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            snapshot = json.loads(message_str)
            
            assert snapshot['type'] == 'snapshot'
            assert snapshot['data']['date'] == far_future
            assert snapshot['data']['total_doctors'] == 0
            assert snapshot['data']['total_appointments'] == 0
            assert snapshot['data']['doctors'] == []
            print(f"✅ Empty snapshot works! Date: {far_future}")
    
    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test WebSocket unsubscribe"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        async with websockets.connect(f"{TEST_WS_URL}/api/v1/ws/queue") as websocket:
            # Subscribe
            await websocket.send(json.dumps({
                "action": "subscribe",
                "date": tomorrow
            }))
            
            # Receive snapshot
            message_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(message_str)
            assert message['type'] == 'snapshot'
            print(f"✅ Subscribed to {tomorrow}")
            
            # Unsubscribe
            await websocket.send(json.dumps({
                "action": "unsubscribe"
            }))
            
            # Should receive confirmation
            message_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(message_str)
            assert message['type'] == 'unsubscribed'
            assert 'message' in message
            print(f"✅ Unsubscribe works! Message: {message['message']}")
    
    @pytest.mark.asyncio
    async def test_resubscribe_to_different_date(self):
        """Test resubscribing to a different date"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        day_after = (date.today() + timedelta(days=2)).isoformat()
        
        async with websockets.connect(f"{TEST_WS_URL}/api/v1/ws/queue") as websocket:
            # Subscribe to tomorrow
            await websocket.send(json.dumps({
                "action": "subscribe",
                "date": tomorrow
            }))
            
            message_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            snapshot1 = json.loads(message_str)
            assert snapshot1['data']['date'] == tomorrow
            print(f"✅ Subscribed to {tomorrow}: {snapshot1['data']['total_appointments']} appointments")
            
            # Resubscribe to day after
            await websocket.send(json.dumps({
                "action": "subscribe",
                "date": day_after
            }))
            
            message_str = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            snapshot2 = json.loads(message_str)
            assert snapshot2['data']['date'] == day_after
            print(f"✅ Resubscribed to {day_after}: {snapshot2['data']['total_appointments']} appointments")
    
    @pytest.mark.asyncio
    async def test_multiple_clients_same_date(self):
        """Test that multiple clients can subscribe to same date"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        # Connect two WebSocket clients
        async with websockets.connect(f"{TEST_WS_URL}/api/v1/ws/queue") as ws1:
            async with websockets.connect(f"{TEST_WS_URL}/api/v1/ws/queue") as ws2:
                # Both subscribe to same date
                await ws1.send(json.dumps({"action": "subscribe", "date": tomorrow}))
                await ws2.send(json.dumps({"action": "subscribe", "date": tomorrow}))
                
                # Both should receive snapshots
                snapshot1_str = await asyncio.wait_for(ws1.recv(), timeout=5.0)
                snapshot2_str = await asyncio.wait_for(ws2.recv(), timeout=5.0)
                snapshot1 = json.loads(snapshot1_str)
                snapshot2 = json.loads(snapshot2_str)
                
                assert snapshot1['type'] == 'snapshot'
                assert snapshot2['type'] == 'snapshot'
                assert snapshot1['data']['date'] == tomorrow
                assert snapshot2['data']['date'] == tomorrow
                print(f"✅ Multiple clients can connect! Both received snapshots for {tomorrow}")


if __name__ == "__main__":
    # Run tests with: pytest tests/integration/test_websockets_simple.py -v -s
    print("Run with: pytest tests/integration/test_websockets_simple.py -v -s")
