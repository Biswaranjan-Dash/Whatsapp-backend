import { useState } from "react";
import type { Appointment } from "@/types/appointment";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { checkInPatient } from "@/lib/api";
import { formatPhone, formatTime, cn } from "@/lib/utils";
import { User, Phone, Calendar, Clock } from "lucide-react";

interface AppointmentCardProps {
  appointment: Appointment;
  onCheckInSuccess?: (appointmentId: string) => void;
  onCheckInError?: (error: string) => void;
}

export function AppointmentCard({
  appointment,
  onCheckInSuccess,
  onCheckInError,
}: AppointmentCardProps) {
  const [isCheckingIn, setIsCheckingIn] = useState(false);
  const [optimisticStatus, setOptimisticStatus] = useState(appointment.status);

  const isCheckedIn = optimisticStatus === "checked_in";
  const isBooked = optimisticStatus === "booked";

  const handleCheckIn = async () => {
    if (!isBooked || isCheckingIn) return;

    setIsCheckingIn(true);
    setOptimisticStatus("checked_in");

    try {
      await checkInPatient(appointment.appointment_id, appointment.patient.id);
      onCheckInSuccess?.(appointment.appointment_id);
    } catch (error) {
      // Rollback optimistic update
      setOptimisticStatus(appointment.status);
      const errorMessage =
        error instanceof Error ? error.message : "Check-in failed";
      onCheckInError?.(errorMessage);
    } finally {
      setIsCheckingIn(false);
    }
  };

  return (
    <Card
      className={cn(
        "relative overflow-hidden transition-all hover:shadow-md",
        isCheckedIn && "border-green-300 bg-green-50",
        isBooked && "border-l-4 border-l-blue-500"
      )}
      role="article"
      aria-label={`Appointment for ${appointment.patient.name}`}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 space-y-3">
            {/* Patient Info */}
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-gray-500" aria-hidden="true" />
                <h3 className="font-semibold text-gray-900">
                  {appointment.patient.name}
                </h3>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Phone className="h-3.5 w-3.5" aria-hidden="true" />
                <span>{formatPhone(appointment.patient.phone)}</span>
                {appointment.patient.age && (
                  <span className="text-gray-400">• {appointment.patient.age} yrs</span>
                )}
              </div>
            </div>

            {/* Appointment Details */}
            <div className="flex flex-wrap gap-3 text-sm">
              <div className="flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-gray-500" aria-hidden="true" />
                <span className="font-medium text-gray-700">
                  Slot {appointment.slot}
                </span>
              </div>

              {appointment.queue && (
                <div className="flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5 text-gray-500" aria-hidden="true" />
                  <span className="text-gray-600">
                    Position #{appointment.queue.position}
                  </span>
                  <span className="text-gray-400">
                    • {formatTime(appointment.queue.checked_in_at)}
                  </span>
                </div>
              )}
            </div>

            {/* Status Badge */}
            <div>
              <Badge
                variant={isCheckedIn ? "success" : "info"}
                className="text-xs"
              >
                {isCheckedIn ? "✓ Checked In" : "Booked"}
              </Badge>
            </div>
          </div>

          {/* Check-in Button */}
          {isBooked && (
            <div className="flex-shrink-0">
              <Button
                onClick={handleCheckIn}
                disabled={isCheckingIn}
                size="sm"
                className="bg-blue-600 hover:bg-blue-700"
                aria-label={`Check in ${appointment.patient.name}`}
              >
                {isCheckingIn ? (
                  <>
                    <div
                      className="h-3 w-3 animate-spin rounded-full border-2 border-white border-t-transparent"
                      aria-hidden="true"
                    />
                    <span>Checking In...</span>
                  </>
                ) : (
                  "Check In"
                )}
              </Button>
            </div>
          )}
        </div>

        {isCheckingIn && (
          <div
            className="absolute inset-0 bg-white/50 backdrop-blur-[2px]"
            aria-hidden="true"
          />
        )}
      </CardContent>
    </Card>
  );
}
