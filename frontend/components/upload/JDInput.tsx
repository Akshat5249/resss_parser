"use client";

import React, { useState } from "react";
import { CheckCircle2, FileText, Loader2, Type, Upload } from "lucide-react";
import { jdApi } from "@/lib/api";
import { toast } from "react-hot-toast";

interface JDInputProps {
  onJDReady: (jdJobId: string) => void;
  onReset: () => void;
  onError: (msg: string) => void;
}

type JDSubmitState = "idle" | "submitting" | "done";

export default function JDInput({ onJDReady, onReset, onError }: JDInputProps) {
  const [jdText, setJdText] = useState("");
  const [activeTab, setActiveTab] = useState<"text" | "file">("text");
  const [submitState, setSubmitState] = useState<JDSubmitState>("idle");

  const handleSubmitText = async () => {
    if (jdText.length < 100) return;
    setSubmitState("submitting");
    try {
      const result = await jdApi.uploadText(jdText);
      setSubmitState("done");
      onJDReady(result.jd_job_id);
      toast.success("Job description saved!");
    } catch (err) {
      setSubmitState("idle");
      onError("Failed to save job description");
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSubmitState("submitting");
    try {
      const result = await jdApi.uploadFile(file);
      setSubmitState("done");
      onJDReady(result.jd_job_id);
      toast.success("Job description file parsed!");
    } catch (err) {
      setSubmitState("idle");
      onError("Failed to parse JD file");
    }
  };

  const handleReset = () => {
    setSubmitState("idle");
    setJdText("");
    onReset();
  };

  if (submitState === "done") {
    return (
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "14px 16px",
        background: "#F0FDF4",
        border: "1px solid #BBF7D0",
        borderRadius: "10px"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <CheckCircle2 size={20} color="#15803D" />
          <span style={{ fontSize: "14px", fontWeight: 500, color: "#15803D" }}>
            Job description saved
          </span>
        </div>
        <button onClick={handleReset} style={{
          fontSize: "12px",
          color: "#6B7280",
          background: "none",
          border: "none",
          cursor: "pointer",
          textDecoration: "underline"
        }}>Edit</button>
      </div>
    );
  }

  return (
    <div style={{ width: "100%" }}>
      {/* Pill Toggle */}
      <div style={{
        display: "inline-flex",
        background: "#F3F4F6",
        borderRadius: "8px",
        padding: "3px",
        marginBottom: "12px"
      }}>
        <button 
          onClick={() => setActiveTab("text")}
          style={{
            padding: "6px 14px",
            borderRadius: "6px",
            border: "none",
            fontSize: "13px",
            fontWeight: 500,
            cursor: "pointer",
            background: activeTab === "text" ? "white" : "transparent",
            color: activeTab === "text" ? "#0A0A0A" : "#6B7280",
            boxShadow: activeTab === "text" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
            transition: "all 0.2s",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}
        >
          <Type size={14} /> Paste text
        </button>
        <button 
          onClick={() => setActiveTab("file")}
          style={{
            padding: "6px 14px",
            borderRadius: "6px",
            border: "none",
            fontSize: "13px",
            fontWeight: 500,
            cursor: "pointer",
            background: activeTab === "file" ? "white" : "transparent",
            color: activeTab === "file" ? "#0A0A0A" : "#6B7280",
            boxShadow: activeTab === "file" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
            transition: "all 0.2s",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}
        >
          <Upload size={14} /> Upload file
        </button>
      </div>

      {activeTab === "text" ? (
        <div style={{ position: "relative" }}>
          <textarea
            value={jdText}
            onChange={e => setJdText(e.target.value)}
            placeholder={"Paste the full job description here...\n\nInclude required skills, experience level, and responsibilities for best results."}
            disabled={submitState === "submitting"}
            style={{
              width: "100%",
              minHeight: "160px",
              padding: "14px",
              border: "1px solid #E5E7EB",
              borderRadius: "10px",
              fontSize: "14px",
              lineHeight: 1.6,
              color: "#374151",
              resize: "vertical",
              outline: "none",
              fontFamily: "inherit",
              transition: "border-color 0.2s"
            }}
            onFocus={(e) => e.target.style.borderColor = "#4F46E5"}
            onBlur={(e) => e.target.style.borderColor = "#E5E7EB"}
          />
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "12px" }}>
            <span style={{ 
              fontSize: "12px", 
              color: jdText.length >= 100 ? "#059669" : "#D97706" 
            }}>
              {jdText.length < 100 
                ? "Add more detail for better results" 
                : `${jdText.length} characters · Good length`}
            </span>
            <button 
              onClick={handleSubmitText}
              disabled={jdText.length < 100 || submitState === "submitting"}
              style={{
                padding: "8px 20px",
                background: jdText.length >= 100 ? "#4F46E5" : "#E5E7EB",
                color: jdText.length >= 100 ? "white" : "#9CA3AF",
                borderRadius: "8px",
                border: "none",
                fontSize: "13px",
                fontWeight: 600,
                cursor: jdText.length >= 100 ? "pointer" : "not-allowed",
                transition: "all 0.2s",
                display: "flex",
                alignItems: "center",
                gap: "8px"
              }}
            >
              {submitState === "submitting" ? <Loader2 size={14} className="animate-spin" /> : "Save JD →"}
            </button>
          </div>
        </div>
      ) : (
        <label style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "160px",
          border: "2px dashed #E5E7EB",
          borderRadius: "10px",
          cursor: submitState === "submitting" ? "wait" : "pointer",
          background: "white",
          transition: "all 0.2s"
        }}>
          <FileText size={32} color="#9CA3AF" />
          <span style={{ fontSize: "14px", color: "#6B7280", marginTop: "12px" }}>
            {submitState === "submitting" ? "Processing..." : "Select job description file"}
          </span>
          <input 
            type="file" 
            style={{ display: "none" }} 
            onChange={handleFileChange}
            disabled={submitState === "submitting"}
            accept=".pdf,.docx"
          />
        </label>
      )}
    </div>
  );
}
