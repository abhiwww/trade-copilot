import React from "react";
import { motion } from "framer-motion";

export default function MessageBubble({
  message,
  onViewEvidence
}: {
  message: { role: string; content: string; findings?: any[] };
  onViewEvidence: (docId: string, field: string) => void;
}) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      {isUser ? (
        <div className="max-w-[85%] px-5 py-3 rounded-2xl bg-[#A1844D] text-white text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>
      ) : (
        <div className="max-w-[85%] space-y-4">
          <div className="px-5 py-4 rounded-2xl bg-white border border-[#E9E5DC] shadow-sm text-sm leading-relaxed text-[#171914] whitespace-pre-wrap">
            {message.content}
          </div>
          {(message.findings ?? []).map((finding: any, fIdx: number) => (
            <div key={fIdx} className="p-5 rounded-2xl border border-[#E9E5DC] bg-[#FFFEFD] shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                  finding.severity === 'high' ? 'bg-[#D85C55] text-white' : 'bg-[#A1844D] text-white'
                }`}>
                  {finding.severity}
                </span>
                <span className="text-sm font-bold">{finding.title}</span>
              </div>
              <p className="text-[#777771] leading-relaxed text-sm">{finding.description}</p>
              <button
                onClick={() => onViewEvidence("unknown", finding.title)}
                className="mt-3 text-xs font-medium text-[#A1844D] hover:underline flex items-center gap-1"
              >
                View Evidence
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
