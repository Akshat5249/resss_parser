"use client";

import React, { useEffect, useState } from "react";
import ScoreGauge from "../ui/ScoreGauge";
import ScoreBar from "../ui/ScoreBar";
import { ScoreBreakdown } from "@/lib/types";

interface ScoreOverviewProps {
  score: ScoreBreakdown;
  label: string;
  similarity: number;
  roleTitle: string;
}

export default function ScoreOverview({ 
  score, 
  label, 
  similarity, 
  roleTitle 
}: ScoreOverviewProps) {
  const getScoreColor = (s: number) => {
    if (s >= 80) return "text-[#10B981]";
    if (s >= 60) return "text-[#4F46E5]";
    if (s >= 40) return "text-[#F59E0B]";
    return "text-[#EF4444]";
  };

  return (
    <div className="w-full flex flex-col md:flex-row items-center md:items-start gap-12">
      {/* Large Score Circle */}
      <div className="flex flex-col items-center space-y-2">
        <div className="relative flex items-center justify-center">
          <ScoreGauge score={score.total} size={200} strokeWidth={14} />
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-7xl font-black tracking-tighter ${getScoreColor(score.total)}`}>
              {Math.round(score.total)}
            </span>
          </div>
        </div>
        <p className={`text-xl font-extrabold uppercase tracking-widest ${getScoreColor(score.total)}`}>
          {label}
        </p>
      </div>

      {/* Breakdown Bars */}
      <div className="flex-1 w-full grid grid-cols-1 sm:grid-cols-2 gap-x-12 gap-y-8 py-4">
        <ScoreBar label="Skill Match" score={score.skill_match} weight={0.4} />
        <ScoreBar label="Experience" score={score.experience} weight={0.25} />
        <ScoreBar label="Projects" score={score.projects} weight={0.15} />
        <ScoreBar label="Education" score={score.education} weight={0.1} />
        <ScoreBar label="Formatting" score={score.formatting} weight={0.1} />
      </div>
    </div>
  );
}
