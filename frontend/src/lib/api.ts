import type { CheckInRequest, CheckInResponse, Patient, Doctor, Appointment } from "@/types/appointment";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// Patient API
export async function searchPatientByPhone(phone: string): Promise<Patient | null> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/patients/search?phone=${encodeURIComponent(phone)}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.message || errorData.detail?.message || "Search failed",
      response.status,
      errorData
    );
  }

  const data = await response.json();
  return data || null;
}

export async function createPatient(patientData: {
  name: string;
  phone: string;
  age?: number;
  gender?: string;
  email?: string;
}): Promise<Patient> {
  const response = await fetch(`${API_BASE_URL}/api/v1/patients`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(patientData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.message || errorData.detail?.message || "Failed to create patient",
      response.status,
      errorData
    );
  }

  return response.json();
}

// Doctor API
export async function listDoctors(): Promise<Doctor[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/doctors`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.message || errorData.detail?.message || "Failed to fetch doctors",
      response.status,
      errorData
    );
  }

  return response.json();
}

export async function setDoctorAvailability(
  doctorId: string,
  date: string,
  isPresent: boolean,
  notes?: string
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/doctors/${doctorId}/availability`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        date,
        is_present: isPresent,
        notes: notes || null,
      }),
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.message || errorData.detail?.message || "Failed to update availability",
      response.status,
      errorData
    );
  }
}

export async function getDoctorAvailability(
  doctorId: string,
  date: string
): Promise<{ is_present: boolean; notes?: string }> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/doctors/${doctorId}/availability?date=${date}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.message || errorData.detail?.message || "Failed to fetch availability",
      response.status,
      errorData
    );
  }

  return response.json();
}

// Appointment API
export async function bookAppointment(appointmentData: {
  patient_id: string;
  doctor_id: string;
  date: string;
  time_slot?: number;
}): Promise<Appointment> {
  const response = await fetch(`${API_BASE_URL}/api/v1/appointments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(appointmentData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.message || errorData.detail?.message || "Failed to book appointment",
      response.status,
      errorData
    );
  }

  return response.json();
}

// Check-in API
export async function checkInPatient(
  appointmentId: string,
  patientId: string
): Promise<CheckInResponse> {
  const payload: CheckInRequest = {
    appointment_id: appointmentId,
    patient_id: patientId,
  };

  console.log('Check-in payload:', payload); // Debug log

  const response = await fetch(`${API_BASE_URL}/api/v1/checkins`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.message || errorData.detail?.message || "Check-in failed",
      response.status,
      errorData
    );
  }

  return response.json();
}
