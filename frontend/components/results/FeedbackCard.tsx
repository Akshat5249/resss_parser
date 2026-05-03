import React from "react";
import { Quote } from "lucide-react";

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
        <div className="flex items-center space-x-3 mb-2">
          <div className="bg-[#4F46E5] p-2 rounded-lg">
            <Quote className="w-4 h-4 text-white fill-current" />
          </div>
          <h3 className="text-lg font-bold text-[#1E293B]">Career Coach Assessment</h3>
        </div>

        <div className="space-y-4">
          {paragraphs.length > 0 ? (
            paragraphs.map((p, idx) => (
              <p key={idx} className="text-base text-[#334155] leading-relaxed italic">
                {p}
              </p>
            ))
          ) : (
            <p className="text-base text-[#334155] leading-relaxed italic">{feedback}</p>
          )}
        </div>
      </div>

      <div className="mt-8 flex items-center space-x-4 border-t border-[#4F46E5]/10 pt-6">
        <div className="w-10 h-10 bg-gradient-to-br from-[#4F46E5] to-[#818CF8] rounded-full flex items-center justify-center text-white font-bold">
          AI
        </div>
        <div>
          <p className="text-sm font-bold text-[#1E293B]">ATS Coaching Intelligence</p>
          <p className="text-xs text-[#64748B]">Personalized feedback based on Job Description</p>
        </div>
      </div>
    </div>
  );
}
