"use client";

import React, { useState, useRef } from "react";
import Link from "next/link";
import { 
  Users, 
  FileText, 
  X, 
  Loader2, 
  Trophy, 
  TrendingUp, 
  ExternalLink,
  Target,
  Search,
  CheckCircle2,
  AlertCircle,
  Plus
} from "lucide-react";
import JDInput from "@/components/upload/JDInput";
import { resumeApi, rankApi } from "@/lib/api";
import { RankingResponse } from "@/lib/types";
import { toast } from "react-hot-toast";

interface ResumeUpload {
  id: string;          // local temp id before upload
  jobId: string | null; // resume_job_id after upload
  filename: string;
  status: "uploading" | "done" | "error";
}

export default function RankPage() {
  const [jdJobId, setJdJobId] = useState<string | null>(null);
  const [jdSaved, setJdSaved] = useState(false);
  const [resumes, setResumes] = useState<ResumeUpload[]>([]);
  const [isRanking, setIsRanking] = useState(false);
  const [rankResult, setRankResult] = useState<RankingResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const readyCount = resumes.filter(r => r.status === "done" && r.jobId).length;
  const canRank = jdJobId !== null && readyCount >= 2 && !isRanking;

  const handleFilesSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    for (const file of files) {
      const localId = Math.random().toString(36).slice(2);
      
      setResumes(prev => [...prev, {
        id: localId,
        jobId: null,
        filename: file.name,
        status: "uploading"
      }]);
      
      // Upload in background
      resumeApi.upload(file)
        .then(data => {
          setResumes(prev => prev.map(r =>
            r.id === localId
              ? {...r, jobId: data.job_id, status: "done"}
              : r
          ));
        })
        .catch(() => {
          setResumes(prev => prev.map(r =>
            r.id === localId ? {...r, status: "error"} : r
          ));
          toast.error(`Failed to upload ${file.name}`);
        });
    }
    
    // Reset input so same file can be re-added
    e.target.value = "";
  };

  const removeResume = (localId: string) => {
    setResumes(prev => prev.filter(r => r.id !== localId));
  };

  const handleRank = async () => {
    const readyResumes = resumes.filter(r => r.status === "done" && r.jobId);
    if (!jdJobId || readyResumes.length < 2) return;
    
    setIsRanking(true);
    try {
      const result = await rankApi.rank(
        jdJobId,
        readyResumes.map(r => r.jobId!)
      );
      setRankResult(result);
      toast.success("Ranking complete!");
    } catch (err: any) {
      toast.error("Ranking failed. Please try again.");
    } finally {
      setIsRanking(false);
    }
  };

  const resetAll = () => {
    setRankResult(null);
    setResumes([]);
    setJdJobId(null);
    setJdSaved(false);
  };

  const resetJD = () => {
    setJdJobId(null);
    setJdSaved(false);
  };

  // --- STATE A: INPUT VIEW ---
  if (!rankResult) {
    return (
      <div style={{ maxWidth: "600px", margin: "0 auto", padding: "48px 24px 80px" }}>
        {/* Hero */}
        <div style={{ textAlign: "center", marginBottom: "40px" }}>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
            background: "#EEF2FF",
            color: "#4F46E5",
            borderRadius: "100px",
            padding: "4px 12px",
            fontSize: "12px",
            fontWeight: 500,
            marginBottom: "16px"
          }}>✦ Recruiter Tool</div>
          
          <h1 style={{
            fontSize: "32px",
            fontWeight: 700,
            color: "#0A0A0A",
            marginBottom: "12px"
          }}>Compare Multiple Candidates</h1>
          
          <p style={{
            fontSize: "15px",
            color: "#6B7280",
            maxWidth: "440px",
            margin: "0 auto",
            lineHeight: 1.6
          }}>
            Upload 2-20 resumes and a job description.
            Get an instant ranked leaderboard with match scores.
          </p>
        </div>

        {/* SECTION 1 — Job Description Card */}
        <div style={{
          background: "white",
          border: "1px solid #E5E7EB",
          borderRadius: "16px",
          padding: "24px",
          marginBottom: "16px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.06)"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            marginBottom: "16px"
          }}>
            <span style={{
              width: "24px",
              height: "24px",
              background: "#EEF2FF",
              color: "#4F46E5",
              borderRadius: "6px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "13px",
              fontWeight: 700
            }}>1</span>
            <span style={{ fontSize: "14px", fontWeight: 600, color: "#0A0A0A" }}>
              Target Job Description
            </span>
            {jdSaved && (
              <span style={{
                marginLeft: "auto",
                fontSize: "12px",
                padding: "3px 10px",
                background: "#ECFDF5",
                color: "#065F46",
                borderRadius: "100px",
                fontWeight: 500
              }}>✓ Saved</span>
            )}
          </div>
          
          {jdSaved ? (
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "12px 16px",
              background: "#F0FDF4",
              border: "1px solid #BBF7D0",
              borderRadius: "10px"
            }}>
              <span style={{ fontSize: "14px", color: "#065F46", fontWeight: 500 }}>
                ✓ Job description ready
              </span>
              <button onClick={resetJD} style={{
                fontSize: "12px",
                color: "#6B7280",
                background: "none",
                border: "none",
                cursor: "pointer",
                textDecoration: "underline"
              }}>Edit</button>
            </div>
          ) : (
            <JDInput 
              onJDReady={(id) => { setJdJobId(id); setJdSaved(true); }} 
              onReset={resetJD}
              onError={(msg) => toast.error(msg)}
            />
          )}
        </div>

        {/* SECTION 2 — Candidate Pool Card */}
        <div style={{
          background: "white",
          border: "1px solid #E5E7EB",
          borderRadius: "16px",
          padding: "24px",
          marginBottom: "24px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.06)"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "16px"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{
                width: "24px",
                height: "24px",
                background: "#EEF2FF",
                color: "#4F46E5",
                borderRadius: "6px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "13px",
                fontWeight: 700
              }}>2</span>
              <span style={{ fontSize: "14px", fontWeight: 600, color: "#0A0A0A" }}>
                Candidate Pool
              </span>
            </div>
            <span style={{ fontSize: "13px", color: "#9CA3AF" }}>
              {resumes.length}/20 uploaded
            </span>
          </div>
          
          <div style={{ marginBottom: resumes.length > 0 ? "16px" : "0" }}>
            {resumes.map(r => (
              <div key={r.id} style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "12px 14px",
                border: "1px solid #E5E7EB",
                borderRadius: "10px",
                marginBottom: "8px",
                background: r.status === "done" ? "#F0FDF4" : "white"
              }}>
                <FileText size={20} color="#9CA3AF" />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ 
                    fontSize: "13px", 
                    fontWeight: 500, 
                    color: "#374151",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis"
                  }}>
                    {r.filename}
                  </div>
                  <div style={{ 
                    fontSize: "11px", 
                    color: r.status === "done" ? "#059669" : r.status === "uploading" ? "#4F46E5" : r.status === "error" ? "#DC2626" : "#9CA3AF" 
                  }}>
                    {r.status === "done" ? "✓ Ready to rank"
                    : r.status === "uploading" ? "Uploading..."
                    : r.status === "error" ? "Upload failed"
                    : "Pending"}
                  </div>
                </div>
                <button 
                  onClick={() => removeResume(r.id)} 
                  style={{
                    width: "24px",
                    height: "24px",
                    background: "#FEF2F2",
                    border: "1px solid #FECACA",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontSize: "12px",
                    color: "#DC2626",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center"
                  }}
                >✕</button>
              </div>
            ))}
          </div>
          
          <button 
            onClick={() => fileInputRef.current?.click()} 
            style={{
              width: "100%",
              padding: "12px",
              border: "2px dashed #E5E7EB",
              borderRadius: "10px",
              background: "transparent",
              cursor: "pointer",
              fontSize: "13px",
              color: "#6B7280",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "6px",
              marginTop: "8px",
              transition: "all 0.15s"
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "#4F46E5";
              e.currentTarget.style.color = "#4F46E5";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "#E5E7EB";
              e.currentTarget.style.color = "#6B7280";
            }}
          >
            <Plus size={16} /> Add Resumes
          </button>
          <input 
            type="file" 
            ref={fileInputRef} 
            multiple 
            accept=".pdf,.docx"
            onChange={handleFilesSelected} 
            style={{ display: "none" }}
          />
          
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: "12px",
            fontSize: "12px",
            color: "#9CA3AF"
          }}>
            <span>{readyCount} of {resumes.length} ready</span>
            <span>Min: 2 · Max: 20</span>
          </div>
        </div>

        <button
          onClick={handleRank}
          disabled={!canRank}
          style={{
            width: "100%",
            height: "52px",
            background: canRank
              ? "linear-gradient(135deg, #4F46E5, #7C3AED)"
              : "#F3F4F6",
            color: canRank ? "white" : "#9CA3AF",
            border: "none",
            borderRadius: "12px",
            fontSize: "15px",
            fontWeight: 600,
            cursor: canRank ? "pointer" : "not-allowed",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            boxShadow: canRank ? "0 4px 14px rgba(79,70,229,0.25)" : "none",
            transition: "all 0.2s"
          }}
        >
          {isRanking ? (
            <>
              <Loader2 size={20} color="white" className="animate-spin" />
              Ranking candidates...
            </>
          ) : (
            <>✦ Rank {readyCount} Candidates</>
          )}
        </button>

        {!canRank && !isRanking && (
          <div style={{ textAlign: "center", marginTop: "12px", fontSize: "12px", color: "#F59E0B" }}>
            {!jdJobId && "⚠ Add a job description first · "}
            {readyCount < 2 && `⚠ Upload at least ${2 - readyCount} more resume${2 - readyCount > 1 ? "s" : ""}`}
          </div>
        )}
      </div>
    );
  }

  // --- STATE B: RESULTS VIEW ---
  const summary = rankResult.summary;
  const rankings = rankResult.rankings;

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto", padding: "64px 24px 120px" }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "32px"
      }}>
        <div>
          <h2 style={{ fontSize: "22px", fontWeight: 700, color: "#0A0A0A", margin: "0 0 4px" }}>
            Ranking Results
          </h2>
          <p style={{ fontSize: "14px", color: "#6B7280", margin: 0 }}>
            {summary.total_resumes} candidates ranked
          </p>
        </div>
        <button onClick={resetAll} style={{
          padding: "8px 16px",
          background: "white",
          border: "1px solid #E5E7EB",
          borderRadius: "8px",
          fontSize: "13px",
          fontWeight: 500,
          color: "#374151",
          cursor: "pointer",
          transition: "all 0.2s"
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = "#F9FAFB"}
        onMouseLeave={(e) => e.currentTarget.style.background = "white"}
        >+ New Ranking</button>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr",
        gap: "12px",
        marginBottom: "24px"
      }}>
        {/* Total Evaluated */}
        <div style={{
          background: "white",
          border: "1px solid #E5E7EB",
          borderRadius: "12px",
          padding: "16px 20px"
        }}>
          <div style={{
            fontSize: "11px", fontWeight: 600, color: "#9CA3AF",
            letterSpacing: "0.5px", marginBottom: "6px"
          }}>
            EVALUATED
          </div>
          <div style={{ fontSize: "28px", fontWeight: 700, color: "#0A0A0A" }}>
            {summary.total_resumes}
          </div>
          <div style={{ fontSize: "12px", color: "#6B7280" }}>candidates</div>
        </div>
        
        {/* Top Match */}
        <div style={{
          background: "white",
          border: "1px solid #E5E7EB",
          borderRadius: "12px",
          padding: "16px 20px",
          borderTop: "3px solid #4F46E5"
        }}>
          <div style={{
            fontSize: "11px", fontWeight: 600, color: "#9CA3AF",
            letterSpacing: "0.5px", marginBottom: "6px"
          }}>TOP MATCH</div>
          <div style={{
            fontSize: "18px", fontWeight: 700, color: "#0A0A0A",
            lineHeight: 1.2, margin: "4px 0"
          }}>
            {summary.top_candidate}
          </div>
          <div style={{ fontSize: "12px", color: "#4F46E5" }}>
            Score: {rankings[0]?.score_total}
          </div>
        </div>
        
        {/* Average Score */}
        <div style={{
          background: "white",
          border: "1px solid #E5E7EB",
          borderRadius: "12px",
          padding: "16px 20px"
        }}>
          <div style={{
            fontSize: "11px", fontWeight: 600, color: "#9CA3AF",
            letterSpacing: "0.5px", marginBottom: "6px"
          }}>AVG SCORE</div>
          <div style={{
            fontSize: "28px", fontWeight: 700,
            color: summary.average_score >= 70 ? "#059669"
                 : summary.average_score >= 50 ? "#4F46E5"
                 : "#F59E0B"
          }}>
            {Math.round(summary.average_score)}
          </div>
          <div style={{ fontSize: "12px", color: "#6B7280" }}>out of 100</div>
        </div>
      </div>

      <div style={{
        background: "white",
        border: "1px solid #E5E7EB",
        borderRadius: "16px",
        overflow: "hidden",
        boxShadow: "0 1px 3px rgba(0,0,0,0.06)"
      }}>
        {/* Table Header */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "60px 1fr 100px 80px 200px 140px",
          gap: "0",
          padding: "12px 20px",
          background: "#F9FAFB",
          borderBottom: "1px solid #E5E7EB",
          fontSize: "11px",
          fontWeight: 600,
          color: "#9CA3AF",
          letterSpacing: "0.5px"
        }}>
          <span>RANK</span>
          <span>CANDIDATE</span>
          <span style={{ textAlign: "center" }}>SCORE</span>
          <span style={{ textAlign: "center" }}>MATCH</span>
          <span>TOP SKILLS</span>
          <span style={{ textAlign: "right" }}>ACTIONS</span>
        </div>
        
        {rankings.map((entry, index) => (
          <div 
            key={entry.resume_job_id} 
            style={{
              display: "grid",
              gridTemplateColumns: "60px 1fr 100px 80px 200px 140px",
              gap: "0",
              padding: "16px 20px",
              borderBottom: "1px solid #F9FAFB",
              alignItems: "center",
              background: index === 0 ? "#FFFBF0" : "white",
              transition: "background 0.15s"
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = "#F9FAFB"}
            onMouseLeave={(e) => e.currentTarget.style.background = index === 0 ? "#FFFBF0" : "white"}
          >
            {/* Rank */}
            <div style={{ display: "flex", alignItems: "center" }}>
              {index === 0 ? (
                <div style={{
                  width: "32px", height: "32px",
                  background: "linear-gradient(135deg, #F59E0B, #D97706)",
                  borderRadius: "8px",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "14px", fontWeight: 700, color: "white"
                }}>1</div>
              ) : index === 1 ? (
                <div style={{
                  width: "32px", height: "32px",
                  background: "linear-gradient(135deg, #9CA3AF, #6B7280)",
                  borderRadius: "8px",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "14px", fontWeight: 700, color: "white"
                }}>2</div>
              ) : (
                <div style={{
                  width: "32px", height: "32px",
                  background: "#F3F4F6",
                  borderRadius: "8px",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "14px", fontWeight: 600, color: "#6B7280"
                }}>{index + 1}</div>
              )}
            </div>
            
            {/* Candidate */}
            <div style={{ minWidth: 0, paddingRight: "16px" }}>
              <div style={{ 
                fontSize: "14px", 
                fontWeight: 600, 
                color: "#0A0A0A",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis"
              }}>
                {entry.candidate_name}
              </div>
              <div style={{ fontSize: "12px", color: "#9CA3AF", marginTop: "2px" }}>
                {entry.recommendation}
              </div>
            </div>
            
            {/* Score */}
            <div style={{ textAlign: "center" }}>
              <span style={{
                fontSize: "20px",
                fontWeight: 700,
                color: entry.score_total >= 70 ? "#059669"
                     : entry.score_total >= 50 ? "#4F46E5"
                     : "#F59E0B"
              }}>{entry.score_total}</span>
              <div style={{ fontSize: "10px", color: "#9CA3AF" }}>/ 100</div>
            </div>
            
            {/* Match */}
            <div style={{ textAlign: "center" }}>
              <span style={{ fontSize: "14px", fontWeight: 600, color: "#374151" }}>
                {Math.round((entry.semantic_similarity || 0) * 100)}%
              </span>
            </div>
            
            {/* Top Skills */}
            <div style={{ display: "flex", gap: "4px", flexWrap: "wrap", paddingRight: "10px" }}>
              {(entry.top_matched_skills || []).slice(0, 3).map(skill => (
                <span key={skill} style={{
                  fontSize: "11px",
                  padding: "2px 8px",
                  background: "#EEF2FF",
                  color: "#4F46E5",
                  borderRadius: "100px",
                  whiteSpace: "nowrap",
                  border: "1px solid #C7D2FE"
                }}>{skill}</span>
              ))}
              {(!entry.top_matched_skills?.length) && (
                <span style={{ fontSize: "12px", color: "#D1D5DB" }}>—</span>
              )}
            </div>
            
            {/* Actions */}
            <div style={{
              display: "flex",
              gap: "6px",
              justifyContent: "flex-end"
            }}>
              <a 
                href={`/results/${entry.resume_job_id}`}
                style={{
                  padding: "6px 10px",
                  background: "#F3F4F6",
                  border: "1px solid #E5E7EB",
                  borderRadius: "6px",
                  fontSize: "12px",
                  fontWeight: 500,
                  color: "#374151",
                  textDecoration: "none",
                  whiteSpace: "nowrap"
                }}
              >Details</a>
              <a 
                href={`${process.env.NEXT_PUBLIC_API_URL}/report/${entry.resume_job_id}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  padding: "6px 10px",
                  background: "#4F46E5",
                  border: "none",
                  borderRadius: "6px",
                  fontSize: "12px",
                  fontWeight: 500,
                  color: "white",
                  textDecoration: "none",
                  whiteSpace: "nowrap",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px"
                }}
              >
                PDF <ExternalLink size={12} />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
