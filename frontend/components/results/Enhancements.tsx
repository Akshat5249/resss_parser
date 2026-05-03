import React, { useState } from "react";
import { Sparkles, Copy, Check, ArrowRight } from "lucide-react";
import { Enhancement } from "@/lib/types";
import { toast } from "react-hot-toast";

interface EnhancementsProps {
  enhancements: Enhancement[] | null;
}

export default function Enhancements({ enhancements }: EnhancementsProps) {
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  if (!enhancements || enhancements.length === 0) return null;

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    toast.success("Copied to clipboard!");
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2">
        <Sparkles className="w-6 h-6 text-[#4F46E5]" />
        <h3 className="text-lg font-bold text-[#1E293B]">AI-Suggested Improvements</h3>
      </div>
      
      <div className="space-y-8">
        {enhancements.map((enh, idx) => (
          <div key={idx} className="bg-white rounded-xl border border-[#E2E8F0] overflow-hidden shadow-sm">
            <div className="bg-[#F8FAFC] px-6 py-3 border-b border-[#E2E8F0] flex justify-between items-center">
              <span className="text-xs font-bold text-[#64748B] uppercase tracking-wider">
                {enh.company} — {enh.role}
              </span>
              <div className="flex gap-1">
                {enh.issues.map(issue => (
                  <span key={issue} className="text-[9px] bg-white text-[#64748B] border border-[#E2E8F0] px-1.5 py-0.5 rounded">
                    {issue}
                  </span>
                ))}
              </div>
            </div>

            <div className="p-6 grid grid-cols-1 md:grid-cols-[1fr,40px,1fr] gap-4 items-center">
              {/* Original */}
              <div className="bg-[#FEE2E2]/30 p-4 rounded-lg border border-[#FEE2E2]">
                <p className="text-[10px] font-bold text-[#EF4444] uppercase mb-2">Original</p>
                <p className="text-sm text-[#1E293B] italic leading-relaxed">"{enh.original}"</p>
              </div>

              {/* Arrow */}
              <div className="flex justify-center">
                <ArrowRight className="w-6 h-6 text-[#94A3B8] rotate-90 md:rotate-0" />
              </div>

              {/* Enhanced */}
              <div className="bg-[#DCFCE7]/30 p-4 rounded-lg border border-[#BBF7D0] relative group">
                <p className="text-[10px] font-bold text-[#10B981] uppercase mb-2">Enhanced</p>
                <p className="text-sm text-[#1E293B] font-medium leading-relaxed italic">"{enh.enhanced}"</p>
                
                <button 
                  onClick={() => handleCopy(enh.enhanced, idx)}
                  className="absolute top-3 right-3 p-1.5 bg-white border border-[#E2E8F0] rounded-md shadow-sm opacity-0 group-hover:opacity-100 transition-opacity hover:bg-[#F8FAFC]"
                >
                  {copiedIdx === idx ? <Check className="w-3.5 h-3.5 text-[#10B981]" /> : <Copy className="w-3.5 h-3.5 text-[#64748B]" />}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
