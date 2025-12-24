"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { 
  Search, 
  UserPlus, 
  ChevronRight, 
  Loader2, 
  Calendar, 
  Clock,
  User,
  Phone,
  Mail,
  Hash,
  Stethoscope,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import { searchPatientByPhone, createPatient, listDoctors, bookAppointment } from "@/lib/api";
import type { Patient, Doctor } from "@/types/appointment";

type Step = "search" | "register" | "select-doctor" | "select-date" | "confirm" | "success";

export default function RegisterPatientPage() {
  const router = useRouter();
  
  // Step management
  const [currentStep, setCurrentStep] = useState<Step>("search");
  
  // Patient data
  const [searchPhone, setSearchPhone] = useState("");
  const [patient, setPatient] = useState<Patient | null>(null);
  const [patientForm, setPatientForm] = useState({
    name: "",
    phone: "",
    age: "",
    gender: "",
    email: ""
  });
  
  // Booking data
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<number | undefined>();
  const [appointmentId, setAppointmentId] = useState<string | null>(null);
  
  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search for existing patient
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    
    try {
      const result = await searchPatientByPhone(searchPhone);
      
      if (result) {
        setPatient(result);
        setCurrentStep("select-doctor");
        await loadDoctors();
      } else {
        // Patient not found, go to registration
        setPatientForm({ ...patientForm, phone: searchPhone });
        setCurrentStep("register");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setIsLoading(false);
    }
  };

  // Register new patient
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    
    try {
      const newPatient = await createPatient({
        name: patientForm.name,
        phone: patientForm.phone,
        age: patientForm.age ? parseInt(patientForm.age) : undefined,
        gender: patientForm.gender || undefined,
        email: patientForm.email || undefined
      });
      
      setPatient(newPatient);
      setCurrentStep("select-doctor");
      await loadDoctors();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  // Load available doctors
  const loadDoctors = async () => {
    try {
      const doctorList = await listDoctors();
      setDoctors(doctorList);
    } catch (err) {
      setError("Failed to load doctors");
    }
  };

  // Select doctor and move to date selection
  const handleSelectDoctor = (doctor: Doctor) => {
    setSelectedDoctor(doctor);
    setCurrentStep("select-date");
    // Set default to today
    const today = new Date().toISOString().split("T")[0];
    setSelectedDate(today);
  };

  // Book appointment
  const handleBookAppointment = async () => {
    if (!patient || !selectedDoctor || !selectedDate) return;
    
    setError(null);
    setIsLoading(true);
    
    try {
      const appointment = await bookAppointment({
        patient_id: patient.id,
        doctor_id: selectedDoctor.id,
        date: selectedDate,
        time_slot: selectedTimeSlot
      });
      
      setAppointmentId(appointment.id || appointment.appointment_id);
      setCurrentStep("success");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Booking failed");
    } finally {
      setIsLoading(false);
    }
  };

  // Reset and start over
  const handleReset = () => {
    setCurrentStep("search");
    setSearchPhone("");
    setPatient(null);
    setPatientForm({ name: "", phone: "", age: "", gender: "", email: "" });
    setSelectedDoctor(null);
    setSelectedDate("");
    setSelectedTimeSlot(undefined);
    setAppointmentId(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="border-b border-blue-100 bg-white/80 backdrop-blur-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Patient Registration & Booking</h1>
              <p className="text-sm text-gray-600">Complete patient registration and appointment booking</p>
            </div>
            <button
              onClick={() => router.push("/")}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Back to Home
            </button>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="border-b bg-white">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-center gap-2 text-sm">
            <StepIndicator
              label="Search/Register"
              active={currentStep === "search" || currentStep === "register"}
              completed={patient !== null}
            />
            <ChevronRight className="h-4 w-4 text-gray-400" />
            <StepIndicator
              label="Select Doctor"
              active={currentStep === "select-doctor"}
              completed={selectedDoctor !== null}
            />
            <ChevronRight className="h-4 w-4 text-gray-400" />
            <StepIndicator
              label="Choose Date"
              active={currentStep === "select-date"}
              completed={selectedDate !== ""}
            />
            <ChevronRight className="h-4 w-4 text-gray-400" />
            <StepIndicator
              label="Confirm"
              active={currentStep === "confirm"}
              completed={currentStep === "success"}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-2xl">
          {/* Error Message */}
          {error && (
            <div className="mb-6 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4">
              <AlertCircle className="h-5 w-5 flex-shrink-0 text-red-600" />
              <div>
                <h4 className="font-medium text-red-900">Error</h4>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Step: Search Patient */}
          {currentStep === "search" && (
            <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
              <div className="mb-6 text-center">
                <div className="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
                  <Search className="h-8 w-8 text-blue-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Search Patient</h2>
                <p className="mt-2 text-gray-600">Enter phone number to find existing patient</p>
              </div>

              <form onSubmit={handleSearch} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <input
                      type="tel"
                      value={searchPhone}
                      onChange={(e) => setSearchPhone(e.target.value)}
                      placeholder="Enter phone number"
                      className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                      required
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Searching...
                    </span>
                  ) : (
                    "Search Patient"
                  )}
                </button>
              </form>
            </div>
          )}

          {/* Step: Register New Patient */}
          {currentStep === "register" && (
            <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
              <div className="mb-6 text-center">
                <div className="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                  <UserPlus className="h-8 w-8 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Register New Patient</h2>
                <p className="mt-2 text-gray-600">Patient not found. Please complete registration</p>
              </div>

              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      value={patientForm.name}
                      onChange={(e) => setPatientForm({ ...patientForm, name: e.target.value })}
                      placeholder="Enter full name"
                      className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number *
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <input
                      type="tel"
                      value={patientForm.phone}
                      onChange={(e) => setPatientForm({ ...patientForm, phone: e.target.value })}
                      placeholder="Enter phone number"
                      className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Age
                    </label>
                    <div className="relative">
                      <Hash className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                      <input
                        type="number"
                        value={patientForm.age}
                        onChange={(e) => setPatientForm({ ...patientForm, age: e.target.value })}
                        placeholder="Age"
                        min="0"
                        max="150"
                        className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Gender
                    </label>
                    <select
                      value={patientForm.gender}
                      onChange={(e) => setPatientForm({ ...patientForm, gender: e.target.value })}
                      className="w-full rounded-lg border border-gray-300 py-3 px-4 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    >
                      <option value="">Select</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email (Optional)
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <input
                      type="email"
                      value={patientForm.email}
                      onChange={(e) => setPatientForm({ ...patientForm, email: e.target.value })}
                      placeholder="Enter email"
                      className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    />
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setCurrentStep("search")}
                    className="flex-1 rounded-lg border border-gray-300 py-3 font-semibold text-gray-700 transition-colors hover:bg-gray-50"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex-1 rounded-lg bg-blue-600 py-3 font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isLoading ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 className="h-5 w-5 animate-spin" />
                        Registering...
                      </span>
                    ) : (
                      "Register & Continue"
                    )}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Step: Select Doctor */}
          {currentStep === "select-doctor" && patient && (
            <div className="space-y-6">
              <div className="rounded-xl border border-green-200 bg-green-50 p-4">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <div>
                    <h4 className="font-medium text-green-900">Patient Found</h4>
                    <p className="text-sm text-green-700">{patient.name} - {patient.phone}</p>
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-3">
                    <Stethoscope className="h-6 w-6 text-blue-600" />
                    <h2 className="text-2xl font-bold text-gray-900">Select Doctor</h2>
                  </div>
                  <p className="text-gray-600">Choose a doctor for the appointment</p>
                </div>

                <div className="space-y-3">
                  {doctors.map((doctor) => (
                    <button
                      key={doctor.id}
                      onClick={() => handleSelectDoctor(doctor)}
                      className="w-full rounded-lg border border-gray-200 p-4 text-left transition-all hover:border-blue-500 hover:bg-blue-50"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold text-gray-900">{doctor.name}</h3>
                          <p className="text-sm text-gray-600">{doctor.specialty || "General Physician"}</p>
                          <p className="text-xs text-gray-500 mt-1">Code: {doctor.code}</p>
                        </div>
                        <ChevronRight className="h-5 w-5 text-gray-400" />
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step: Select Date & Time */}
          {currentStep === "select-date" && selectedDoctor && (
            <div className="space-y-6">
              <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
                <div className="flex items-center gap-3">
                  <Stethoscope className="h-5 w-5 text-blue-600" />
                  <div>
                    <h4 className="font-medium text-blue-900">Selected Doctor</h4>
                    <p className="text-sm text-blue-700">{selectedDoctor.name} - {selectedDoctor.specialty}</p>
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-3">
                    <Calendar className="h-6 w-6 text-blue-600" />
                    <h2 className="text-2xl font-bold text-gray-900">Select Date & Time</h2>
                  </div>
                  <p className="text-gray-600">Choose appointment date and preferred time slot</p>
                </div>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Appointment Date *
                    </label>
                    <input
                      type="date"
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                      min={new Date().toISOString().split("T")[0]}
                      className="w-full rounded-lg border border-gray-300 py-3 px-4 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Time Slot (Optional)
                    </label>
                    <div className="grid grid-cols-4 gap-2">
                      {[9, 10, 11, 12, 14, 15, 16, 17].map((hour) => (
                        <button
                          key={hour}
                          type="button"
                          onClick={() => setSelectedTimeSlot(hour)}
                          className={`rounded-lg border py-2 text-sm font-medium transition-all ${
                            selectedTimeSlot === hour
                              ? "border-blue-500 bg-blue-500 text-white"
                              : "border-gray-300 text-gray-700 hover:border-blue-300 hover:bg-blue-50"
                          }`}
                        >
                          {hour}:00
                        </button>
                      ))}
                    </div>
                    <p className="mt-2 text-xs text-gray-500">If not selected, system will auto-assign available slot</p>
                  </div>

                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={() => setCurrentStep("select-doctor")}
                      className="flex-1 rounded-lg border border-gray-300 py-3 font-semibold text-gray-700 transition-colors hover:bg-gray-50"
                    >
                      Back
                    </button>
                    <button
                      type="button"
                      onClick={handleBookAppointment}
                      disabled={isLoading || !selectedDate}
                      className="flex-1 rounded-lg bg-blue-600 py-3 font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                    >
                      {isLoading ? (
                        <span className="flex items-center justify-center gap-2">
                          <Loader2 className="h-5 w-5 animate-spin" />
                          Booking...
                        </span>
                      ) : (
                        "Book Appointment"
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step: Success */}
          {currentStep === "success" && (
            <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm text-center">
              <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-green-100">
                <CheckCircle2 className="h-10 w-10 text-green-600" />
              </div>
              
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Appointment Booked!</h2>
              <p className="text-gray-600 mb-6">Your appointment has been successfully scheduled</p>

              <div className="rounded-lg bg-gray-50 p-6 mb-6 text-left">
                <h3 className="font-semibold text-gray-900 mb-4">Appointment Details</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Patient:</span>
                    <span className="font-medium text-gray-900">{patient?.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Doctor:</span>
                    <span className="font-medium text-gray-900">{selectedDoctor?.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Date:</span>
                    <span className="font-medium text-gray-900">{selectedDate}</span>
                  </div>
                  {selectedTimeSlot && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Time Slot:</span>
                      <span className="font-medium text-gray-900">{selectedTimeSlot}:00</span>
                    </div>
                  )}
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Appointment ID:</span>
                    <span className="font-mono text-sm font-semibold text-gray-900 break-all">{appointmentId}</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleReset}
                  className="flex-1 rounded-lg border border-gray-300 py-3 font-semibold text-gray-700 transition-colors hover:bg-gray-50"
                >
                  Book Another
                </button>
                <button
                  onClick={() => router.push("/appointments")}
                  className="flex-1 rounded-lg bg-blue-600 py-3 font-semibold text-white transition-colors hover:bg-blue-700"
                >
                  View Dashboard
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function StepIndicator({ label, active, completed }: { label: string; active: boolean; completed: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium ${
          completed
            ? "bg-green-500 text-white"
            : active
            ? "bg-blue-600 text-white"
            : "bg-gray-200 text-gray-600"
        }`}
      >
        {completed ? <CheckCircle2 className="h-4 w-4" /> : null}
      </div>
      <span
        className={`text-sm font-medium ${
          active ? "text-gray-900" : "text-gray-500"
        }`}
      >
        {label}
      </span>
    </div>
  );
}
