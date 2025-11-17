"use client";

import { useState, useEffect } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import { ConnectionStatusIndicator } from "@/components/ConnectionStatus";
import { DoctorSection } from "@/components/DoctorSection";
import { formatDate } from "@/lib/utils";
import { Calendar } from "lucide-react";

export default function AppointmentsPage() {
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    const today = new Date();
    return today.toISOString().split("T")[0];
  });

  const [toastMessage, setToastMessage] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  const { status, data, retry } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/ws/queue",
    date: selectedDate,
    onSnapshot: (snapshot) => {
      console.log("Received snapshot:", snapshot);
    },
    onUpdate: (update) => {
      console.log("Received update:", update);
    },
    onError: (error) => {
      showToast("error", error);
    },
  });

  const showToast = (type: "success" | "error", message: string) => {
    setToastMessage({ type, message });
    setTimeout(() => setToastMessage(null), 5000);
  };

  const handleCheckInSuccess = (appointmentId: string) => {
    showToast("success", "Patient checked in successfully!");
  };

  const handleCheckInError = (error: string) => {
    showToast("error", error);
  };

  // Auto-dismiss toast
  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => setToastMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [toastMessage]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-blue-100 bg-white/80 backdrop-blur-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Appointment Dashboard
              </h1>
              <p className="text-sm text-gray-600">
                Real-time queue monitoring system
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              {/* Date Selector */}
              <div className="flex items-center gap-2 rounded-lg border border-blue-200 bg-white px-4 py-2 shadow-sm">
                <Calendar className="h-4 w-4 text-blue-600" aria-hidden="true" />
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="border-none bg-transparent text-sm font-medium text-gray-700 outline-none"
                  aria-label="Select date"
                />
              </div>

              {/* Connection Status */}
              <ConnectionStatusIndicator status={status} onRetry={retry} />
            </div>
          </div>
        </div>
      </header>

      {/* Toast Notification */}
      {toastMessage && (
        <div
          className="fixed right-4 top-20 z-50 animate-in slide-in-from-top-2"
          role="alert"
          aria-live="assertive"
        >
          <div
            className={`rounded-lg border px-4 py-3 shadow-lg ${
              toastMessage.type === "success"
                ? "border-green-200 bg-green-50 text-green-800"
                : "border-red-200 bg-red-50 text-red-800"
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">{toastMessage.message}</span>
              <button
                onClick={() => setToastMessage(null)}
                className="ml-2 text-gray-500 hover:text-gray-700"
                aria-label="Close notification"
              >
                ×
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {status === "connected" && data ? (
          <div className="space-y-8">
            {/* Stats Overview */}
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <div className="mb-2 text-sm font-medium text-gray-600">
                {formatDate(data.date)}
              </div>
              <div className="flex gap-6 text-sm">
                <div>
                  <span className="font-semibold text-gray-900">
                    {data.total_doctors}
                  </span>
                  <span className="text-gray-600"> Doctors</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-900">
                    {data.total_appointments}
                  </span>
                  <span className="text-gray-600"> Total Appointments</span>
                </div>
              </div>
            </div>

            {/* Doctor Sections */}
            <div className="space-y-8">
              {data.doctors.length === 0 ? (
                <div className="rounded-lg border border-dashed border-gray-300 bg-white p-12 text-center">
                  <p className="text-gray-500">
                    No appointments scheduled for this date
                  </p>
                </div>
              ) : (
                data.doctors.map((doctorData) => (
                  <DoctorSection
                    key={doctorData.doctor.id}
                    doctorData={doctorData}
                    onCheckInSuccess={handleCheckInSuccess}
                    onCheckInError={handleCheckInError}
                  />
                ))
              )}
            </div>
          </div>
        ) : status === "connecting" ? (
          <div className="flex h-64 items-center justify-center">
            <div className="text-center">
              <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
              <p className="text-gray-600">Connecting to server...</p>
            </div>
          </div>
        ) : (
          <div className="flex h-64 items-center justify-center">
            <div className="text-center">
              <p className="mb-4 text-gray-600">
                Unable to connect to the server
              </p>
              <button
                onClick={retry}
                className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
              >
                Retry Connection
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
