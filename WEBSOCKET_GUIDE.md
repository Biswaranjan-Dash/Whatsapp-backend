# WebSocket Real-time Queue Updates - Central Monitor

## 🔌 WebSocket Endpoint

```
ws://localhost:8000/api/v1/ws/queue
```

Or for network access:
```
ws://192.168.0.192:8000/api/v1/ws/queue
```

**Note:** This is a **central WebSocket** that streams ALL appointments across ALL doctors for a specific date. No doctor ID required!

## 📡 How It Works

1. **Connect** to the WebSocket endpoint (no parameters needed)
2. **Subscribe** by sending the date you want to monitor
3. **Receive** real-time updates for ALL doctors whenever:
   - Any patient books an appointment
   - Any patient checks in
   - Any queue status changes

This is perfect for:
- 📺 Central reception display
- 📊 Admin dashboard
- 📱 Hospital management app
- 🤖 WhatsApp bot serving multiple doctors

## 📤 Client → Server Messages

### Subscribe to a Date

```json
{
  "action": "subscribe",
  "date": "2025-11-17"
}
```

**Response**: You'll immediately receive a snapshot of all appointments and queue for that date.

### Unsubscribe

```json
{
  "action": "unsubscribe"
}
```

### Keep-Alive Ping

```json
{
  "action": "ping"
}
```

**Response**: 
```json
{
  "type": "pong",
  "timestamp": "2025-11-17T10:30:00"
}
```

## 📥 Server → Client Messages

### Initial Snapshot

When you first subscribe, you get the complete queue state for **all doctors**:

```json
{
  "type": "snapshot",
  "data": {
    "date": "2025-11-17",
    "total_appointments": 15,
    "total_doctors": 3,
    "doctors": [
      {
        "doctor": {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "name": "Dr. Smith",
          "code": "DOC001",
          "specialty": "Cardiology"
        },
        "total_appointments": 5,
        "checked_in_count": 2,
        "appointments": [
          {
            "appointment_id": "...",
            "slot": 1,
            "status": "confirmed",
            "patient": {
              "id": "...",
              "name": "John Doe",
              "phone": "+1234567890",
              "age": 45,
              "gender": "male"
            },
            "queue": {
              "position": 1,
              "checked_in_at": "2025-11-17T09:15:00",
              "called_at": null,
              "completed_at": null,
              "status": "checked_in"
            }
          }
          // ... more appointments for this doctor
        ]
      },
      {
        "doctor": {
          "id": "...",
          "name": "Dr. Johnson",
          "code": "DOC002",
          "specialty": "Neurology"
        },
        "total_appointments": 7,
        "checked_in_count": 3,
        "appointments": [...]
      }
      // ... more doctors
    ],
    "timestamp": "2025-11-17T10:30:00"
  }
}
```

### Real-time Updates

Whenever something changes (new booking, check-in, etc.), you receive:

```json
{
  "type": "update",
  "data": {
    // Same structure as snapshot
  }
}
```

## 🧪 Testing the WebSocket

### Option 1: HTML Test Client

1. Open `test_websocket.html` in your browser
2. Select a date (defaults to today)
3. Click "Subscribe"
4. Watch live updates for ALL doctors!

### Option 2: JavaScript Client

```javascript
// Connect to central WebSocket (no doctor ID!)
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/queue');

ws.onopen = () => {
  console.log('Connected to central queue!');
  
  // Subscribe to a date
  ws.send(JSON.stringify({
    action: 'subscribe',
    date: '2025-11-17'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
  
  if (message.type === 'snapshot' || message.type === 'update') {
    const data = message.data;
    console.log(`${data.total_doctors} doctors, ${data.total_appointments} appointments`);
    
    // Iterate through all doctors
    data.doctors.forEach(doctorData => {
      console.log(`\nDr. ${doctorData.doctor.name}:`);
      console.log(`  - ${doctorData.total_appointments} appointments`);
      console.log(`  - ${doctorData.checked_in_count} checked in`);
      
      doctorData.appointments.forEach(appt => {
        console.log(`    Slot ${appt.slot}: ${appt.patient.name}`);
      });
    });
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

### Option 3: Python Client

```python
import asyncio
import websockets
import json

async def monitor_central_queue():
    uri = "ws://localhost:8000/api/v1/ws/queue"
    
    async with websockets.connect(uri) as websocket:
        # Subscribe to date
        await websocket.send(json.dumps({
            "action": "subscribe",
            "date": "2025-11-17"
        }))
        
        # Listen for updates
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data['type']}")
            
            if data['type'] in ['snapshot', 'update']:
                queue = data['data']
                print(f"\nDate: {queue['date']}")
                print(f"Total: {queue['total_doctors']} doctors, {queue['total_appointments']} appointments\n")
                
                for doctor_data in queue['doctors']:
                    doctor = doctor_data['doctor']
                    print(f"Dr. {doctor['name']} ({doctor['specialty']}):")
                    print(f"  {doctor_data['total_appointments']} appointments, {doctor_data['checked_in_count']} checked in")
                    
                    for appt in doctor_data['appointments']:
                        status = f"[{appt['queue']['status']}]" if appt['queue'] else ""
                        print(f"    Slot {appt['slot']}: {appt['patient']['name']} {status}")
                    print()

asyncio.run(monitor_central_queue())
```

### Option 4: cURL/wscat

Install wscat:
```bash
npm install -g wscat
```

Connect and test:
```bash
wscat -c ws://localhost:8000/api/v1/ws/queue

# Once connected, type:
{"action": "subscribe", "date": "2025-11-17"}
```

## 📱 React/Next.js Integration Example

```typescript
import { useEffect, useState } from 'react';

interface DoctorQueueData {
  doctor: {
    id: string;
    name: string;
    code: string;
    specialty: string;
  };
  total_appointments: number;
  checked_in_count: number;
  appointments: Array<{
    appointment_id: string;
    slot: number;
    status: string;
    patient: {
      name: string;
      phone: string;
      age: number;
      gender: string;
    };
    queue?: {
      position: number;
      status: string;
      checked_in_at?: string;
    };
  }>;
}

interface CentralQueueData {
  date: string;
  total_appointments: number;
  total_doctors: number;
  doctors: DoctorQueueData[];
  timestamp: string;
}

export function useCentralQueueMonitor(date: string) {
  const [queueData, setQueueData] = useState<CentralQueueData | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!date) return;

    // No doctor ID needed - central WebSocket!
    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/queue`);

    ws.onopen = () => {
      setIsConnected(true);
      ws.send(JSON.stringify({
        action: 'subscribe',
        date: date
      }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === 'snapshot' || message.type === 'update') {
        setQueueData(message.data);
      }
    };

    ws.onerror = () => {
      setIsConnected(false);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    // Cleanup
    return () => {
      ws.close();
    };
  }, [date]);

  return { queueData, isConnected };
}

// Usage in component - Central Dashboard
function CentralQueueDashboard({ date }: { date: string }) {
  const { queueData, isConnected } = useCentralQueueMonitor(date);

  if (!isConnected) return <div>Connecting...</div>;
  if (!queueData) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <h1>Central Queue Monitor - {queueData.date}</h1>
      <div className="stats">
        <div>Total Doctors: {queueData.total_doctors}</div>
        <div>Total Appointments: {queueData.total_appointments}</div>
      </div>
      
      {queueData.doctors.map(doctorData => (
        <div key={doctorData.doctor.id} className="doctor-section">
          <h2>{doctorData.doctor.name}</h2>
          <p>{doctorData.doctor.specialty}</p>
          <p>
            {doctorData.total_appointments} appointments • 
            {doctorData.checked_in_count} checked in
          </p>
          
          {doctorData.appointments.map(appt => (
            <div key={appt.appointment_id} className="appointment">
              <strong>Slot {appt.slot}:</strong> {appt.patient.name}
              {appt.queue && (
                <span> - Position #{appt.queue.position} ({appt.queue.status})</span>
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
```

## 🔄 Events that Trigger Updates

The WebSocket automatically sends updates when:

1. **New Appointment Booked**
   - `POST /api/v1/appointments`
   - All subscribers to that doctor + date receive update

2. **Patient Checks In**
   - `POST /api/v1/checkins`
   - Queue positions updated in real-time

3. **Queue Status Changes**
   - When queue entries are modified
   - Position changes reflected immediately

## 🎯 Use Cases

1. **Central Reception Display**: Show live queue for ALL doctors on a TV screen
2. **Hospital Dashboard**: Monitor all departments in one view
3. **Mobile Admin App**: Track all appointments across the hospital
4. **Analytics System**: Real-time monitoring of patient flow
5. **WhatsApp Bot**: Serve multiple doctors from one WebSocket connection
6. **Load Balancing**: See which doctors have capacity
7. **Emergency Coordination**: Quick overview of all doctor availability

## 🔒 Production Considerations

### Authentication (TODO)

For production, you'd want to add authentication:

```python
@router.websocket("/ws/queue/{doctor_id}")
async def websocket_queue(
    websocket: WebSocket,
    doctor_id: UUID,
    token: str = Query(...),  # Add token verification
    db: AsyncSession = Depends(get_db)
):
    # Verify token
    user = await verify_token(token)
    if not user:
        await websocket.close(code=1008)  # Policy violation
        return
    
    # Rest of the code...
```

### Rate Limiting

Consider adding rate limits to prevent abuse:
- Max connections per IP
- Max subscriptions per user
- Message throttling

### Monitoring

Track WebSocket metrics:
- Active connections
- Messages per second
- Connection duration
- Error rates

## 📊 Example Output

When a patient checks in, all connected clients receive:

```json
{
  "type": "update",
  "data": {
    "doctor": {
      "name": "Dr. Smith",
      ...
    },
    "total_appointments": 10,
    "appointments": [
      {
        "slot": 1,
        "patient": {
          "name": "John Doe",
          ...
        },
        "queue": {
          "position": 1,
          "status": "checked_in",
          "checked_in_at": "2025-11-17T09:15:23"
        }
      },
      // ... rest of queue
    ]
  }
}
```

## 🐛 Troubleshooting

**Connection fails:**
- Check if server is running
- Verify doctor ID is valid UUID
- Check firewall/network settings

**No updates received:**
- Ensure you sent the subscribe message
- Check date format is YYYY-MM-DD
- Verify appointments exist for that date

**Connection drops:**
- Implement reconnection logic
- Send periodic ping messages
- Check network stability

## 🚀 Quick Start

1. Start the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Open `test_websocket.html` in browser

3. Select a date (defaults to today)

4. Click "Subscribe" and see ALL doctors' queues!

5. In another terminal, book an appointment or check in a patient:
   ```bash
   curl -X POST http://localhost:8000/api/v1/checkins \
     -H "Content-Type: application/json" \
     -d '{"appointment_id": "...", "patient_id": "..."}'
   ```

6. See the update appear instantly for ALL connected clients! 🎉

## 📊 Example Output

When ANY patient checks in to ANY doctor, ALL connected clients receive:

```json
{
  "type": "update",
  "data": {
    "date": "2025-11-17",
    "total_appointments": 15,
    "total_doctors": 3,
    "doctors": [
      {
        "doctor": { "name": "Dr. Smith", ... },
        "total_appointments": 5,
        "checked_in_count": 3,  // ← Updated!
        "appointments": [...]
      },
      // ... other doctors
    ]
  }
}
```
