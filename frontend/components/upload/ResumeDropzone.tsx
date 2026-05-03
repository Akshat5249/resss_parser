"use client";

import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud } from "lucide-react";
import { toast } from "react-hot-toast";

interface ResumeDropzoneProps {
  onFileSelect: (file: File) => void;
}

export default function ResumeDropzone({ onFileSelect }: ResumeDropzoneProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Basic Validation
    const isDoc = file.name.toLowerCase().endsWith(".pdf") || file.name.toLowerCase().endsWith(".docx");
    const isSmall = file.size <= 10 * 1024 * 1024;

    if (!isDoc) {
      toast.error("Please upload a PDF or DOCX file");
      return;
    }
    if (!isSmall) {
      toast.error("File size must be under 10MB");
      return;
    }

    onFileSelect(file);
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    multiple: false
  });

  return (
    <div 
      {...getRootProps()} 
      style={{
        border: "2px dashed #D1D5DB",
        borderRadius: "12px",
        padding: "48px 24px",
        textAlign: "center",
        cursor: "pointer",
        transition: "all 0.2s",
        background: isDragActive ? "#EEF2FF" : "white",
        borderColor: isDragActive ? "#4F46E5" : "#D1D5DB"
      }}
      onMouseEnter={(e) => {
        if (!isDragActive) {
          e.currentTarget.style.borderColor = "#4F46E5";
          e.currentTarget.style.background = "#FAFAFE";
        }
      }}
      onMouseLeave={(e) => {
        if (!isDragActive) {
          e.currentTarget.style.borderColor = "#D1D5DB";
          e.currentTarget.style.background = "white";
        }
      }}
    >
      <input {...getInputProps()} />
      <UploadCloud size={40} color="#9CA3AF" style={{ margin: "0 auto" }} />
      <p style={{ fontSize: "15px", fontStyle: "normal", fontWeight: 500, color: "#374151", margin: "12px 0 4px" }}>
        Drop your resume here
      </p>
      <p style={{ fontSize: "13px", color: "#9CA3AF" }}>
        or <span style={{ color: "#4F46E5", fontWeight: 500 }}>browse files</span>
      </p>
      <p style={{ fontSize: "12px", color: "#C4C4C4", marginTop: "8px" }}>
        PDF or DOCX · Max 10MB
      </p>
    </div>
  );
}
