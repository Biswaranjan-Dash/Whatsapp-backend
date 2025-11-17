# Appointment Dashboard - Frontend

A real-time appointment monitoring dashboard built with Next.js, TypeScript, and Tailwind CSS. Connects to a FastAPI backend via WebSocket to display live appointment updates.

## Features

- ✅ Real-time WebSocket connection to backend
- ✅ Live appointment updates across all doctors
- ✅ Patient check-in functionality with optimistic UI
- ✅ Connection status indicator with auto-reconnect
- ✅ Accessible UI with ARIA attributes
- ✅ Blue-themed design with color-coded appointment states
- ✅ Responsive layout for mobile and desktop

## Prerequisites

- [Bun](https://bun.sh/) installed (v1.0.0+)
- Backend server running on `http://localhost:8000`

## Installation

1. **Install dependencies:**

```bash
bun install
```

2. **Install required packages:**

```bash
bun add lucide-react class-variance-authority clsx tailwind-merge
bun add @radix-ui/react-slot
```

## Environment Variables

Create a `.env.local` file in the frontend directory:

```env
# WebSocket URL
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/ws/queue

# API Base URL  
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note:** For network access (not localhost), use your IP address:
```env
NEXT_PUBLIC_WS_URL=ws://192.168.0.192:8000/api/v1/ws/queue
NEXT_PUBLIC_API_URL=http://192.168.0.192:8000
```

## Running the Development Server

```bash
bun run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000)

## Navigate to Appointments Page

Open [http://localhost:3000/appointments](http://localhost:3000/appointments) to view the dashboard.

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   └── appointments/
│   │       └── page.tsx          # Main dashboard page
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── card.tsx
│   │   │   ├── button.tsx
│   │   │   └── badge.tsx
│   │   ├── AppointmentCard.tsx   # Individual appointment card
│   │   ├── DoctorSection.tsx     # Doctor section with appointments
│   │   └── ConnectionStatus.tsx  # WebSocket status indicator
│   ├── hooks/
│   │   └── useWebSocket.ts       # WebSocket connection hook
│   ├── lib/
│   │   ├── api.ts                # API client functions
│   │   └── utils.ts              # Utility functions
│   └── types/
│       └── appointment.ts        # TypeScript type definitions
```

## Usage

### Viewing Appointments

1. The dashboard loads today's appointments by default
2. Use the date picker to view appointments for different dates
3. Connection status is shown in the top-right corner

### Checking In Patients

1. Locate the appointment card (blue left border = booked)
2. Click the "Check In" button
3. The card will optimistically turn green
4. Success/error toast will appear
5. WebSocket will send real-time update to all connected clients

### WebSocket Behavior

- **Auto-connect** on page load
- **Auto-reconnect** with exponential backoff (max 5 attempts)
- **Real-time updates** when appointments are booked or checked in
- **Manual retry** button if connection fails

## Color Coding

- **Blue** (`border-l-blue-500`): Booked appointments
- **Green** (`bg-green-50`, `border-green-300`): Checked-in appointments
- **Status badges**:
  - Blue "Booked" badge
  - Green "✓ Checked In" badge

## Accessibility

- Semantic HTML with proper heading hierarchy
- ARIA labels and roles for interactive elements
- Keyboard navigation support
- Screen reader announcements for status changes
- Color contrast compliant with WCAG AA

## API Integration

### Check-In Endpoint

```typescript
POST /api/v1/checkins
Content-Type: application/json

{
  "appointment_id": "uuid",
  "patient_id": "uuid"
}
```

### WebSocket Messages

**Subscribe:**
```json
{
  "action": "subscribe",
  "date": "2025-11-18"
}
```

**Snapshot Response:**
```json
{
  "type": "snapshot",
  "data": {
    "date": "2025-11-18",
    "total_appointments": 10,
    "total_doctors": 3,
    "doctors": [...]
  }
}
```

## Troubleshooting

### WebSocket won't connect

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check WebSocket endpoint: `wscat -c ws://localhost:8000/api/v1/ws/queue`
3. If using IP address, update `.env.local` with your IP
4. Check browser console for connection errors

### Check-in fails

1. Verify appointment exists and is in "booked" status
2. Check patient ID matches the appointment
3. Ensure backend database is accessible
4. Check browser network tab for API errors

### Localhost issues on Windows

If `localhost` doesn't work, use `127.0.0.1` or your IP address (`192.168.0.192`) in the environment variables.

## Building for Production

```bash
bun run build
bun run start
```

## Development Notes

- Uses Next.js 15 App Router
- TypeScript strict mode enabled
- Tailwind CSS for styling
- shadcn/ui components for UI primitives
- Optimistic UI updates for better UX
- Error boundaries for graceful error handling

## License

MIT
