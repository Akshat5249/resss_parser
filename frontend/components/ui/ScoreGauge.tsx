"use client";

import React, { useEffect, useState } from "react";

interface ScoreGaugeProps {
  score: number;
  size?: number;
  strokeWidth?: number;
}

export default function ScoreGauge({ 
  score, 
  size = 160, 
  strokeWidth = 12 
}: ScoreGaugeProps) {
  const [offset, setOffset] = useState(0);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;

  useEffect(() => {
    const progressOffset = ((100 - score) / 100) * circumference;
    setOffset(progressOffset);
  }, [score, circumference]);

  const getColor = (s: number) => {
    if (s >= 80) return "#10B981"; // success
    if (s >= 60) return "#4F46E5"; // indigo
    if (s >= 40) return "#F59E0B"; // amber
    return "#EF4444"; // red
  };

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E2E8F0"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={getColor(score)}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="score-gauge-animate"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-4xl font-bold" style={{ color: getColor(score) }}>
          {Math.round(score)}
        </span>
        <span className="text-xs text-[#64748B] font-medium uppercase tracking-wider">Score</span>
      </div>
    </div>
  );
}
