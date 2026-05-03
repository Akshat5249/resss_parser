import React from "react";
import { AlertTriangle, CheckCircle2, History, Target } from "lucide-react";
import { Gaps } from "@/lib/types";

interface GapAnalysisProps {
  gaps: Gaps;
}

export default function GapAnalysis({ gaps }: GapAnalysisProps) {
  const getSeverityColor = (sev: string) => {
    if (sev === "high") return "bg-[#EF4444]";
    if (sev === "medium") return "bg-[#F59E0B]";
    return "bg-[#10B981]";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-[#1E293B]">Gap Analysis</h3>
        <div className={`px-3 py-1 rounded-full text-white text-xs font-bold uppercase tracking-wider ${getSeverityColor(gaps.overall_gap_severity)}`}>
          {gaps.overall_gap_severity} SEVERITY Gap
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Experience Gap */}
        <div className={`p-6 rounded-xl border-2 ${gaps.experience_gap.has_gap ? "border-[#F59E0B] bg-[#FFFBEB]" : "border-[#10B981] bg-[#F0FDF4]"}`}>
          <div className="flex items-center space-x-3 mb-3">
            <History className={`w-5 h-5 ${gaps.experience_gap.has_gap ? "text-[#F59E0B]" : "text-[#10B981]"}`} />
            <h4 className="font-bold">Experience Fit</h4>
          </div>
          {gaps.experience_gap.has_gap ? (
            <div className="space-y-2">
              <p className="text-sm text-[#92400E]">
                You have <b>{Math.round(gaps.experience_gap.resume_months / 12)} years</b> of experience, but this role typically requires <b>{Math.round(gaps.experience_gap.required_months / 12)} years</b>.
              </p>
              <p className="text-xs text-[#B45309]">Gap: {gaps.experience_gap.gap_months} months</p>
            </div>
          ) : (
            <p className="text-sm text-[#065F46]">Your experience matches or exceeds the job requirements. Great job!</p>
          )}
        </div>

        {/* Project Relevance */}
        <div className="p-6 rounded-xl border-2 border-[#4F46E5] bg-[#EEF2FF]">
          <div className="flex items-center space-x-3 mb-3">
            <Target className="w-5 h-5 text-[#4F46E5]" />
            <h4 className="font-bold">Project Relevance</h4>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-end">
              <span className="text-xs font-medium text-[#4338CA]">Alignment Score</span>
              <span className="text-sm font-bold text-[#1E293B]">{gaps.project_relevance_score}%</span>
            </div>
            <div className="h-1.5 w-full bg-[#E0E7FF] rounded-full overflow-hidden">
              <div className="h-full bg-[#4F46E5]" style={{ width: `${gaps.project_relevance_score}%` }} />
            </div>
            <p className="text-[10px] text-[#6366F1] mt-2 italic">How well your projects align with JD requirements.</p>
          </div>
        </div>
      </div>

      {/* Weak Bullets */}
      <div className="bg-white rounded-xl border border-[#E2E8F0] p-6 shadow-sm">
        <div className="flex items-center space-x-3 mb-4 text-[#F59E0B]">
          <AlertTriangle className="w-5 h-5" />
          <h4 className="font-bold">Improvement Areas in Content</h4>
        </div>
        
        {gaps.weak_bullets.length > 0 ? (
          <div className="space-y-4">
            {gaps.weak_bullets.map((wb, idx) => (
              <div key={idx} className="border-l-4 border-[#F59E0B] pl-4 py-1">
                <p className="text-xs font-bold text-[#64748B] mb-1">{wb.company} — {wb.role}</p>
                <p className="text-sm text-[#1E293B] italic mb-2">"{wb.bullet}"</p>
                <div className="flex flex-wrap gap-2">
                  {wb.issues.map(issue => (
                    <span key={issue} className="text-[10px] bg-[#FFFBEB] text-[#B45309] border border-[#FDE68A] px-2 py-0.5 rounded uppercase font-bold">
                      {issue}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center space-x-2 text-[#10B981]">
            <CheckCircle2 className="w-4 h-4" />
            <p className="text-sm">All resume bullets are strong and impactful!</p>
          </div>
        )}
      </div>
    </div>
  );
}
