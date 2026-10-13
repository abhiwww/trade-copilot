"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Bell, FileText, ShieldAlert, CheckCircle2 } from "lucide-react";

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  severity: "info" | "warning" | "critical";
  time: string;
  isRead: boolean;
}

const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: "1",
    type: "FINDING_CREATED",
    title: "High-risk finding detected",
    message: "TC-2026-001: Quantity mismatch found in Commercial Invoice.",
    severity: "critical",
    time: "5 min ago",
    isRead: false
  },
  {
    id: "2",
    type: "DOCUMENT_PROCESSED",
    title: "Document processing completed",
    message: "commercial_invoice.pdf has been successfully parsed.",
    severity: "info",
    time: "12 min ago",
    isRead: true
  },
  {
    id: "3",
    type: "SANCTIONS_REVIEW",
    title: "Review required",
    message: "Sanctions screening requires manual review for Destination: UAE.",
    severity: "warning",
    time: "1 hour ago",
    isRead: false
  }
];

export default function NotificationPanel() {
  const [isOpen, setIsOpen] = useState(false);
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

  const unreadCount = MOCK_NOTIFICATIONS.filter(n => !n.isRead).length;

  return (
    <div className="relative" ref={containerRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-10 h-10 rounded-full border border-transparent hover:bg-[#f7f4ee] flex items-center justify-center text-xl relative transition-colors"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <div className="absolute top-2 right-2 w-1.5 h-1.5 bg-[#D85C55] border-2 border-white rounded-full" />
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            className="absolute top-full right-0 mt-3 w-80 glass-card bg-white border border-[#E9E5DC] shadow-2xl z-50 overflow-hidden"
          >
            <div className="p-4 border-b border-[#E9E5DC] flex justify-between items-center bg-[#F8F6F1]">
              <div className="flex items-center gap-2">
                <Bell size={18} className="text-[#A1844D]" />
                <h3 className="font-serif text-lg font-medium">Notifications</h3>
              </div>
              <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-slate-200 rounded-full transition-colors">
                <X size={16} />
              </button>
            </div>

            <div className="max-h-96 overflow-y-auto">
              {MOCK_NOTIFICATIONS.length > 0 ? (
                <div className="divide-y divide-[#E9E5DC]">
                  {MOCK_NOTIFICATIONS.map((n) => (
                    <div
                      key={n.id}
                      className={`p-4 hover:bg-[#FBFBFB] cursor-pointer transition-colors ${!n.isRead ? "bg-blue-50/30" : ""}`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className={`text-xs font-bold ${
                          n.severity === 'critical' ? 'text-rose-600' :
                          n.severity === 'warning' ? 'text-amber-600' : 'text-slate-600'
                        }`}>
                          {n.title}
                        </span>
                        <span className="text-[10px] text-slate-400">{n.time}</span>
                      </div>
                      <p className="text-xs text-[#777771] leading-relaxed">{n.message}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-400 italic">
                  No notifications yet.
                </div>
              )}
            </div>

            <div className="p-3 border-t border-[#E9E5DC] text-center">
              <button className="text-[11px] font-bold text-[#A1844D] hover:underline">
                View all notifications
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
