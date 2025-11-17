# Quick Start Guide - Appointment Dashboard

## 🚀 Setup (One-time)

1. **Ensure backend is running:**
```bash
# In backend directory
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Environment is already configured:**
The `.env.local` file has been created with default settings.

## ▶️ Run the Dashboard

```bash
# Navigate to frontend directory
cd frontend

# Start development server
bun run dev
```

## 📱 Access the Dashboard

Open your browser and go to:
- **Dashboard:** [http://localhost:3000/appointments](http://localhost:3000/appointments)
- **Home:** [http://localhost:3000](http://localhost:3000)

## 🎨 What You'll See

- **Real-time connection status** in the top-right corner
- **Date selector** to view appointments for different dates
- **Doctor sections** with their appointments grouped
- **Appointment cards** showing:
  - Patient name, phone, age
  - Slot number
  - Queue position (if checked in)
  - Check-in button (for booked appointments)

## 🔵 Color Coding

- **Blue border** (left stripe) = Booked appointment
- **Green background** = Checked-in appointment
- **Blue badge** = "Booked" status
- **Green badge** = "✓ Checked In" status

## 🎯 Testing Check-In

1. Find a **booked** appointment (blue left border)
2. Click the **"Check In"** button
3. Card will turn green (optimistic update)
4. Success toast will appear
5. All connected clients will see the update in real-time!

## 🔌 WebSocket Connection

- **Auto-connects** on page load
- **Auto-reconnects** if connection drops (up to 5 attempts)
- **Manual retry** button if connection fails
- **Status indicator** shows: Connecting → Connected → Disconnected/Error

## 🐛 Troubleshooting

### WebSocket won't connect?
```bash
# Test backend WebSocket manually
wscat -c ws://localhost:8000/api/v1/ws/queue

# Or check if backend is running
curl http://localhost:8000/health
```

### Localhost not working on Windows?
Update `.env.local` to use `127.0.0.1` or your IP:
```env
NEXT_PUBLIC_WS_URL=ws://127.0.0.1:8000/api/v1/ws/queue
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## 📦 Tech Stack

- **Next.js 15** (App Router)
- **TypeScript** (Strict mode)
- **Tailwind CSS** (Styling)
- **shadcn/ui** (UI components)
- **WebSocket** (Real-time updates)
- **Bun** (Runtime & package manager)

## 🎉 Features

✅ Real-time WebSocket updates  
✅ Optimistic UI for check-ins  
✅ Auto-reconnect with backoff  
✅ Accessible (ARIA, keyboard nav)  
✅ Responsive design  
✅ Error handling with toasts  
✅ Blue-themed design  

Enjoy your real-time appointment dashboard! 🎊
