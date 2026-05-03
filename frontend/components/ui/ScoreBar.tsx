import React from "react";

interface ScoreBarProps {
  label: string;
  score: number;
  weight?: number;
}

export default function ScoreBar({ label, score, weight }: ScoreBarProps) {
  const getColorClass = (s: number) => {
    if (s >= 80) return "bg-[#10B981]";
    if (s >= 60) return "bg-[#4F46E5]";
    if (s >= 40) return "bg-[#F59E0B]";
    return "bg-[#EF4444]";
  };

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-end">
        <span className="text-sm font-medium text-[#1E293B]">
          {label}
          {weight && <span className="text-xs text-[#64748B] font-normal ml-1">({weight * 100}% weight)</span>}
        </span>
        <span className="text-sm font-bold text-[#1E293B]">{Math.round(score)}%</span>
      </div>
      <div className="h-2 w-full bg-[#E2E8F0] rounded-full overflow-hidden">
        <div 
          className={`h-full ${getColorClass(score)} progress-bar-animate`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}
