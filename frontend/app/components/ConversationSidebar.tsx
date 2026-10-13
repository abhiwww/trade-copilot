"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Plus, Search, MessageSquare, X, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { API_URL } from "@/app/lib/api-config";

export interface ConversationSummary {
  conversation_id: string;
  title: string;
  case_id: string | null;
  document_ids: string[];
  updated_at: string;
}

interface ConversationSidebarProps {
  activeConversationId: string | null;
  refreshKey: number;
  onSelect: (conversation: ConversationSummary) => void;
  onNewChat: () => void;
}

type Group = { label: string; items: ConversationSummary[] };

function groupConversations(items: ConversationSummary[]): Group[] {
  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfYesterday = new Date(startOfToday.getTime() - 86400000);
  const last7 = new Date(startOfToday.getTime() - 7 * 86400000);

  const groups: Record<string, ConversationSummary[]> = {
    Today: [],
    Yesterday: [],
    "Previous 7 days": [],
    Older: [],
  };

  for (const c of items) {
    const d = new Date(c.updated_at.replace(" ", "T"));
    if (d >= startOfToday) groups["Today"].push(c);
    else if (d >= startOfYesterday) groups["Yesterday"].push(c);
    else if (d >= last7) groups["Previous 7 days"].push(c);
    else groups["Older"].push(c);
  }

  return Object.entries(groups)
    .filter(([, list]) => list.length > 0)
    .map(([label, list]) => ({ label, items: list }));
}

export default function ConversationSidebar({
  activeConversationId,
  refreshKey,
  onSelect,
  onNewChat,
}: ConversationSidebarProps) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [collapsed, setCollapsed] = useState(false);

  const fetchConversations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/conversations/`, {
        credentials: "include",
      });
      if (response.ok) {
        setConversations(await response.json());
      } else if (response.status === 401) {
        setError("Your session has expired. Please sign in again.");
      } else {
        setError("Unable to load conversations.");
      }
    } catch {
      setError("Unable to connect to Trade Copilot.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations, refreshKey]);

  const filtered = query.trim()
    ? conversations.filter(
        (c) =>
          c.title.toLowerCase().includes(query.toLowerCase()) ||
          (c.case_id || "").toLowerCase().includes(query.toLowerCase())
      )
    : conversations;

  const groups = groupConversations(filtered);

  if (collapsed) {
    return (
      <button
        onClick={() => setCollapsed(false)}
        className="fixed left-4 top-28 z-30 w-10 h-10 rounded-full border border-[#E9E5DC] bg-white flex items-center justify-center text-[#806633] hover:bg-[#F5F0E6] transition-colors shadow-sm"
        aria-label="Show conversation history"
      >
        <PanelLeftOpen size={16} />
      </button>
    );
  }

  return (
    <aside className="w-72 shrink-0 border-r border-[#E9E5DC] bg-[#FBFAF7]/80 flex flex-col h-[calc(100vh-92px)] sticky top-[92px]">
      <div className="p-4 flex items-center justify-between">
        <button
          onClick={onNewChat}
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#A1844D] text-white text-sm font-medium hover:bg-[#806633] transition-all"
        >
          <Plus size={16} /> New Chat
        </button>
        <button
          onClick={() => setCollapsed(true)}
          className="p-2 rounded-full text-[#8B8A85] hover:bg-[#F5F0E6] transition-colors"
          aria-label="Hide conversation history"
        >
          <PanelLeftClose size={16} />
        </button>
      </div>

      <div className="px-4 pb-3">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search conversations..."
            className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-[#E9E5DC] bg-white outline-none focus:border-[#A1844D] transition-colors"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-4">
        {loading ? (
          <div className="p-4 text-center text-xs text-[#92928D]">Loading conversations...</div>
        ) : error ? (
          <div className="p-4 text-center text-xs text-[#8A3F31]">{error}</div>
        ) : groups.length === 0 ? (
          <div className="p-4 text-center text-xs text-[#92928D] italic">
            {query ? "No conversations match your search." : "No conversations yet."}
          </div>
        ) : (
          groups.map((group) => (
            <div key={group.label} className="mb-4">
              <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#92928D]">
                {group.label}
              </div>
              <div className="space-y-0.5">
                {group.items.map((c) => (
                  <button
                    key={c.conversation_id}
                    onClick={() => onSelect(c)}
                    className={`w-full text-left px-3 py-2.5 rounded-xl text-sm transition-all flex items-center gap-2 ${
                      activeConversationId === c.conversation_id
                        ? "bg-[#F5F0E6] text-[#171914] border border-[#D9CDB5]"
                        : "text-[#4F4E49] hover:bg-white border border-transparent"
                    }`}
                  >
                    <MessageSquare size={14} className={activeConversationId === c.conversation_id ? "text-[#A1844D]" : "text-slate-400"} />
                    <span className="truncate">{c.title}</span>
                  </button>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
