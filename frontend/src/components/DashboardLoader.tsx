export function DashboardLoader() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-50">
      <div className="relative">
        {/* Outer rotating ring */}
        <div className="absolute inset-0 -m-8 animate-spin-slow">
          <div className="h-32 w-32 rounded-full border-4 border-transparent border-t-blue-400 border-r-blue-300" />
        </div>
        
        {/* Middle pulsing ring */}
        <div className="absolute inset-0 -m-4 animate-pulse">
          <div className="h-24 w-24 rounded-full border-2 border-blue-200" />
        </div>
        
        {/* Inner spinning dots */}
        <div className="relative h-16 w-16 animate-spin">
          <div className="absolute left-1/2 top-0 h-3 w-3 -translate-x-1/2 rounded-full bg-blue-600" />
          <div className="absolute right-0 top-1/2 h-3 w-3 -translate-y-1/2 rounded-full bg-blue-500" />
          <div className="absolute bottom-0 left-1/2 h-3 w-3 -translate-x-1/2 rounded-full bg-blue-400" />
          <div className="absolute left-0 top-1/2 h-3 w-3 -translate-y-1/2 rounded-full bg-blue-300" />
        </div>
        
        {/* Center icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-6 w-6 rounded-full bg-blue-600 opacity-80 animate-pulse" />
        </div>
      </div>
      
      {/* Loading text */}
      <div className="absolute mt-48">
        <div className="flex flex-col items-center gap-3">
          <p className="text-lg font-semibold text-gray-700 animate-fade-in">
            Connecting to Dashboard
          </p>
          <div className="flex gap-1">
            <span className="h-2 w-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0ms]" />
            <span className="h-2 w-2 rounded-full bg-blue-600 animate-bounce [animation-delay:150ms]" />
            <span className="h-2 w-2 rounded-full bg-blue-600 animate-bounce [animation-delay:300ms]" />
          </div>
        </div>
      </div>
    </div>
  );
}
