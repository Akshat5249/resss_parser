import { useState, useEffect, useRef } from "react";
import { StatusResponse } from "../lib/types";

interface UsePollingOptions {
  jobId: string | null;
  pollFn: (jobId: string) => Promise<StatusResponse>;
  onComplete: (jobId: string) => void;
  onError: (message: string) => void;
  interval?: number;
}

export function usePolling({
  jobId, 
  pollFn, 
  onComplete, 
  onError, 
  interval = 2000
}: UsePollingOptions) {
  const [status, setStatus] = useState<string>("idle");
  const [message, setMessage] = useState<string>("");
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!jobId) {
      setStatus("idle");
      setMessage("");
      return;
    }

    const poll = async () => {
      try {
        const result = await pollFn(jobId);
        setStatus(result.status);
        setMessage(result.message);

        if (result.status === "done") {
          if (timerRef.current) clearInterval(timerRef.current);
          onComplete(jobId);
        } else if (result.status === "failed") {
          if (timerRef.current) clearInterval(timerRef.current);
          onError(result.message);
        }
      } catch (err) {
        console.error("Polling error:", err);
        onError("Connection error with server");
        if (timerRef.current) clearInterval(timerRef.current);
      }
    };

    // Initial poll
    poll();
    
    // Set up interval
    timerRef.current = setInterval(poll, interval);
    
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [jobId, pollFn, onComplete, onError, interval]);

  return { status, message };
}
