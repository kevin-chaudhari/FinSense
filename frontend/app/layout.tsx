import type { Metadata, Viewport } from "next"
import { Inter, Outfit } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" })

export const metadata: Metadata = {
  title: {
    default: "FinSense AI — Intelligent Personal Finance",
    template: "%s | FinSense AI",
  },
  description:
    "FinSense AI is a production-grade AI-powered personal finance platform. Track expenses, get AI-driven insights, and visualize your financial data with LangGraph agents and FAISS vector search.",
  keywords: [
    "personal finance",
    "AI finance",
    "expense tracker",
    "budget assistant",
    "financial AI",
    "LangGraph",
    "Gemini AI",
  ],
  authors: [{ name: "Kevinkumar Chaudhari" }],
  openGraph: {
    title: "FinSense AI",
    description: "AI-Powered Personal Finance Platform",
    type: "website",
  },
}

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#6366f1" },
    { media: "(prefers-color-scheme: dark)", color: "#4f46e5" },
  ],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${outfit.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  )
}
