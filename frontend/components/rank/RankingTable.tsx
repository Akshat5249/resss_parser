import React from "react";
import Link from "next/link";
import { Trophy, ExternalLink, TrendingUp, Users, FileDown } from "lucide-react";
import { RankingResponse } from "@/lib/types";
import SkillBadge from "../ui/SkillBadge";

interface RankingTableProps {
  data: RankingResponse;
}

export default function RankingTable({ data }: RankingTableProps) {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-[#EEF2FF] rounded-xl text-[#4F46E5]">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-bold text-[#64748B] uppercase tracking-wider">Total Evaluated</p>
            <p className="text-2xl font-bold text-[#111827]">{data.summary.total_resumes}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-[#DCFCE7] rounded-xl text-[#10B981]">
            <Trophy className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-bold text-[#64748B] uppercase tracking-wider">Top Match</p>
            <p className="text-xl font-bold text-[#111827] truncate max-w-[150px]">{data.summary.top_candidate}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-[#FFFBEB] rounded-xl text-[#F59E0B]">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-bold text-[#64748B] uppercase tracking-wider">Avg. Score</p>
            <p className="text-2xl font-bold text-[#1E293B]">{data.summary.average_score}%</p>
          </div>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0]">
                <th className="px-6 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider w-16">Rank</th>
                <th className="px-6 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider">Candidate</th>
                <th className="px-6 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider text-center">Score</th>
                <th className="px-6 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider text-center">Match</th>
                <th className="px-6 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider">Top Matched Skills</th>
                <th className="px-6 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9]">
              {data.rankings.map((entry) => (
                <tr 
                  key={entry.resume_job_id} 
                  className={`
                    hover:bg-[#F8FAFC] transition-colors
                    ${entry.rank === 1 ? "bg-[#FFFDF2]/50" : ""}
                    ${entry.rank === 2 ? "bg-[#F8F9FF]/50" : ""}
                  `}
                >
                  <td className="px-6 py-4">
                    <span className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                      entry.rank === 1 ? "bg-[#F59E0B] text-white" : 
                      entry.rank === 2 ? "bg-[#94A3B8] text-white" : 
                      "bg-[#F1F5F9] text-[#64748B]"
                    }`}>
                      {entry.rank}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-sm font-bold text-[#1E293B]">{entry.candidate_name}</p>
                    <p className="text-[10px] font-medium text-[#64748B]">{entry.recommendation}</p>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className={`px-2.5 py-1 rounded-lg text-sm font-bold ${
                      entry.score_total >= 80 ? "bg-[#DCFCE7] text-[#10B981]" :
                      entry.score_total >= 60 ? "bg-[#EEF2FF] text-[#4F46E5]" :
                      "bg-[#FFFBEB] text-[#F59E0B]"
                    }`}>
                      {entry.score_total}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center text-sm font-medium text-[#1E293B]">
                    {(entry.semantic_similarity * 100).toFixed(0)}%
                  </td>
                  <td className="px-6 py-4">
                    {/* Improvement 2 fix: Show top matched skills */}
                    <div className="flex flex-wrap gap-1.5 max-w-[280px]">
                      {entry.top_matched_skills && entry.top_matched_skills.length > 0 ? (
                        entry.top_matched_skills.slice(0, 4).map(skill => (
                          <span key={skill} className="text-[10px] font-bold bg-[#EEF2FF] text-[#4F46E5] px-2 py-0.5 rounded-full border border-[#C7D2FE]">
                            {skill}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs text-[#94A3B8] italic">—</span>
                      )}
                      {entry.matched_skills_count > 4 && (
                        <span className="text-[9px] font-bold text-[#64748B] self-center">+{entry.matched_skills_count - 4} more</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right space-x-3">
                    {/* Bug 2 fix: Direct PDF link + View Details link */}
                    <Link 
                      href={`/results/${entry.resume_job_id}`}
                      className="inline-flex items-center text-xs font-bold text-[#6B7280] hover:text-[#111827] transition-colors"
                    >
                      <span>Details</span>
                    </Link>
                    <a 
                      href={`${process.env.NEXT_PUBLIC_API_URL}/report/${entry.resume_job_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-1 text-xs font-bold text-[#4F46E5] hover:underline"
                    >
                      <span>PDF</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
