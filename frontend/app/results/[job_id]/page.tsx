"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  FileDown, 
  ArrowLeft, 
  LayoutDashboard, 
  FileText, 
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles
} from "lucide-react";
import { analyzeApi, reportApi } from "@/lib/api";
import { AnalysisResult } from "@/lib/types";
import ScoreOverview from "@/components/results/ScoreOverview";
import SkillsAnalysis from "@/components/results/SkillsAnalysis";
import GapAnalysis from "@/components/results/GapAnalysis";
import Enhancements from "@/components/results/Enhancements";
import LearningPath from "@/components/results/LearningPath";
import FeedbackCard from "@/components/results/FeedbackCard";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import { toast } from "react-hot-toast";

export default function ResultsPage() {
  const { job_id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!job_id) return;
      try {
        const result = await analyzeApi.getResult(job_id as string);
        setData(result);
      } catch (err: any) {
        const msg = err.response?.data?.detail || "Failed to load results";
        setError(msg);
        toast.error(msg);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [job_id]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] bg-white">
        <LoadingSpinner size="lg" message="Reading your AI analysis..." />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-md mx-auto mt-24 text-center space-y-6 px-6">
        <div className="bg-white p-10 rounded-3xl border border-[#E5E7EB] shadow-xl">
          <div className="w-16 h-16 bg-[#FEF2F2] rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle className="w-8 h-8 text-[#DC2626]" />
          </div>
          <h2 className="text-xl font-bold text-[#111827] mb-2">Analysis Not Found</h2>
          <p className="text-sm text-[#6B7280] mb-8 leading-relaxed">
            {error || "We couldn't find the results for this scan ID."}
          </p>
          <button 
            onClick={() => router.push('/')}
            className="w-full py-3.5 bg-[#111827] text-white rounded-xl font-bold hover:bg-black transition-all"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const roleTitle = data.jd_job_id ? "Job Analysis" : "Resume Analysis";

  const matchedSkills = {
    required_matched: data.matched_skills?.required_matched ?? [],
    required_missing: data.matched_skills?.required_missing ?? [],
    preferred_matched: data.matched_skills?.preferred_matched ?? [],
    preferred_missing: data.matched_skills?.preferred_missing ?? []
  };

  return (
    <div className="min-h-screen bg-[#F9FAFB]">
      {/* Sticky Top Bar */}
      <div className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-[#E5E7EB] px-6 py-3">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button 
              onClick={() => router.push('/')}
              className="p-2 hover:bg-[#F3F4F6] rounded-lg transition-colors group"
              title="Go back"
            >
              <ArrowLeft className="w-5 h-5 text-[#6B7280] group-hover:text-[#111827]" />
            </button>
            <div className="h-6 w-px bg-[#E5E7EB]"></div>
            <div>
              <p className="text-xs font-bold text-[#6B7280] uppercase tracking-widest">Analysis Report</p>
              <p className="text-sm font-bold text-[#111827] truncate max-w-[150px] md:max-w-xs">
                {data.score_label} Match Found
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <a 
              href={reportApi.getReportUrl(data.resume_job_id)}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center px-4 py-2 bg-[#4F46E5] text-white rounded-lg text-xs font-bold hover:bg-[#4338CA] transition-all shadow-lg shadow-[#4F46E5]/20"
            >
              <FileDown className="w-3.5 h-3.5 mr-2" />
              <span className="hidden sm:inline">Download PDF</span>
              <span className="sm:hidden">PDF</span>
            </a>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-12 pb-32 space-y-16">
        {/* 1. Score Overview */}
        <section>
          <div className="flex items-center space-x-2 mb-8">
            <div className="w-8 h-8 bg-white rounded-lg border border-[#E5E7EB] flex items-center justify-center shadow-sm">
              <LayoutDashboard className="w-4 h-4 text-[#4F46E5]" />
            </div>
            <h2 className="text-lg font-bold text-[#111827]">Performance Dashboard</h2>
          </div>
          
          <div className="bg-white rounded-3xl border border-[#E5E7EB] p-10 shadow-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#4F46E5]/5 rounded-full -mr-32 -mt-32 blur-3xl"></div>
            <div className="relative z-10 flex flex-col md:flex-row items-center gap-12">
              <div className="flex flex-col items-center">
                <div className="relative group">
                  <div className="absolute inset-0 bg-[#4F46E5]/10 rounded-full blur-xl group-hover:bg-[#4F46E5]/20 transition-all"></div>
                  <div className="relative bg-white rounded-full p-4 shadow-inner">
                    <ScoreOverview 
                      score={data.score} 
                      label={data.score_label} 
                      similarity={data.semantic_similarity}
                      roleTitle={roleTitle} 
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 2. Feedback Card */}
        <section>
          <div className="border-l-4 border-[#4F46E5]">
            <FeedbackCard feedback={data.feedback} />
          </div>
        </section>

        {/* 3. Skills & Requirements */}
        <section className="space-y-8">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-white rounded-lg border border-[#E5E7EB] flex items-center justify-center shadow-sm">
              <FileText className="w-4 h-4 text-[#059669]" />
            </div>
            <h2 className="text-lg font-bold text-[#111827]">Requirements Alignment</h2>
          </div>
          
          <SkillsAnalysis skills={matchedSkills} />
        </section>

        {/* 4. Deep Gap Analysis */}
        <section>
          <GapAnalysis gaps={data.gaps} />
        </section>

        {/* 5. AI Enhancements */}
        {data.enhancements && data.enhancements.length > 0 && (
          <section>
            <Enhancements enhancements={data.enhancements} />
          </section>
        )}

        {/* 6. Learning Roadmap */}
        <section>
          <LearningPath path={data.learning_path} />
        </section>
      </div>
    </div>
  );
}
