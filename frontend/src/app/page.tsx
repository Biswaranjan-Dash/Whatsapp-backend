import Link from "next/link";
import { CalendarCheck, Clock, Users, Zap, UserPlus, Stethoscope } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-center space-y-12 text-center">
          {/* Header */}
          <div className="space-y-6 animate-fade-in">
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-2 text-sm font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
              <Zap className="h-4 w-4" />
              Real-time Updates with WebSocket
            </div>
            
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl md:text-6xl lg:text-7xl">
              Appointment Management
              <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Made Simple
              </span>
            </h1>
            
            <p className="mx-auto max-w-2xl text-lg text-gray-600 dark:text-gray-300 sm:text-xl">
              Complete patient registration, doctor scheduling, and appointment booking system with real-time queue management.
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col gap-4 sm:flex-row sm:gap-6">
            <Link
              href="/register-patient"
              className="group inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-8 py-3.5 text-base font-semibold text-white shadow-lg transition-all hover:bg-blue-700 hover:shadow-xl hover:scale-105"
            >
              <UserPlus className="h-5 w-5" />
              Register & Book
              <span className="ml-1 transition-transform group-hover:translate-x-1">→</span>
            </Link>
            
            <Link
              href="/appointments"
              className="inline-flex items-center justify-center gap-2 rounded-lg border-2 border-gray-300 bg-white px-8 py-3.5 text-base font-semibold text-gray-700 transition-all hover:border-gray-400 hover:shadow-md dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:border-gray-500"
            >
              <CalendarCheck className="h-5 w-5" />
              View Dashboard
            </Link>

            <Link
              href="/doctor-lists"
              className="inline-flex items-center justify-center gap-2 rounded-lg border-2 border-blue-300 bg-blue-50 px-8 py-3.5 text-base font-semibold text-blue-700 transition-all hover:border-blue-400 hover:bg-blue-100 hover:shadow-md dark:border-blue-600 dark:bg-blue-900/30 dark:text-blue-300 dark:hover:border-blue-500"
            >
              <Stethoscope className="h-5 w-5" />
              Manage Doctors
            </Link>
          </div>

          {/* Features Grid */}
          <div className="mt-20 grid w-full max-w-5xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <FeatureCard
              icon={<Users className="h-6 w-6" />}
              title="Patient Registration"
              description="Quick and easy patient onboarding with complete profile management"
            />
            <FeatureCard
              icon={<CalendarCheck className="h-6 w-6" />}
              title="Smart Scheduling"
              description="Max 10 appointments per doctor per day with automatic slot allocation"
            />
            <FeatureCard
              icon={<Clock className="h-6 w-6" />}
              title="Queue Management"
              description="Real-time check-in queue with automatic position assignment"
            />
            <FeatureCard
              icon={<Zap className="h-6 w-6" />}
              title="Live Updates"
              description="WebSocket integration for instant appointment status changes"
            />
          </div>

          {/* Stats Section */}
          <div className="mt-16 grid w-full max-w-4xl gap-8 sm:grid-cols-3">
            <StatCard number="10" label="Appointments/Day/Doctor" />
            <StatCard number="Real-time" label="WebSocket Updates" />
            <StatCard number="100%" label="Concurrency Safe" />
          </div>
        </div>
      </main>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:shadow-lg hover:border-blue-200 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-blue-800">
      <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100 text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white dark:bg-blue-900/30 dark:text-blue-400">
        {icon}
      </div>
      <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
      <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
    </div>
  );
}

function StatCard({ number, label }: { number: string; label: string }) {
  return (
    <div className="rounded-lg bg-white p-6 text-center shadow-sm dark:bg-gray-800">
      <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{number}</div>
      <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">{label}</div>
    </div>
  );
}
