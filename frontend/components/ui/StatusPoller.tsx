"use client";

import React from "react";
import { usePolling } from "@/hooks/usePolling";
import { StatusResponse } from "@/lib/types";
import LoadingSpinner from "./LoadingSpinner";

interface StatusPollerProps {
  jobId: string | null;
  pollFn: (id: string) => Promise<StatusResponse>;
  onComplete: (id: string) => void;
  onError: (msg: string) => void;
}

export default function StatusPoller({ 
  jobId, 
  pollFn, 
  onComplete, 
  onError 
}: StatusPollerProps) {
  const { status, message } = usePolling({ jobId, pollFn, onComplete, onError });

  if (status === "idle" || !jobId) return null;

  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4 bg-white rounded-2xl border border-[#E2E8F0] shadow-sm">
      <LoadingSpinner size="lg" />
      <div className="text-center">
        <p className="text-sm font-bold text-[#1E293B] uppercase tracking-widest">{status}</p>
        <p className="text-sm text-[#64748B] mt-1">{message}</p>
      </div>
      <div className="w-full max-w-xs h-1 bg-[#F1F5F9] rounded-full overflow-hidden">
        <div className="h-full bg-[#4F46E5] animate-progress-indefinite" style={{ width: '40%' }}></div>
      </div>
    </div>
  );
}
