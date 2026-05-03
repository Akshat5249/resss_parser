import React from "react";
import { GraduationCap, ExternalLink, Clock } from "lucide-react";
import { LearningPath as LearningPathType } from "@/lib/types";

interface LearningPathProps {
  path: LearningPathType | null;
}

export default function LearningPath({ path }: LearningPathProps) {
  if (!path || path.priority_skills.length === 0) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2">
        <GraduationCap className="w-6 h-6 text-[#4F46E5]" />
        <h3 className="text-lg font-bold text-[#1E293B]">Your Learning Roadmap</h3>
      </div>

      <div className="bg-[#EEF2FF] p-6 rounded-xl border border-[#C7D2FE]">
        <p className="text-sm text-[#4338CA] italic leading-relaxed mb-4">
          "{path.summary}"
        </p>
        <div className="flex items-center space-x-4 text-xs font-bold text-[#6366F1] uppercase">
          <div className="flex items-center">
            <Clock className="w-3.5 h-3.5 mr-1.5" />
            <span>{path.total_estimated_weeks} Weeks total</span>
          </div>
          <span>•</span>
          <span>{path.priority_skills.length} Priority Skills</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {path.priority_skills.map((skill, idx) => (
          <div key={idx} className="bg-white p-5 rounded-xl border border-[#E2E8F0] shadow-sm flex flex-col h-full">
            <div className="flex justify-between items-start mb-4">
              <h4 className="font-bold text-[#1E293B]">{skill.skill}</h4>
              <span className={`text-[9px] px-2 py-0.5 rounded font-bold uppercase ${
                skill.level === 'beginner' ? 'bg-[#DCFCE7] text-[#10B981]' : 
                skill.level === 'intermediate' ? 'bg-[#E0F2FE] text-[#0EA5E9]' : 'bg-[#FEE2E2] text-[#EF4444]'
              }`}>
                {skill.level}
              </span>
            </div>
            
            <div className="space-y-3 flex-1">
              <p className="text-[10px] text-[#64748B] font-bold uppercase tracking-wider">Top Resources</p>
              {skill.resources.map((res, ridx) => (
                <a 
                  key={ridx}
                  href={res.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-start group border-b border-[#F1F5F9] pb-2 last:border-0"
                >
                  <div className="flex-1">
                    <p className="text-xs font-bold text-[#1E293B] group-hover:text-[#4F46E5] transition-colors">{res.name}</p>
                    <p className="text-[10px] text-[#94A3B8]">{res.platform} • {res.type}</p>
                  </div>
                  <ExternalLink className="w-3 h-3 text-[#94A3B8] mt-1 group-hover:text-[#4F46E5]" />
                </a>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t border-[#F1F5F9] text-center">
              <span className="text-[10px] font-bold text-[#64748B] uppercase italic">
                ~ {skill.estimated_weeks} weeks to master
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
