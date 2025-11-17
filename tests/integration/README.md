# WebSocket Integration Tests

This directory contains comprehensive integration tests for the WebSocket real-time queue monitoring system.

## 📋 Test Coverage

### 1. Connection Tests (`TestWebSocketConnection`)
- ✅ Basic WebSocket connection and subscription
- ✅ Invalid date format handling
- ✅ Missing date parameter handling
- ✅ Ping/pong keep-alive mechanism
- ✅ Unsubscribe functionality

### 2. Real-Time Update Tests (`TestWebSocketRealTimeUpdates`)
- ✅ Appointment booking triggers WebSocket update
- ✅ Patient check-in triggers WebSocket update
- ✅ Queue position updates in real-time

### 3. Multiple Clients Tests (`TestWebSocketMultipleClients`)
- ✅ Multiple clients receive same updates
- ✅ Broadcast mechanism works correctly

### 4. Multiple Doctors Tests (`TestWebSocketMultipleDoctors`)
- ✅ Snapshot includes all doctors with appointments
- ✅ Empty date returns empty snapshot
- ✅ Central monitoring across all doctors

### 5. Edge Cases Tests (`TestWebSocketEdgeCases`)
- ✅ Unknown action handling
- ✅ Resubscribe to different dates
- ✅ Error message formats

## 🚀 Running the Tests

### Prerequisites

1. **PostgreSQL Test Database**: Create a test database
   ```sql
   CREATE DATABASE clinic_test_db;
   ```

2. **Install Test Dependencies**:
   ```bash
   pip install pytest pytest-asyncio httpx websockets
   ```

### Run All WebSocket Tests

```bash
pytest tests/integration/test_websockets.py -v
```

### Run Specific Test Class

```bash
# Test only connection logic
pytest tests/integration/test_websockets.py::TestWebSocketConnection -v

# Test only real-time updates
pytest tests/integration/test_websockets.py::TestWebSocketRealTimeUpdates -v

# Test only multiple clients
pytest tests/integration/test_websockets.py::TestWebSocketMultipleClients -v
```

### Run Specific Test

```bash
pytest tests/integration/test_websockets.py::TestWebSocketConnection::test_websocket_connect_and_subscribe -v
```

### Run with Coverage

```bash
pytest tests/integration/test_websockets.py --cov=app.api.v1.routers.websockets --cov-report=html
```

## 📊 Test Database

The tests use a separate test database (`clinic_test_db`) to avoid interfering with your development data.

**Configuration**:
- Database: `clinic_test_db`
- User: `postgres`
- Password: `postgres`
- Host: `localhost`
- Port: `5432`

Each test:
1. Creates fresh tables
2. Runs the test
3. Drops all tables
4. Cleans up

This ensures complete isolation between tests.

## 🧪 What Each Test Does

### Connection Tests

**test_websocket_connect_and_subscribe**:
- Creates a doctor and patient
- Books an appointment
- Connects to WebSocket
- Subscribes to a date
- Verifies snapshot contains correct data

**test_websocket_invalid_date_format**:
- Sends invalid date like "invalid-date"
- Verifies error message is returned

**test_websocket_ping_pong**:
- Sends ping message
- Verifies pong response with timestamp

### Real-Time Update Tests

**test_appointment_booking_triggers_update**:
- Connects WebSocket and subscribes
- Receives empty snapshot
- Books an appointment via API
- Waits for WebSocket update
- Verifies update contains new appointment

**test_checkin_triggers_update**:
- Sets up appointment
- Subscribes to WebSocket
- Checks in patient via API
- Verifies WebSocket update shows queue position

### Multiple Clients Test

**test_multiple_clients_receive_same_update**:
- Connects two WebSocket clients
- Both subscribe to same date
- Books one appointment
- Verifies both clients receive the update

### Multiple Doctors Test

**test_snapshot_includes_all_doctors**:
- Creates two doctors
- Books appointments for both
- Subscribes to date
- Verifies snapshot includes both doctors

## 🔧 Troubleshooting

### Test Database Connection Failed

If you see `connection refused` errors:

1. Ensure PostgreSQL is running:
   ```bash
   # Windows
   Get-Service postgresql*
   
   # Start if needed
   Start-Service postgresql-x64-16
   ```

2. Create test database if missing:
   ```sql
   CREATE DATABASE clinic_test_db;
   ```

3. Verify connection string in test file matches your setup

### Timeout Errors

If tests timeout waiting for WebSocket updates:

1. Check if notifications are properly triggered in your code
2. Increase timeout in `asyncio.wait_for()` calls
3. Add debug logging to see what's happening

### Import Errors

If you see `ModuleNotFoundError`:

```bash
# Install missing dependencies
pip install pytest pytest-asyncio httpx websockets

# Or install all dev dependencies
pip install -r requirements.txt
```

## 📈 Expected Output

When all tests pass, you should see:

```
tests/integration/test_websockets.py::TestWebSocketConnection::test_websocket_connect_and_subscribe PASSED
tests/integration/test_websockets.py::TestWebSocketConnection::test_websocket_invalid_date_format PASSED
tests/integration/test_websockets.py::TestWebSocketConnection::test_websocket_missing_date PASSED
tests/integration/test_websockets.py::TestWebSocketConnection::test_websocket_ping_pong PASSED
tests/integration/test_websockets.py::TestWebSocketConnection::test_websocket_unsubscribe PASSED
tests/integration/test_websockets.py::TestWebSocketRealTimeUpdates::test_appointment_booking_triggers_update PASSED
tests/integration/test_websockets.py::TestWebSocketRealTimeUpdates::test_checkin_triggers_update PASSED
tests/integration/test_websockets.py::TestWebSocketMultipleClients::test_multiple_clients_receive_same_update PASSED
tests/integration/test_websockets.py::TestWebSocketMultipleDoctors::test_snapshot_includes_all_doctors PASSED
tests/integration/test_websockets.py::TestWebSocketMultipleDoctors::test_empty_date_returns_empty_snapshot PASSED
tests/integration/test_websockets.py::TestWebSocketEdgeCases::test_unknown_action PASSED
tests/integration/test_websockets.py::TestWebSocketEdgeCases::test_resubscribe_to_different_date PASSED

============ 12 passed in 5.23s ============
```

## 🎯 Test Coverage Goals

Current coverage areas:
- ✅ WebSocket connection lifecycle
- ✅ Subscription/unsubscription
- ✅ Message formats (subscribe, ping, unsubscribe)
- ✅ Snapshot data structure
- ✅ Real-time update broadcasting
- ✅ Multiple concurrent clients
- ✅ Multiple doctors in single stream
- ✅ Error handling
- ✅ Edge cases

## 🔜 Future Test Ideas

1. **Load Testing**: Test with 100+ concurrent WebSocket connections
2. **Reconnection Logic**: Test automatic reconnection after disconnect
3. **Message Ordering**: Verify updates arrive in correct order
4. **Race Conditions**: Test simultaneous booking + check-in
5. **Memory Leaks**: Long-running connection tests
6. **Authentication**: Once auth is added, test token validation
7. **Rate Limiting**: Test message throttling if implemented

## 📝 Adding New Tests

To add a new test:

1. Add to appropriate test class or create new one
2. Follow async/await pattern
3. Use `db_session` fixture for database
4. Use `http_client` fixture for API calls
5. Clean up resources (WebSocket connections auto-close)

Example:

```python
@pytest.mark.asyncio
async def test_my_new_feature(self, db_session, http_client):
    """Test description"""
    # Setup
    doctor = await create_test_doctor(http_client)
    
    # Test WebSocket
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        async with client.websocket_connect("/api/v1/ws/queue") as websocket:
            await websocket.send_json({
                "action": "subscribe",
                "date": "2025-11-17"
            })
            
            message = await websocket.receive_json()
            assert message['type'] == 'snapshot'
```

## 🐛 Debugging Tests

Run with verbose output and no capture:

```bash
pytest tests/integration/test_websockets.py -v -s
```

Add print statements in tests:

```python
@pytest.mark.asyncio
async def test_something(self, db_session):
    print(f"Debug: {some_variable}")
    # ... rest of test
```

Use pytest's debugging:

```bash
pytest tests/integration/test_websockets.py --pdb
```

## 📚 Related Documentation

- [WebSocket API Guide](../../WEBSOCKET_GUIDE.md) - Complete API documentation
- [test_websocket.html](../../test_websocket.html) - Manual testing UI
- [FastAPI WebSocket Docs](https://fastapi.tiangolo.com/advanced/websockets/)
