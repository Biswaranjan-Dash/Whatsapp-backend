import type { ConnectionStatus } from "@/types/appointment";
import { cn } from "@/lib/utils";

interface ConnectionStatusIndicatorProps {
  status: ConnectionStatus;
  onRetry?: () => void;
}

export function ConnectionStatusIndicator({
  status,
  onRetry,
}: ConnectionStatusIndicatorProps) {
  const statusConfig = {
    connecting: {
      label: "Connecting...",
      color: "bg-yellow-500",
      textColor: "text-yellow-700",
      bgColor: "bg-yellow-50",
      borderColor: "border-yellow-200",
    },
    connected: {
      label: "Connected",
      color: "bg-green-500",
      textColor: "text-green-700",
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
    },
    disconnected: {
      label: "Disconnected",
      color: "bg-gray-500",
      textColor: "text-gray-700",
      bgColor: "bg-gray-50",
      borderColor: "border-gray-200",
    },
    error: {
      label: "Connection Error",
      color: "bg-red-500",
      textColor: "text-red-700",
      bgColor: "bg-red-50",
      borderColor: "border-red-200",
    },
  };

  const config = statusConfig[status];

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-lg border px-3 py-2 text-sm",
        config.bgColor,
        config.borderColor
      )}
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-2">
        <div
          className={cn(
            "h-2 w-2 rounded-full",
            config.color,
            status === "connecting" && "animate-pulse"
          )}
          aria-hidden="true"
        />
        <span className={cn("font-medium", config.textColor)}>
          {config.label}
        </span>
      </div>
      {(status === "disconnected" || status === "error") && onRetry && (
        <button
          onClick={onRetry}
          className={cn(
            "ml-2 text-xs underline hover:no-underline",
            config.textColor
          )}
          aria-label="Retry connection"
        >
          Retry
        </button>
      )}
    </div>
  );
}
