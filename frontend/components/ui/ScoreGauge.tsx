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
  strokeWidth = 10 
}: ScoreGaugeProps) {
  // UI FIX 1: Use specific structure with ONE text element inside SVG
  const scoreInt = Math.round(score);
  
  const getColor = (s: number) => {
    if (s >= 70) return "#10B981"; // success
    if (s >= 40) return "#4F46E5"; // indigo
    return "#F59E0B"; // amber
  };

  const scoreColor = getColor(scoreInt);
  
  // Circumference of r=60 is 2*π*60 ≈ 377
  // strokeDasharray = (score/100) * 377 filled, rest empty.
  const dashOffset = (scoreInt / 100) * 377;

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg viewBox="0 0 160 160" width={size} height={size} style={{ display: "block", margin: "0 auto" }}>
        {/* Background circle */}
        <circle 
          cx="80" cy="80" r="60"
          fill="none" 
          stroke="#F3F4F6" 
          strokeWidth="10"
        />
        
        {/* Progress circle */}
        <circle 
          cx="80" cy="80" r="60"
          fill="none"
          stroke={scoreColor}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${dashOffset} 377`}
          transform="rotate(-90 80 80)"
          style={{ transition: "stroke-dasharray 1.2s ease" }}
        />
        
        {/* Score number (ONE text element only) */}
        <text 
          x="80" y="76"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="32"
          fontWeight="700"
          fontFamily="inherit"
          fill={scoreColor}
        >
          {scoreInt}
        </text>
        
        {/* "SCORE" label */}
        <text 
          x="80" y="100"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="11"
          fontWeight="500"
          fontFamily="inherit"
          fill="#9CA3AF"
          letterSpacing="1.5"
        >
          SCORE
        </text>
      </svg>
    </div>
  );
}
