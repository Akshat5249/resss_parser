import React from "react";
import { CheckCircle2, XCircle, Star } from "lucide-react";
import SkillBadge from "../ui/SkillBadge";
import { MatchedSkills } from "@/lib/types";

interface SkillsAnalysisProps {
  skills: MatchedSkills;
}

export default function SkillsAnalysis({ skills }: SkillsAnalysisProps) {
  const reqMatched = skills.required_matched ?? [];
  const reqMissing = skills.required_missing ?? [];
  const prefMatched = skills.preferred_matched ?? [];
  const prefMissing = skills.preferred_missing ?? [];
  
  return (
    <div className="space-y-12">
      {/* Required Skills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* Matched */}
        <div className="space-y-6">
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center space-x-2 bg-[#ECFDF5] px-3 py-1.5 rounded-full border border-[#6EE7B7]">
              <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
              <span className="text-[11px] font-bold text-[#059669] uppercase tracking-wider">✓ You Have These</span>
            </div>
            <span className="text-[10px] font-bold text-[#6B7280]">{reqMatched.length} Matched</span>
          </div>
          
          <div className="bg-white min-h-[160px] rounded-3xl border border-[#E5E7EB] p-8 shadow-sm flex flex-wrap gap-3 items-start content-start transition-all hover:shadow-md">
            {reqMatched.length > 0 ? (
              reqMatched.map(s => <SkillBadge key={s} skill={s} variant="matched" />)
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <p className="text-sm text-[#94A3B8] italic">No required skills matched yet.</p>
              </div>
            )}
          </div>
        </div>

        {/* Missing */}
        <div className="space-y-6">
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center space-x-2 bg-[#FEF2F2] px-3 py-1.5 rounded-full border border-[#FECACA]">
              <XCircle className="w-4 h-4 text-[#DC2626]" />
              <span className="text-[11px] font-bold text-[#DC2626] uppercase tracking-wider">✗ You're Missing These</span>
            </div>
            <span className="text-[10px] font-bold text-[#6B7280]">{reqMissing.length} Gaps</span>
          </div>
          
          <div className="bg-white min-h-[160px] rounded-3xl border border-[#E5E7EB] p-8 shadow-sm flex flex-wrap gap-3 items-start content-start transition-all hover:shadow-md">
            {reqMissing.length > 0 ? (
              reqMissing.map(s => <SkillBadge key={s} skill={s} variant="missing" />)
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-[#F0FDF4] rounded-2xl">
                <p className="text-sm text-[#059669] font-medium">✓ You have all required skills!</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Preferred Skills */}
      <div className="bg-white rounded-3xl border border-[#E5E7EB] p-10 shadow-sm relative overflow-hidden group hover:shadow-md transition-all">
        <div className="absolute top-0 right-0 w-32 h-32 bg-[#EEF2FF] rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-110 opacity-30"></div>
        
        <div className="relative z-10 space-y-8">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-[#EEF2FF] rounded-xl flex items-center justify-center">
              <Star className="w-5 h-5 text-[#4F46E5] fill-current" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-[#111827]">Preferred & Bonus Qualifications</h3>
              <p className="text-xs text-[#6B7280]">These aren't mandatory but will give you a significant advantage.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 pt-4">
            <div className="space-y-4">
              <p className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest px-1">Bonus skills you possess</p>
              <div className="flex flex-wrap gap-2">
                {prefMatched.length > 0 ? (
                  prefMatched.map(s => <SkillBadge key={s} skill={s} variant="preferred" />)
                ) : (
                  <p className="text-xs text-[#94A3B8] italic pl-1">None identified in your resume.</p>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <p className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest px-1">Nice-to-haves to consider</p>
              <div className="flex flex-wrap gap-2">
                {prefMissing.length > 0 ? (
                  prefMissing.map(s => <SkillBadge key={s} skill={s} variant="neutral" />)
                ) : (
                  <p className="text-xs text-[#94A3B8] italic pl-1">No additional preferred skills missing.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
