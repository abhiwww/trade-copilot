"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Search, HelpCircle } from "lucide-react";

interface HelpOption {
  title: string;
  category: string;
  description: string;
}

const HELP_OPTIONS: HelpOption[] = [
  { title: "Getting Started", category: "Onboarding", description: "Learn how to set up your first trade case and upload documents." },
  { title: "Uploading Documents", category: "Documents", description: "Supported formats, size limits, and processing times." },
  { title: "Trade Cases", category: "Management", description: "How to organize and track your international shipments." },
  { title: "Document Analysis", category: "Intelligence", description: "Understanding the AI extraction and classification process." },
  { title: "Compliance", category: "Intelligence", description: "How we check against global trade regulations." },
  { title: "Sanctions", category: "Intelligence", description: "Screening parties and destinations against global watchlists." },
  { title: "Reports", category: "Output", description: "Generating professional trade intelligence reports." },
];

export default function HelpPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");

  const filteredOptions = HELP_OPTIONS.filter(opt =>
    opt.title.toLowerCase().includes(query.toLowerCase()) ||
    opt.description.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="w-10 h-10 rounded-full border border-transparent hover:bg-[#f7f4ee] flex items-center justify-center text-xl transition-colors"
      >
        ?
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <div
              className="fixed inset-0 z-40 bg-black/10 backdrop-blur-sm"
              onClick={() => setIsOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="fixed top-20 right-12 w-96 glass-card bg-white border border-[#E9E5DC] shadow-2xl z-50 overflow-hidden"
            >
              <div className="p-4 border-b border-[#E9E5DC] flex justify-between items-center bg-[#F8F6F1]">
                <div className="flex items-center gap-2">
                  <HelpCircle size={18} className="text-[#A1844D]" />
                  <h3 className="font-serif text-lg font-medium">How can we help?</h3>
                </div>
                <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-slate-200 rounded-full transition-colors">
                  <X size={16} />
                </button>
              </div>

              <div className="p-4">
                <div className="relative mb-4">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search help center..."
                    className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-[#E9E5DC] outline-none focus:border-[#A1844D] transition-colors"
                  />
                </div>

                <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
                  {filteredOptions.map((opt, idx) => (
                    <button
                      key={idx}
                      className="w-full text-left p-3 rounded-xl border border-transparent hover:border-[#E9E5DC] hover:bg-[#FBFBFB] transition-all group"
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-xs font-bold text-[#171914] group-hover:text-[#A1844D] transition-colors">{opt.title}</span>
                        <span className="text-[9px] uppercase font-bold text-slate-400">{opt.category}</span>
                      </div>
                      <p className="text-[11px] text-[#777771] leading-relaxed">{opt.description}</p>
                    </button>
                  ))}
                  {filteredOptions.length === 0 && (
                    <div className="text-center py-8 text-xs text-slate-400 italic">
                      No matching help articles found.
                    </div>
                  )}
                </div>
              </div>

              <div className="p-4 border-t border-[#E9E5DC] bg-slate-50 flex justify-between items-center">
                <span className="text-[11px] text-slate-500">Need more help?</span>
                <button className="text-[11px] font-bold text-[#A1844D] hover:underline">Contact Support</button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
