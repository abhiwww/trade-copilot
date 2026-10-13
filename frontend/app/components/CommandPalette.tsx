"use client";

import React, { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, X, Command, Zap, FileText, Globe, ShieldAlert } from "lucide-react";

interface CommandPaletteProps {
  onAction: (action: string) => void;
}

const ACTIONS = [
  { id: "new-case", label: "New Trade Analysis", icon: Zap, category: "Actions", shortcut: "N" },
  { id: "export-report", label: "Export Intelligence Report", icon: FileText, category: "Actions", shortcut: "E" },
  { id: "jump-risk", label: "Jump to Risk Pulse", icon: ShieldAlert, category: "Navigation", shortcut: "R" },
  { id: "jump-evidence", label: "Open Evidence Vault", icon: Globe, category: "Navigation", shortcut: "V" },
  { id: "clear-case", label: "Clear Current Case", icon: X, category: "System", shortcut: "C" },
];

export default function CommandPalette({ onAction }: CommandPaletteProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");

  const togglePalette = useCallback(() => setIsOpen((prev) => !prev), []);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        togglePalette();
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [togglePalette]);

  const filteredActions = ACTIONS.filter((a) =>
    a.label.toLowerCase().includes(query.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-32 px-4 pointer-events-none">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: -20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -20 }}
        className="w-full max-w-xl pointer-events-auto"
      >
        <div className="glass-card p-2 shadow-2xl border-white/20 ring-1 ring-white/10">
          <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
            <Search size={20} className="text-primary" />
            <input
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type a command or search..."
              className="w-full bg-transparent outline-none text-lg font-light placeholder:text-slate-500"
            />
            <div className="flex items-center gap-1 px-2 py-1 rounded bg-slate-800 text-[10px] text-slate-400 font-mono">
              <Command size={10} /> K
            </div>
          </div>

          <div className="max-h-[400px] overflow-y-auto p-2 space-y-4">
            {filteredActions.length === 0 && (
              <div className="p-4 text-center text-slate-500 text-sm">No matching commands found.</div>
            )}

            <div className="py-2">
              {filteredActions.map((action) => (
                <button
                  key={action.id}
                  onClick={() => {
                    onAction(action.id);
                    setIsOpen(false);
                  }}
                  className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-primary/20 hover:text-primary transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <action.icon size={18} className="text-slate-400 group-hover:text-primary" />
                    <span className="text-sm font-medium">{action.label}</span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 group-hover:text-primary/50">{action.shortcut}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/40 backdrop-blur-sm -z-10 pointer-events-auto"
        onClick={() => setIsOpen(false)}
      />
    </div>
  );
}
