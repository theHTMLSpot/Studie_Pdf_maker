"use client";

import { data } from "autoprefixer";
import { useRef, useState } from "react";
import useSWRMutation from "swr/mutation";

interface StudyPlan {
  title: string;
  notes: string[];
  key_concepts: string[];
  study_recommendations: string[];
  estimated_study_hours: number;
  download_url: string;
}

interface PdfUploaderProps {
  onUpload: (file: File) => void;
  loading: boolean;
}

function PdfUploader({ onUpload, loading }: PdfUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files[0]?.type === "application/pdf") {
      onUpload(e.dataTransfer.files[0]);
    } else alert("Please upload a PDF file");
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`relative rounded-lg border-2 border-dashed p-8 text-center cursor-pointer transition-all ${
        dragActive
          ? "border-indigo-500 bg-indigo-50"
          : "border-gray-300 bg-white hover:border-gray-400"
      } ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        onChange={(e) => e.target.files && onUpload(e.target.files[0])}
        className="hidden"
        disabled={loading}
      />
      <div className="space-y-4">
        <div className="text-5xl">📄</div>
        <p className="font-semibold text-gray-900">Drop your PDF here</p>
        <p className="text-sm text-gray-500 mt-1">or click to browse</p>
        <p className="text-xs text-gray-400">PDF files only</p>
      </div>
      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-50 rounded-lg flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      )}
    </div>
  );
}

type TabType = "notes" | "concepts" | "recommendations";

function StudyPlanDisplay({ plan }: { plan: StudyPlan }) {
  const [activeTab, setActiveTab] = useState<TabType>("notes");

  const handleDownload = async () => {
    const res = await fetch(plan.download_url);
    const blob = await res.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = plan.title;
    link.click();
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900">{plan.title}</h2>
        <div className="mt-4 flex items-center space-x-4">
          <div className="bg-indigo-100 rounded-lg px-4 py-2">
            <p className="text-sm text-gray-600">Estimated Study Time</p>
            <p className="text-2xl font-bold text-indigo-600">
              {plan.estimated_study_hours}h
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200 flex">
          {["notes", "concepts", "recommendations"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as TabType)}
              className={`flex-1 px-6 py-4 font-semibold text-center transition-colors ${
                activeTab === tab
                  ? "text-indigo-600 border-b-2 border-indigo-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {tab === "notes"
                ? `📝 Notes (${plan.notes.length})`
                : tab === "concepts"
                  ? `🎯 Key Concepts (${plan.key_concepts.length})`
                  : `💡 Study Tips`}
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === "notes" &&
            plan.notes.map((note, i) => (
              <div
                key={i}
                className="bg-gray-50 rounded-lg p-4 border border-gray-200 mb-2"
              >
                {note}
              </div>
            ))}
          {activeTab === "concepts" && (
            <div className="grid grid-cols-2 gap-3">
              {plan.key_concepts.map((c, i) => (
                <div
                  key={i}
                  className="bg-indigo-50 border border-indigo-200 rounded-lg px-4 py-3"
                >
                  {c}
                </div>
              ))}
            </div>
          )}
          {activeTab === "recommendations" &&
            plan.study_recommendations.map((r, i) => (
              <div
                key={i}
                className="flex items-start space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg m-2"
              >
                <span className="text-xl">✓</span>
                <p>{r}</p>
              </div>
            ))}
        </div>
      </div>

      <button
        onClick={handleDownload}
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg transition-colors"
      >
        📥 Download PDF
      </button>
    </div>
  );
}

// -------------------------
// MAIN PAGE
// -------------------------
export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const { trigger, data, isMutating, error } = useSWRMutation(
    "/api/upload-pdf",
    async (_url, { arg }: { arg: File }) => {
      const form = new FormData();
      form.append("file", arg);
      const res = await fetch("http://localhost:8000/upload-pdf", {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error("Upload failed");
      return res.json();
    },
  );

  const handleUpload = (f: File) => {
    setFile(f);
    trigger(f);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <h1 className="text-4xl font-bold mb-4">📚 Study Planner</h1>
      <p className="text-gray-600 mb-8">
        Transform your PDFs into organized study materials
      </p>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <PdfUploader onUpload={handleUpload} loading={isMutating} />
        </div>

        <div className="lg:col-span-2">
          {isMutating ? (
            <p>Processing your PDF...</p>
          ) : data ? (
            <StudyPlanDisplay plan={data} />
          ) : (
            <p>Upload a PDF to get started</p>
          )}
        </div>
      </div>
    </main>
  );
}
