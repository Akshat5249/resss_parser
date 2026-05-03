import React from "react";

interface SkillBadgeProps {
  skill: string;
  variant: "matched" | "missing" | "preferred" | "neutral";
}

export default function SkillBadge({ skill, variant }: SkillBadgeProps) {
  const variants = {
    matched: "bg-[#DCFCE7] text-[#10B981] border-[#BBF7D0]",
    missing: "bg-[#FEE2E2] text-[#EF4444] border-[#FECACA]",
    preferred: "bg-[#E0F2FE] text-[#0EA5E9] border-[#BAE6FD]",
    neutral: "bg-[#F1F5F9] text-[#64748B] border-[#E2E8F0]",
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${variants[variant]}`}>
      {skill}
    </span>
  );
}
