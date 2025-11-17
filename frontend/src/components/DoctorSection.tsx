import type { DoctorWithAppointments } from "@/types/appointment";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { AppointmentCard } from "./AppointmentCard";
import { Stethoscope, Users, UserCheck } from "lucide-react";

interface DoctorSectionProps {
  doctorData: DoctorWithAppointments;
  onCheckInSuccess?: (appointmentId: string) => void;
  onCheckInError?: (error: string) => void;
}

export function DoctorSection({
  doctorData,
  onCheckInSuccess,
  onCheckInError,
}: DoctorSectionProps) {
  const { doctor, appointments, total_appointments, checked_in_count } = doctorData;

  return (
    <section
      className="space-y-4"
      aria-labelledby={`doctor-${doctor.id}`}
    >
      <Card className="border-blue-100 bg-gradient-to-r from-blue-50 to-white">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <CardTitle
                id={`doctor-${doctor.id}`}
                className="flex items-center gap-2 text-2xl font-bold text-gray-900"
              >
                <Stethoscope className="h-5 w-5 text-blue-600" aria-hidden="true" />
                <span>{doctor.name}</span>
              </CardTitle>
              {doctor.specialty && (
                <p className="text-sm font-medium text-gray-700">{doctor.specialty}</p>
              )}
              <p className="text-xs text-gray-500">Code: {doctor.code}</p>
            </div>

            <div className="flex gap-4 text-sm">
              <div className="flex items-center gap-1.5 rounded-lg bg-white px-3 py-2 shadow-sm">
                <Users className="h-4 w-4 text-blue-600" aria-hidden="true" />
                <span className="font-semibold text-gray-700">
                  {total_appointments}
                </span>
                <span className="text-gray-500">Total</span>
              </div>
              <div className="flex items-center gap-1.5 rounded-lg bg-white px-3 py-2 shadow-sm">
                <UserCheck className="h-4 w-4 text-green-600" aria-hidden="true" />
                <span className="font-semibold text-gray-700">
                  {checked_in_count}
                </span>
                <span className="text-gray-500">Checked In</span>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        {appointments.length === 0 ? (
          <div className="col-span-full rounded-lg border border-dashed border-gray-300 p-8 text-center">
            <p className="text-gray-500">No appointments scheduled</p>
          </div>
        ) : (
          appointments.map((appointment) => (
            <AppointmentCard
              key={appointment.appointment_id}
              appointment={appointment}
              onCheckInSuccess={onCheckInSuccess}
              onCheckInError={onCheckInError}
            />
          ))
        )}
      </div>
    </section>
  );
}
