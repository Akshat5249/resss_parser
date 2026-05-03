import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ATS Resume Scanner",
  description: "AI-powered ATS Resume Scanner and Optimizer",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Toaster position="top-right" />
        <nav style={{
          position: "sticky", 
          top: 0, 
          zIndex: 50,
          background: "rgba(255,255,255,0.8)",
          backdropFilter: "blur(12px)",
          borderBottom: "1px solid #F0F0F0",
          height: "56px",
          display: "flex", 
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px"
        }}>
          <Link href="/" style={{ textDecoration: "none" }}>
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{
                background: "#4F46E5",
                color: "white",
                borderRadius: "6px",
                padding: "2px 6px",
                fontSize: "12px",
                fontWeight: 700,
                letterSpacing: "0.5px"
              }}>ATS</span>
              <span style={{
                fontSize: "15px",
                fontWeight: 600,
                color: "#0A0A0A"
              }}>Scanner</span>
            </span>
          </Link>

          <div style={{ display: "flex", gap: "24px", alignItems: "center" }}>
            <Link href="/" style={{
              fontSize: "14px",
              color: "#6B7280",
              textDecoration: "none",
              fontWeight: 500
            }}>Scan Resume</Link>
            <Link href="/rank" style={{
              fontSize: "14px",
              color: "#6B7280",
              textDecoration: "none",
              fontWeight: 500
            }}>Compare Resumes</Link>
            <a 
              href="https://github.com" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{
                fontSize: "13px",
                color: "white",
                background: "#0A0A0A",
                padding: "6px 14px",
                borderRadius: "8px",
                textDecoration: "none",
                fontWeight: 500
              }}
            >
              GitHub ↗
            </a>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
