/**
 * Type definitions for the appointment system
 * Matches the FastAPI backend contract
 */

export interface Doctor {
  id: string;
  name: string;
  code: string;
  specialty: string | null;
}

export interface Patient {
  id: string;
  name: string;
  phone: string;
  age: number | null;
  gender: string | null;
}

export interface QueueEntry {
  position: number;
  checked_in_at: string;
  status: "waiting" | "served" | "skipped";
}

export type AppointmentStatus = "booked" | "checked_in" | "cancelled" | "completed";

export interface Appointment {
  appointment_id: string;
  slot: number;
  status: AppointmentStatus;
  patient: Patient;
  queue: QueueEntry | null;
}

export interface DoctorWithAppointments {
  doctor: Doctor;
  appointments: Appointment[];
  total_appointments: number;
  checked_in_count: number;
}

export interface QueueSnapshot {
  date: string;
  total_appointments: number;
  total_doctors: number;
  doctors: DoctorWithAppointments[];
  timestamp: string;
}

export interface WebSocketMessage {
  type: "snapshot" | "update" | "pong" | "unsubscribed" | "error";
  data?: QueueSnapshot;
  message?: string;
  error?: string;
  timestamp?: string;
}

export interface CheckInRequest {
  appointment_id: string;
  patient_id: string;
}

export interface CheckInResponse {
  queue_position: number;
  checked_in_at: string;
  appointment_id: string;
}

export type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";
