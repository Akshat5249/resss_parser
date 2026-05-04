"use client";

import React from "react";
import ScoreGauge from "../ui/ScoreGauge";
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
  // UI FIX 2: Specific layout with progress bars
  const scoreItems = [
    { label: "Skill Match", weight: "40%", value: score.skill_match ?? 0 },
    { label: "Experience",  weight: "25%", value: score.experience ?? 0 },
    { label: "Projects",    weight: "15%", value: score.projects ?? 0 },
    { label: "Education",   weight: "10%", value: score.education ?? 0 },
    { label: "Formatting",  weight: "10%", value: score.formatting ?? 0 },
  ];

  const getBarColor = (v: number) =>
    v >= 70 ? "#10B981" : v >= 40 ? "#4F46E5" : "#F59E0B";

  return (
    <div className="w-full flex flex-col items-center">
      {/* Large Score Circle - UI FIX 1: removed double number overlay */}
      <div className="flex flex-col items-center space-y-2 mb-8">
        <ScoreGauge score={score.total} size={200} />
        <p className="text-xl font-extrabold uppercase tracking-widest text-[#111827]">
          {label}
        </p>
      </div>

      {/* Breakdown Bars - UI FIX 2 */}
      <div style={{
        maxWidth: "440px",
        margin: "0 auto",
        width: "100%",
        padding: "0 16px"
      }}>
        {scoreItems.map(item => {
          const val = Math.round(item.value ?? 0);
          const color = getBarColor(val);
          return (
            <div key={item.label} style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "10px"
            }}>
              <span style={{
                width: "88px",
                fontSize: "12px",
                color: "#6B7280",
                flexShrink: 0,
                textAlign: "right"
              }}>{item.label}</span>
              
              <span style={{
                width: "30px",
                fontSize: "10px",
                color: "#C4C4C4",
                flexShrink: 0,
                textAlign: "center"
              }}>{item.weight}</span>
              
              <div style={{
                flex: 1,
                height: "6px",
                background: "#F3F4F6",
                borderRadius: "100px",
                overflow: "hidden",
                minWidth: "60px"
              }}>
                <div style={{
                  height: "100%",
                  width: `${val}%`,
                  background: color,
                  borderRadius: "100px",
                  transition: "width 1.2s ease"
                }}/>
              </div>
              
              <span style={{
                width: "30px",
                fontSize: "12px",
                fontWeight: 600,
                color: color,
                flexShrink: 0,
                textAlign: "right"
              }}>{val}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
