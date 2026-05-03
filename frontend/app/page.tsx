"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { 
  UploadCloud, 
  CheckCircle2, 
  Loader2, 
  Sparkles, 
  Target, 
  Zap, 
  ArrowRight,
  ChevronDown,
  ChevronUp,
  FileText,
  Search,
  Briefcase
} from "lucide-react";
import ResumeDropzone from "@/components/upload/ResumeDropzone";
import JDInput from "@/components/upload/JDInput";
import { resumeApi, analyzeApi } from "@/lib/api";
import { usePolling } from "@/hooks/usePolling";
import { toast } from "react-hot-toast";

type PageState =
  | "idle"           // nothing uploaded yet
  | "uploading"      // resume being uploaded
  | "scanned"        // baseline scan complete, score shown
  | "jd_ready"       // JD also saved, ready for full analysis
  | "analyzing"      // full analysis running
  | "analyzed";      // full analysis complete

export default function HomePage() {
  const router = useRouter();
  
  const [pageState, setPageState] = useState<PageState>("idle");
  const [resumeJobId, setResumeJobId] = useState<string | null>(null);
  const [jdJobId, setJdJobId] = useState<string | null>(null);
  const [baselineResult, setBaselineResult] = useState<any>(null);
  const [baselineLoading, setBaselineLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analyzeMessage, setAnalyzeMessage] = useState("");
  const [pollingJobId, setPollingJobId] = useState<string | null>(null);
  const [isJdExpanded, setIsJdExpanded] = useState(false);
  const [filename, setFilename] = useState("");

  const messages = [
    "Matching your skills against the job description...",
    "Running AI gap detection...",
    "Generating improvement suggestions...",
    "Almost ready..."
  ];

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (pageState === "analyzing") {
      let idx = 0;
      setAnalyzeMessage(messages[0]);
      interval = setInterval(() => {
        idx = (idx + 1) % messages.length;
        setAnalyzeMessage(messages[idx]);
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [pageState]);

  const fetchBaseline = async (jobId: string, retries = 12) => {
    setBaselineLoading(true);
    for (let i = 0; i < retries; i++) {
      try {
        const jobData = await resumeApi.get(jobId);
        if (jobData.analysis?.score_total) {
          setBaselineResult({
            name: jobData.job_details?.parsed_data?.name,
            skills: jobData.job_details?.parsed_data?.skills || [],
            experience: jobData.job_details?.parsed_data?.experience || [],
            projects: jobData.job_details?.parsed_data?.projects || [],
            score: jobData.analysis?.score_breakdown || {},
            score_total: jobData.analysis?.score_total || 0,
            score_label: jobData.score_label || "Scanned"
          });
          setBaselineLoading(false);
          setPageState("scanned");
          return;
        }
      } catch (err) {
        console.error("Baseline fetch error", err);
      }
      await new Promise(r => setTimeout(r, 2500));
    }
    setBaselineLoading(false);
    toast.error("Analysis is taking longer than expected. We'll keep trying.");
  };

  const handleFileSelect = async (file: File) => {
    setFilename(file.name);
    setPageState("uploading");
    setUploadProgress(10);
    
    // Progress simulation
    const p = setInterval(() => {
      setUploadProgress(prev => (prev >= 85 ? 85 : prev + 5));
    }, 300);

    try {
      const data = await resumeApi.upload(file);
      clearInterval(p);
      setUploadProgress(100);
      setResumeJobId(data.job_id);
      setPageState("scanned");
      fetchBaseline(data.job_id);
    } catch (err) {
      clearInterval(p);
      setPageState("idle");
      toast.error("Upload failed. Please try again.");
    }
  };

  const handleJDReady = (id: string) => {
    setJdJobId(id);
    setPageState("jd_ready");
  };

  const handleJDReset = () => {
    setJdJobId(null);
    setPageState("scanned");
  };

  const handleFullAnalysis = async () => {
    if (!resumeJobId || !jdJobId) return;
    setPageState("analyzing");
    try {
      await analyzeApi.start(resumeJobId, jdJobId);
      setPollingJobId(resumeJobId);
    } catch (err) {
      setPageState("jd_ready");
      toast.error("Failed to start analysis");
    }
  };

  usePolling({
    jobId: pollingJobId,
    pollFn: analyzeApi.getStatus,
    onComplete: (id) => {
      router.push(`/results/${id}`);
    },
    onError: (msg) => {
      setPageState("jd_ready");
      setPollingJobId(null);
      toast.error(msg);
    }
  });

  const getScoreColor = (score: number) => {
    if (score >= 80) return "#10B981";
    if (score >= 60) return "#4F46E5";
    if (score >= 40) return "#F59E0B";
    return "#EF4444";
  };

  return (
    <div style={{ minHeight: "100vh", paddingBottom: "100px" }}>
      {/* SECTION 1: HERO */}
      <section style={{ maxWidth: "640px", margin: "0 auto", padding: "64px 16px 40px", textAlign: "center" }}>
        <div style={{
          display: "inline-flex", alignItems: "center", gap: "6px",
          background: "#EEF2FF", color: "#4F46E5",
          borderRadius: "100px", padding: "4px 12px",
          fontSize: "12px", fontWeight: 500,
          marginBottom: "20px"
        }}>
          <span>✦</span> AI-Powered Resume Analysis
        </div>
        <h1 style={{
          fontSize: "clamp(28px, 5vw, 48px)",
          fontWeight: 700,
          lineHeight: 1.15,
          color: "#0A0A0A",
          marginBottom: "16px",
          letterSpacing: "-0.5px"
        }}>
          Know exactly why you're<br/>
          <span style={{ color: "#4F46E5" }}>not getting callbacks</span>
        </h1>
        <p style={{
          fontSize: "16px",
          color: "#6B7280",
          maxWidth: "480px",
          margin: "0 auto 32px",
          lineHeight: 1.6
        }}>
          Upload your resume. Get an instant ATS score, see missing skills,
          and get AI-rewritten bullet points — no job description required.
        </p>
      </section>

      {/* SECTION 2: MAIN CARD */}
      <section style={{ maxWidth: "640px", margin: "0 auto", padding: "0 16px" }}>
        <div style={{
          background: "white",
          border: "1px solid #E5E7EB",
          borderRadius: "16px",
          padding: "32px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.04)"
        }}>
          {/* IDLE OR UPLOADING STATE */}
          {(pageState === "idle" || pageState === "uploading") && (
            <div className="animate-fade-in">
              <label style={{ fontSize: "11px", fontWeight: 700, color: "#6B7280", textTransform: "uppercase", letterSpacing: "1px", marginBottom: "12px", display: "block" }}>
                Upload your resume
              </label>
              {pageState === "idle" ? (
                <ResumeDropzone onFileSelect={handleFileSelect} />
              ) : (
                <div style={{
                  border: "2px solid #F3F4F6",
                  borderRadius: "12px",
                  padding: "48px 24px",
                  textAlign: "center"
                }}>
                  <Loader2 size={40} color="#4F46E5" className="animate-spin" style={{ margin: "0 auto" }} />
                  <p style={{ fontSize: "15px", fontWeight: 500, color: "#374151", margin: "12px 0 4px" }}>
                    Uploading {filename.length > 20 ? filename.slice(0, 20) + "..." : filename}
                  </p>
                  <div style={{
                    height: "4px",
                    background: "#F3F4F6",
                    borderRadius: "100px",
                    margin: "16px auto 0",
                    maxWidth: "200px",
                    overflow: "hidden"
                  }}>
                    <div style={{
                      height: "100%",
                      background: "#4F46E5",
                      borderRadius: "100px",
                      width: `${uploadProgress}%`,
                      transition: "width 0.3s ease"
                    }}/>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* SCANNED OR JD READY OR ANALYZING STATE */}
          {(pageState === "scanned" || pageState === "jd_ready" || pageState === "analyzing") && (
            <div className="animate-fade-in space-y-6">
              {/* HEADER INFO */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "32px" }}>
                <div>
                  <div style={{ display: "inline-flex", alignItems: "center", gap: "6px", background: "#ECFDF5", color: "#059669", padding: "4px 10px", borderRadius: "100px", fontSize: "12px", fontWeight: 600, marginBottom: "8px" }}>
                    <CheckCircle2 size={14} /> Resume Uploaded
                  </div>
                  <p style={{ fontSize: "13px", color: "#6B7280", margin: 0 }}>
                    {filename} · <button onClick={() => { setPageState("idle"); setBaselineResult(null); }} style={{ background: "none", border: "none", color: "#4F46E5", fontWeight: 600, cursor: "pointer", fontSize: "13px", padding: 0 }}>Change</button>
                  </p>
                </div>

                {/* Score Circular Display */}
                <div style={{ position: "relative", width: "100px", height: "100px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <svg viewBox="0 0 80 80" style={{ width: "100%", height: "100%", transform: "rotate(-90deg)" }}>
                    <circle cx="40" cy="40" r="36" fill="none" stroke="#F3F4F6" strokeWidth="6" />
                    {baselineResult && (
                      <circle 
                        cx="40" cy="40" r="36" fill="none" 
                        stroke={getScoreColor(baselineResult.score_total)} 
                        strokeWidth="6" 
                        strokeLinecap="round"
                        strokeDasharray="226.2"
                        strokeDashoffset={226.2 - (baselineResult.score_total / 100 * 226.2)}
                        className="score-circle-path"
                      />
                    )}
                    {baselineLoading && (
                      <circle 
                        cx="40" cy="40" r="36" fill="none" 
                        stroke="#4F46E5" 
                        strokeWidth="6" 
                        strokeLinecap="round"
                        strokeDasharray="40 186"
                        className="animate-spin"
                        style={{ transformOrigin: "center" }}
                      />
                    )}
                  </svg>
                  <div style={{ position: "absolute", textAlign: "center" }}>
                    {baselineLoading ? (
                      <span className="animate-pulse" style={{ fontSize: "24px", fontWeight: 800, color: "#9CA3AF" }}>...</span>
                    ) : (
                      <span style={{ fontSize: "28px", fontWeight: 800, color: "#0A0A0A", display: "block", lineHeight: 1 }}>{Math.round(baselineResult?.score_total || 0)}</span>
                    )}
                    <span style={{ fontSize: "10px", fontWeight: 700, color: "#9CA3AF", textTransform: "uppercase" }}>Score</span>
                  </div>
                </div>
              </div>

              {/* Baseline Result Content */}
              {baselineLoading ? (
                <div style={{ textAlign: "center", padding: "20px 0" }}>
                   <p style={{ fontSize: "14px", fontWeight: 600, color: "#374151" }}>Computing your ATS score...</p>
                   <p style={{ fontSize: "12px", color: "#9CA3AF", marginTop: "4px" }}>This takes about 15-20 seconds</p>
                </div>
              ) : baselineResult && (
                <>
                  {/* Breakdown Grid */}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "32px" }}>
                    {Object.entries(baselineResult.score).map(([key, val]: [string, any]) => (
                      <div key={key}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                          <span style={{ fontSize: "11px", color: "#6B7280", fontWeight: 500 }}>{key.replace("_", " ").toUpperCase()}</span>
                          <span style={{ fontSize: "11px", color: "#0A0A0A", fontWeight: 600 }}>{Math.round(val)}%</span>
                        </div>
                        <div style={{ height: "4px", background: "#F3F4F6", borderRadius: "10px", overflow: "hidden" }}>
                          <div style={{ height: "100%", background: getScoreColor(val), width: `${val}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Parsed Pills */}
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "32px", borderBottom: "1px solid #F3F4F6", paddingBottom: "24px" }}>
                    <div style={{ background: "#F9FAFB", border: "1px solid #E5E7EB", borderRadius: "100px", padding: "4px 12px", fontSize: "12px", color: "#374151", fontWeight: 500 }}>
                      {baselineResult.skills.length} skills detected
                    </div>
                    <div style={{ background: "#F9FAFB", border: "1px solid #E5E7EB", borderRadius: "100px", padding: "4px 12px", fontSize: "12px", color: "#374151", fontWeight: 500 }}>
                       {baselineResult.experience.length} roles found
                    </div>
                    <div style={{ background: "#F9FAFB", border: "1px solid #E5E7EB", borderRadius: "100px", padding: "4px 12px", fontSize: "12px", color: "#374151", fontWeight: 500 }}>
                       {baselineResult.projects.length} projects
                    </div>
                  </div>
                </>
              )}

              {/* JD UPGRADE SECTION */}
              {!baselineLoading && (
                <div style={{ background: "#FAFAFA", border: "1px solid #E5E7EB", borderRadius: "12px", padding: "20px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontSize: "14px", fontWeight: 600, color: "#0A0A0A", margin: "0 0 4px" }}>
                        Want a deeper analysis?
                      </p>
                      <p style={{ fontSize: "13px", color: "#6B7280", margin: 0, lineHeight: 1.5 }}>
                        Add a job description to see skill gaps, get AI-rewritten bullets, and a match score for a specific role.
                      </p>
                    </div>
                    <button 
                      onClick={() => setIsJdExpanded(!isJdExpanded)}
                      style={{ background: "#F3F4F6", border: "none", borderRadius: "8px", padding: "8px", cursor: "pointer", marginLeft: "16px" }}
                    >
                      {isJdExpanded ? <ChevronUp size={18} color="#6B7280" /> : <ChevronDown size={18} color="#6B7280" />}
                    </button>
                  </div>

                  <div style={{ 
                    maxHeight: isJdExpanded ? "1000px" : "0", 
                    overflow: "hidden", 
                    transition: "max-height 0.4s ease-in-out" 
                  }}>
                    <div style={{ paddingTop: "20px" }}>
                      <JDInput onJDReady={handleJDReady} onReset={handleJDReset} onError={(msg) => toast.error(msg)} />
                    </div>
                  </div>
                </div>
              )}

              {/* ACTIONS */}
              {pageState === "jd_ready" && (
                <button onClick={handleFullAnalysis} style={{
                  width: "100%",
                  height: "52px",
                  background: "linear-gradient(135deg, #4F46E5, #7C3AED)",
                  color: "white",
                  border: "none",
                  borderRadius: "12px",
                  fontSize: "15px",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  marginTop: "20px",
                  boxShadow: "0 4px 14px rgba(79,70,229,0.3)",
                  transition: "transform 0.1s"
                }}
                onMouseDown={(e) => e.currentTarget.style.transform = "scale(0.99)"}
                onMouseUp={(e) => e.currentTarget.style.transform = "scale(1)"}
                >
                  <Sparkles size={18} /> Run Full Analysis
                </button>
              )}

              {pageState === "analyzing" && (
                <div style={{ marginTop: "20px" }}>
                  <div style={{
                    width: "100%",
                    height: "52px",
                    background: "#F3F4F6",
                    borderRadius: "12px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "12px"
                  }}>
                    <Loader2 size={20} color="#4F46E5" className="animate-spin" />
                    <span style={{ fontSize: "14px", color: "#6B7280" }}>{analyzeMessage}</span>
                  </div>
                  <div style={{
                    height: "3px",
                    background: "linear-gradient(90deg, #4F46E5, #7C3AED, #4F46E5)",
                    backgroundSize: "200% 100%",
                    animation: "shimmer 1.5s infinite",
                    borderRadius: "100px",
                    marginTop: "8px"
                  }}/>
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* SECTION 3: FEATURES */}
      <section style={{ maxWidth: "640px", margin: "64px auto 0", padding: "0 16px" }}>
        <div style={{ display: "flex", gap: "32px", flexWrap: "wrap", justifyContent: "space-between" }}>
           <div style={{ flex: "1 1 180px" }}>
              <div style={{ width: "36px", height: "36px", background: "#F3F4F6", borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Target size={18} color="#4F46E5" />
              </div>
              <h3 style={{ fontSize: "14px", fontWeight: 600, color: "#0A0A0A", margin: "12px 0 4px" }}>Weighted Scoring</h3>
              <p style={{ fontSize: "13px", color: "#9CA3AF", lineHeight: 1.5 }}>Skills 40%, experience 25%, projects 15%, education 10%.</p>
           </div>
           <div style={{ flex: "1 1 180px" }}>
              <div style={{ width: "36px", height: "36px", background: "#F3F4F6", borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Zap size={18} color="#4F46E5" />
              </div>
              <h3 style={{ fontSize: "14px", fontWeight: 600, color: "#0A0A0A", margin: "12px 0 4px" }}>Instant Results</h3>
              <p style={{ fontSize: "13px", color: "#9CA3AF", lineHeight: 1.5 }}>Baseline score in under 5 seconds. Full analysis under 60.</p>
           </div>
           <div style={{ flex: "1 1 180px" }}>
              <div style={{ width: "36px", height: "36px", background: "#F3F4F6", borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Sparkles size={18} color="#4F46E5" />
              </div>
              <h3 style={{ fontSize: "14px", fontWeight: 600, color: "#0A0A0A", margin: "12px 0 4px" }}>GPT-4 Enhancement</h3>
              <p style={{ fontSize: "13px", color: "#9CA3AF", lineHeight: 1.5 }}>Bullet rewrites that actually sound human, not AI-generated.</p>
           </div>
        </div>
      </section>
    </div>
  );
}
