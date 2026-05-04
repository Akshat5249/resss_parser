import React from "react";
import { Quote, MessageSquare } from "lucide-react";

interface FeedbackCardProps {
  feedback: string;
}

export default function FeedbackCard({ feedback }: FeedbackCardProps) {
  // Structure check: usually AI returns 3 paragraphs separated by newlines
  const paragraphs = feedback.split("\n").filter(p => p.trim().length > 0);

  return (
    <div className="bg-[#4F46E5]/5 border border-[#4F46E5]/20 rounded-2xl p-8 relative overflow-hidden">
      <Quote className="absolute -top-4 -left-4 w-24 h-24 text-[#4F46E5]/5 transform -rotate-12" />
      
      <div className="relative z-10 space-y-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-3">
            <div className="bg-[#4F46E5] p-2 rounded-lg">
              <MessageSquare className="w-4 h-4 text-white fill-current" />
            </div>
            <h3 className="text-lg font-bold text-[#1E293B]">Career Coach Assessment</h3>
          </div>
          <div style={{
            fontSize: "11px",
            fontWeight: 700,
            background: "#EEF2FF",
            color: "#4F46E5",
            padding: "4px 10px",
            borderRadius: "100px",
            letterSpacing: "0.5px"
          }}>AI · PERSONALIZED</div>
        </div>

        <div className="space-y-4">
          {paragraphs.length > 0 ? (
            paragraphs.map((p, idx) => (
              <p key={idx} className="text-base text-[#334155] leading-relaxed italic">
                {p}
              </p>
            ))
          ) : (
            <p className="text-base text-[#334155] leading-relaxed italic">{feedback || "No feedback generated."}</p>
          )}
        </div>
      </div>
    </div>
  );
}
