import { useEffect, useRef } from "react";
import { toast } from "sonner";
import { useGetReminders } from "../../hooks/useQueries";

export default function ReminderMonitor() {
  const { data: reminders = [] } = useGetReminders();
  const triggeredRef = useRef<Set<string>>(new Set());

  // Check reminders every minute
  useEffect(() => {
    const check = () => {
      for (const r of reminders) {
        const key = r.id.toString();
        
        // Skip if already triggered in this session
        if (triggeredRef.current.has(key)) continue;

        // Skip if already triggered in the backend/data
        if (r.isTriggered) {
          triggeredRef.current.add(key);
          continue;
        }

        // Convert the BigInt timestamp (nanoseconds) back to milliseconds for comparison
        const ms = Number(r.dateTime) / 1_000_000;
        
        if (ms <= Date.now()) {
          triggeredRef.current.add(key);
          
          // Browser Notification
          if ("Notification" in window && Notification.permission === "granted") {
            new Notification(`⏰ ${r.title}`, {
              body: r.isBirthday ? "🎂 Birthday reminder!" : "FocusFlow Reminder",
            });
          }
          
          // Toast Notification (always show in-app)
          toast(`⏰ ${r.title}`, {
            description: r.isBirthday ? "🎂 Birthday!" : "Reminder triggered",
            duration: 10000,
          });
          
          console.log(`Reminder triggered: ${r.title}`);
        }
      }
    };

    check();
    const interval = setInterval(check, 30_000); // Check every 30 seconds for better responsiveness
    return () => clearInterval(interval);
  }, [reminders]);

  // Request notification permission once on mount
  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
  }, []);

  return null; // This component has no UI
}
