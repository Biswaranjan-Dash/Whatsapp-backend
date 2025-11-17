"""
Simple WebSocket client to monitor clinic queue updates in real-time.
Connects to the clinic WebSocket endpoint and displays snapshots and updates.
"""
import asyncio
import websockets
import json
from datetime import datetime


async def monitor_websocket(url: str = "ws://127.0.0.1:8000/api/v1/ws/queue", subscribe_date: str = None):
    """
    Connect to the WebSocket and display all messages received.
    
    Args:
        url: WebSocket URL (default: ws://127.0.0.1:8000/api/v1/ws/queue)
        subscribe_date: Date to subscribe to (default: today in YYYY-MM-DD format)
    
    Note: Uses 127.0.0.1 instead of localhost to avoid Windows IPv6/IPv4 issues
    """
    if subscribe_date is None:
        subscribe_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to {url}...")
    
    try:
        async with websockets.connect(url) as websocket:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Connected successfully!")
            
            # Send subscribe message
            subscribe_msg = {"action": "subscribe", "date": subscribe_date}
            await websocket.send(json.dumps(subscribe_msg))
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Subscribing to date: {subscribe_date}")
            print("-" * 80)
            
            # Receive and display messages
            async for message in websocket:
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                try:
                    data = json.loads(message)
                    message_type = data.get('type', 'unknown')
                    
                    print(f"\n[{timestamp}] Message Type: {message_type}")
                    print("=" * 80)
                    
                    if message_type == 'snapshot':
                        # Pretty print snapshot
                        doctors = data.get('data', {}).get('doctors', [])
                        print(f"Total Doctors: {len(doctors)}")
                        
                        for doc in doctors:
                            doctor_info = doc.get('doctor', {})
                            appointments = doc.get('appointments', [])
                            
                            print(f"\n  Doctor: {doctor_info.get('name')} (Code: {doctor_info.get('code')})")
                            print(f"  Specialization: {doctor_info.get('specialization')}")
                            print(f"  Appointments: {len(appointments)}")
                            
                            if appointments:
                                for idx, appt in enumerate(appointments, 1):
                                    patient = appt.get('patient', {})
                                    queue = appt.get('queue')
                                    
                                    print(f"\n    [{idx}] Patient: {patient.get('name')}")
                                    print(f"        Phone: {patient.get('phone_number')}")
                                    print(f"        Appointment ID: {appt.get('appointment_id')}")
                                    
                                    if queue:
                                        print(f"        Queue Position: {queue.get('position')}")
                                        print(f"        Status: {queue.get('status')}")
                                        print(f"        Checked In: {queue.get('checked_in_at', 'N/A')}")
                                    else:
                                        print(f"        Queue: Not checked in yet")
                    
                    elif message_type == 'update':
                        # Pretty print update
                        update_data = data.get('data', {})
                        print(f"  Doctor ID: {update_data.get('doctor_id')}")
                        print(f"  Date: {update_data.get('date')}")
                        print(f"  Action: Queue updated - check new snapshot")
                    
                    else:
                        # Print raw JSON for unknown types
                        print(json.dumps(data, indent=2))
                    
                    print("-" * 80)
                    
                except json.JSONDecodeError:
                    print(f"[{timestamp}] Raw message: {message}")
                    print("-" * 80)
    
    except websockets.exceptions.ConnectionClosed:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Connection closed by server")
    except ConnectionRefusedError:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✗ Connection refused - is the server running?")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")


async def main():
    """Main entry point"""
    print("=" * 80)
    print("CLINIC QUEUE WEBSOCKET MONITOR")
    print("=" * 80)
    print("\nPress Ctrl+C to stop\n")
    
    try:
        await monitor_websocket()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Stopped by user")


if __name__ == "__main__":
    asyncio.run(main())
