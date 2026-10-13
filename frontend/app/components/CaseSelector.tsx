"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Globe, ChevronDown, X } from "lucide-react";
import { API_URL } from "@/app/lib/api-config";
import CreateCaseModal from "./CreateCaseModal";


interface TradeCase {
  case_id: string;
  name: string;
  origin: { country: string; state?: string; city?: string; port?: string };
  destination: { country: string; state?: string; city?: string; port?: string };
  product: string;
  status: string;
}

interface CaseSelectorProps {
  selectedCase: TradeCase | null;
  onSelect: (caseObj: TradeCase) => void;
}

export default function CaseSelector({ selectedCase, onSelect }: CaseSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [cases, setCases] = useState<TradeCase[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function fetchCases() {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/cases/`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setCases(data);
      }
    } catch (error) {
      console.error("Error fetching cases:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (isOpen) fetchCases();
  }, [isOpen]);

  const filteredCases = cases.filter(c =>
    c.name.toLowerCase().includes(query.toLowerCase()) ||
    c.case_id.toLowerCase().includes(query.toLowerCase()) ||
    c.product.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="relative" ref={containerRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium hover:text-[#806633] transition-colors"
      >
        <Globe size={16} className="text-[#806633]" />
        <span className="truncate max-w-[150px]">
          {selectedCase ? selectedCase.name : "Select Trade Case"}
        </span>
        <ChevronDown size={14} className={`transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute bottom-full mb-3 left-0 w-80 glass-card bg-white border border-[#E9E5DC] shadow-2xl z-50 overflow-hidden"
          >
            <div className="p-3 border-b border-[#E9E5DC] bg-[#F8F6F1]">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search cases..."
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-[#E9E5DC] outline-none focus:border-[#A1844D] transition-colors"
                />
              </div>
            </div>

            <div className="max-h-60 overflow-y-auto p-2">
              {loading ? (
                <div className="p-4 text-center text-xs text-slate-500">Loading cases...</div>
              ) : filteredCases.length > 0 ? (
                <div className="space-y-1">
                  {filteredCases.map(c => (
                    <button
                      key={c.case_id}
                      onClick={() => {
                        onSelect(c);
                        setIsOpen(false);
                      }}
                      className={`w-full text-left p-3 rounded-xl transition-all group ${
                        selectedCase?.case_id === c.case_id ? "bg-[#F5F0E6] border-[#A1844D]" : "hover:bg-[#FBFBFB]"
                      } border border-transparent`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-xs font-bold text-[#171914]">{c.name}</span>
                        <span className="text-[10px] font-mono text-slate-400">{c.case_id}</span>
                      </div>
                      <div className="text-[11px] text-[#777771] flex items-center gap-1">
                        <Globe size={10} /> {c.origin.country} → {c.destination.country}
                      </div>
                      <div className="text-[11px] text-[#8B8A85] mt-1">{c.product}</div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-500 italic">
                  {query ? "No cases match your search." : "No trade cases found."}
                </div>
              )}
            </div>

            {cases.length === 0 && !loading && (
              <div className="p-3 border-t border-[#E9E5DC] bg-slate-50 text-center">
                <button
                  className="text-[11px] font-medium text-[#A1844D] hover:underline"
                  onClick={() => setIsCreateModalOpen(true)}
                >
                  + Create New Trade Case
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <CreateCaseModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreate={(newCase) => {
          onSelect(newCase);
          setIsOpen(false);
        }}
      />
    </div>
  );
}
