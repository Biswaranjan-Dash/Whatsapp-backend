"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Stethoscope,
  Calendar,
  Check,
  X,
  Loader2,
  AlertCircle,
  CheckCircle2,
  ArrowUpDown,
  CalendarClock,
  Home,
} from "lucide-react";
import { listDoctors, setDoctorAvailability, getDoctorAvailability } from "@/lib/api";
import type { Doctor } from "@/types/appointment";

interface DoctorWithAvailability extends Doctor {
  isAvailable?: boolean;
  availabilityNotes?: string;
  isLoading?: boolean;
}

export default function DoctorListsPage() {
  const router = useRouter();

  // State
  const [doctors, setDoctors] = useState<DoctorWithAvailability[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    return new Date().toISOString().split("T")[0];
  });
  const [sortField, setSortField] = useState<"name" | "specialty" | "code">("name");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Load doctors
  useEffect(() => {
    loadDoctors();
  }, []);

  // Load availability when date changes
  useEffect(() => {
    if (doctors.length > 0) {
      loadAvailability();
    }
  }, [selectedDate]);

  const loadDoctors = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listDoctors();
      setDoctors(data.map((d) => ({ ...d, isAvailable: true })));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load doctors");
    } finally {
      setIsLoading(false);
    }
  };

  const loadAvailability = async () => {
    try {
      const updatedDoctors = await Promise.all(
        doctors.map(async (doctor) => {
          try {
            const availability = await getDoctorAvailability(doctor.id, selectedDate);
            return {
              ...doctor,
              isAvailable: availability.is_present,
              availabilityNotes: availability.notes || undefined,
            };
          } catch (err) {
            // Default to available if no record
            return { ...doctor, isAvailable: true, availabilityNotes: undefined };
          }
        })
      );
      setDoctors(updatedDoctors);
    } catch (err) {
      console.error("Failed to load availability:", err);
    }
  };

  const toggleAvailability = async (doctorId: string, currentStatus: boolean) => {
    const newStatus = !currentStatus;
    const doctorName = doctors.find((d) => d.id === doctorId)?.name;

    // Optimistic update
    setDoctors((prev) =>
      prev.map((d) =>
        d.id === doctorId ? { ...d, isAvailable: newStatus, isLoading: true } : d
      )
    );

    try {
      await setDoctorAvailability(
        doctorId,
        selectedDate,
        newStatus,
        newStatus ? "Available" : "Unavailable"
      );

      setSuccessMessage(
        `${doctorName} marked as ${newStatus ? "available" : "unavailable"} for ${selectedDate}`
      );
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      // Rollback on error
      setDoctors((prev) =>
        prev.map((d) => (d.id === doctorId ? { ...d, isAvailable: currentStatus } : d))
      );
      setError(err instanceof Error ? err.message : "Failed to update availability");
      setTimeout(() => setError(null), 5000);
    } finally {
      setDoctors((prev) =>
        prev.map((d) => (d.id === doctorId ? { ...d, isLoading: false } : d))
      );
    }
  };

  // Filtered and sorted doctors
  const filteredDoctors = useMemo(() => {
    let filtered = doctors.filter(
      (doctor) =>
        doctor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doctor.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (doctor.specialty &&
          doctor.specialty.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    filtered.sort((a, b) => {
      let aValue = a[sortField] || "";
      let bValue = b[sortField] || "";

      if (typeof aValue === "string") {
        aValue = aValue.toLowerCase();
        bValue = (bValue as string).toLowerCase();
      }

      if (sortDirection === "asc") {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return filtered;
  }, [doctors, searchQuery, sortField, sortDirection]);

  const toggleSort = (field: "name" | "specialty" | "code") => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const availableCount = filteredDoctors.filter((d) => d.isAvailable).length;
  const unavailableCount = filteredDoctors.length - availableCount;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="border-b border-blue-100 bg-white/80 backdrop-blur-md sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Stethoscope className="h-6 w-6 text-blue-600" />
                Doctor Management
              </h1>
              <p className="text-sm text-gray-600">
                Manage doctor availability and schedules
              </p>
            </div>
            <button
              onClick={() => router.push("/")}
              className="inline-flex items-center gap-2 rounded-lg border border-blue-200 bg-white px-3 py-2 text-sm font-medium text-blue-600 shadow-sm hover:bg-blue-50 hover:border-blue-300 transition-colors"
            >
              <Home className="h-4 w-4" />
              Home
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Notifications */}
        {error && (
          <div className="mb-6 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 animate-in slide-in-from-top-2">
            <AlertCircle className="h-5 w-5 flex-shrink-0 text-red-600" />
            <div className="flex-1">
              <h4 className="font-medium text-red-900">Error</h4>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 flex items-start gap-3 rounded-lg border border-green-200 bg-green-50 p-4 animate-in slide-in-from-top-2">
            <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-green-600" />
            <div className="flex-1">
              <h4 className="font-medium text-green-900">Success</h4>
              <p className="text-sm text-green-700">{successMessage}</p>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search doctors by name, code, or specialty..."
              className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            />
          </div>

          {/* Date Selector */}
          <div className="flex items-center gap-2 rounded-lg border border-blue-200 bg-white px-4 py-2 shadow-sm">
            <Calendar className="h-4 w-4 text-blue-600" />
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="border-none bg-transparent text-sm font-medium text-gray-900 outline-none"
            />
          </div>
        </div>

        {/* Stats */}
        <div className="mb-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
                <Stethoscope className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{filteredDoctors.length}</p>
                <p className="text-sm text-gray-600">Total Doctors</p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100">
                <Check className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{availableCount}</p>
                <p className="text-sm text-gray-600">Available Today</p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100">
                <X className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{unavailableCount}</p>
                <p className="text-sm text-gray-600">Unavailable</p>
              </div>
            </div>
          </div>
        </div>

        {/* Doctors Table */}
        {isLoading ? (
          <div className="flex items-center justify-center rounded-lg border border-gray-200 bg-white p-12">
            <div className="text-center">
              <Loader2 className="mx-auto h-8 w-8 animate-spin text-blue-600" />
              <p className="mt-2 text-sm text-gray-600">Loading doctors...</p>
            </div>
          </div>
        ) : filteredDoctors.length === 0 ? (
          <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
            <Stethoscope className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">No doctors found</h3>
            <p className="mt-2 text-sm text-gray-600">
              {searchQuery
                ? "Try adjusting your search query"
                : "No doctors have been added to the system yet"}
            </p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => toggleSort("name")}
                    >
                      <div className="flex items-center gap-2">
                        Doctor Name
                        <ArrowUpDown className="h-3.5 w-3.5" />
                      </div>
                    </th>
                    <th
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => toggleSort("specialty")}
                    >
                      <div className="flex items-center gap-2">
                        Specialty
                        <ArrowUpDown className="h-3.5 w-3.5" />
                      </div>
                    </th>
                    <th
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => toggleSort("code")}
                    >
                      <div className="flex items-center gap-2">
                        Code
                        <ArrowUpDown className="h-3.5 w-3.5" />
                      </div>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Availability Status
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredDoctors.map((doctor) => (
                    <tr
                      key={doctor.id}
                      className="transition-colors hover:bg-gray-50"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
                            <Stethoscope className="h-5 w-5 text-blue-600" />
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-900">
                              {doctor.name}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <p className="text-sm text-gray-900">
                          {doctor.specialty || "General Physician"}
                        </p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <code className="rounded bg-gray-100 px-2 py-1 text-xs font-mono text-gray-700">
                          {doctor.code}
                        </code>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          {doctor.isAvailable ? (
                            <>
                              <div className="flex h-2 w-2 rounded-full bg-green-500" />
                              <span className="text-sm font-medium text-green-700">
                                Available
                              </span>
                            </>
                          ) : (
                            <>
                              <div className="flex h-2 w-2 rounded-full bg-red-500" />
                              <span className="text-sm font-medium text-red-700">
                                Unavailable
                              </span>
                            </>
                          )}
                        </div>
                        {doctor.availabilityNotes && (
                          <p className="mt-1 text-xs text-gray-500">
                            {doctor.availabilityNotes}
                          </p>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <button
                          onClick={() =>
                            toggleAvailability(doctor.id, doctor.isAvailable || false)
                          }
                          disabled={doctor.isLoading}
                          className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                            doctor.isAvailable
                              ? "bg-red-100 text-red-700 hover:bg-red-200"
                              : "bg-green-100 text-green-700 hover:bg-green-200"
                          } disabled:opacity-50`}
                        >
                          {doctor.isLoading ? (
                            <>
                              <Loader2 className="h-4 w-4 animate-spin" />
                              Updating...
                            </>
                          ) : doctor.isAvailable ? (
                            <>
                              <X className="h-4 w-4" />
                              Mark Unavailable
                            </>
                          ) : (
                            <>
                              <Check className="h-4 w-4" />
                              Mark Available
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
