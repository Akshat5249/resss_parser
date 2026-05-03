"use client";

import React, { useState, useEffect, useRef } from "react";
import { Upload, X, FileText, Loader2, Plus, CheckCircle2, Clock } from "lucide-react";
import { resumeApi } from "@/lib/api";
import { toast } from "react-hot-toast";

interface ResumeItem {
  id: string;
  name: string;
  status: "pending" | "processing" | "done" | "failed";
}

interface RankUploaderProps {
  onResumesReady: (ids: string[]) => void;
}

export default function RankUploader({ onResumesReady }: RankUploaderProps) {
  const [resumes, setResumes] = useState<ResumeItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const pollIntervals = useRef<Record<string, NodeJS.Timeout>>({});

  const startPolling = (jobId: string) => {
    if (pollIntervals.current[jobId]) return;

    const poll = async () => {
      try {
        const result = await resumeApi.getStatus(jobId);
        
        setResumes(prev => prev.map(r => 
          r.id === jobId ? { ...r, status: result.status } : r
        ));

        if (result.status === "done" || result.status === "failed") {
          clearInterval(pollIntervals.current[jobId]);
          delete pollIntervals.current[jobId];
        }
      } catch (err) {
        console.error("Polling error for", jobId, err);
      }
    };

    poll();
    pollIntervals.current[jobId] = setInterval(poll, 3000);
  };

  useEffect(() => {
    // Notify parent of ready resumes (only those with 'done' status)
    const readyIds = resumes.filter(r => r.status === "done").map(r => r.id);
    onResumesReady(readyIds);
  }, [resumes, onResumesReady]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      Object.values(pollIntervals.current).forEach(clearInterval);
    };
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    setIsUploading(true);

    for (const file of files) {
      try {
        const res = await resumeApi.upload(file);
        const newResume: ResumeItem = { 
          id: res.job_id, 
          name: file.name, 
          status: "pending" 
        };
        setResumes(prev => [...prev, newResume]);
        startPolling(res.job_id);
      } catch (err) {
        toast.error(`Failed to upload ${file.name}`);
      }
    }

    setIsUploading(false);
  };

  const removeResume = (id: string) => {
    if (pollIntervals.current[id]) {
      clearInterval(pollIntervals.current[id]);
      delete pollIntervals.current[id];
    }
    setResumes(prev => prev.filter(r => r.id !== id));
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {resumes.map((res) => (
          <div key={res.id} className={`flex items-center justify-between p-4 bg-white border rounded-xl shadow-sm transition-all ${res.status === 'done' ? 'border-[#10B981] bg-[#F0FDF4]' : 'border-[#E2E8F0]'}`}>
            <div className="flex items-center space-x-3 overflow-hidden">
              <div className={`p-2 rounded-lg shrink-0 ${res.status === 'done' ? 'bg-[#DCFCE7]' : 'bg-[#F1F5F9]'}`}>
                <FileText className={`w-4 h-4 ${res.status === 'done' ? 'text-[#10B981]' : 'text-[#64748B]'}`} />
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-bold text-[#111827] truncate">{res.name}</p>
                <div className="flex items-center space-x-1.5 mt-0.5">
                  {res.status === 'done' ? (
                    <span className="text-[9px] font-bold text-[#10B981] uppercase flex items-center">
                      <CheckCircle2 className="w-2.5 h-2.5 mr-1" /> Ready
                    </span>
                  ) : res.status === 'failed' ? (
                    <span className="text-[9px] font-bold text-[#EF4444] uppercase">Failed</span>
                  ) : (
                    <span className="text-[9px] font-bold text-[#6B7280] uppercase flex items-center animate-pulse">
                      <Clock className="w-2.5 h-2.5 mr-1" /> Processing...
                    </span>
                  )}
                </div>
              </div>
            </div>
            <button 
              onClick={() => removeResume(res.id)}
              className="p-1.5 hover:bg-[#FEE2E2] hover:text-[#EF4444] rounded-md transition-colors text-[#94A3B8]"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
        
        <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-[#E2E8F0] rounded-xl hover:border-[#4F46E5] hover:bg-[#EEF2FF]/50 transition-all cursor-pointer bg-white group min-h-[72px]">
          <div className="flex items-center space-x-2 text-[#64748B] group-hover:text-[#4F46E5]">
            {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            <span className="text-xs font-bold uppercase tracking-widest">Add Resumes</span>
          </div>
          <input 
            type="file" 
            className="hidden" 
            multiple 
            onChange={handleFileChange} 
            accept=".pdf,.docx"
          />
        </label>
      </div>

      <div className="flex justify-between items-center text-[10px] text-[#94A3B8] font-bold uppercase tracking-widest">
        <span>{resumes.filter(r => r.status === 'done').length} of {resumes.length} ready</span>
        <span>Min: 2 ready required</span>
      </div>
    </div>
  );
}
