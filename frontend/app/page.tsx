"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Paperclip,
  Globe,
  HelpCircle,
  Bell,
  ChevronDown,
  Search,
  Zap,
  FileText,
  ShieldAlert,
  X,
  CheckCircle2,
  RefreshCw,
  User,
  Building,
  Settings,
  LogOut,
  Shield
} from "lucide-react";
import CommandPalette from "./components/CommandPalette";
import ConversationSidebar, { ConversationSummary } from "./components/ConversationSidebar";
import CaseSelector from "./components/CaseSelector";
import GeographySelector from "./components/GeographySelector";
import HelpPanel from "./components/HelpPanel";
import NotificationPanel from "./components/NotificationPanel";
import EvidenceViewer from "./components/EvidenceViewer";
import AuthGuard from "./components/AuthGuard";
import { getUserDisplayName, getUserInitials, useAuth } from "@/app/context/AuthContext";
import { API_URL } from "@/app/lib/api-config";
import { useRouter } from "next/navigation";

import Header from "@/components/layout/header";
import { Button, Badge } from "@/components/ui/atomic";
import MessageBubble from "@/components/features/chat/message-bubble";
import FileUploadBadge from "@/components/features/docs/file-uploader";

interface Finding {
  title: string;
  description: string;
  severity: string;
}

interface UploadedFile {
  id: string;
  filename: string;
  status: "Uploading" | "Processing" | "Processed" | "Failed";
  size: string;
}

interface TradeCase {
  case_id: string;
  name: string;
  origin: { country: string; state?: string; city?: string; port?: string };
  destination: { country: string; state?: string; city?: string; port?: string };
  product: string;
  status: string;
}

export default function HomePage() {
  const { user, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Array<{ role: string; content: string; findings?: any[] }>>([]);
  const [convosRefreshKey, setConvosRefreshKey] = useState(0);
  const [loading, setLoading] = useState(false);
  const [thoughtTrace, setThoughtTrace] = useState<string[]>([]);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedCase, setSelectedCase] = useState<TradeCase | null>(null);
  const [viewingEvidence, setViewingEvidence] = useState<{ docId: string; field: string } | null>(null);
  const [route, setRoute] = useState({
    origin: { country: "India", state: "Karnataka", city: "Bengaluru", port: "Bengaluru International Airport" },
    destination: { country: "United States", state: "California", city: "Los Angeles", port: "Los Angeles" }
  });
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);
  const profileTriggerRef = useRef<HTMLButtonElement>(null);
  const submittingRef = useRef(false);
  const composerRef = useRef<HTMLTextAreaElement>(null);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function fetchHealth() {
      try {
        await fetch(`${API_URL}/api/v1/health`);
      } catch (error) {
        console.warn("Backend not reachable yet.");
      }
    }
    fetchHealth();
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node) &&
          profileTriggerRef.current && !profileTriggerRef.current.contains(event.target as Node)) {
        setProfileMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && profileMenuOpen) {
        setProfileMenuOpen(false);
        profileTriggerRef.current?.focus();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [profileMenuOpen]);

  const handleSignOut = useCallback(async () => {
    await logout();
    router.push("/login");
  }, [logout, router]);

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files) return;

    if (!selectedCase) {
      setStatusMessage("Select or create a trade case before attaching documents.");
      e.target.value = "";
      return;
    }

    for (const file of Array.from(files)) {
      const fileId = Math.random().toString(36).substring(7);
      setUploadedFiles(prev => [...prev, {
        id: fileId,
        filename: file.name,
        status: "Uploading",
        size: (file.size / 1024).toFixed(1) + " KB"
      }]);

      const formData = new FormData();
      formData.append("file", file);
      formData.append("case_id", selectedCase.case_id);

      try {
        const response = await fetch(`${API_URL}/api/v1/documents/upload`, {
          method: "POST",
          body: formData,
          credentials: "include",
        });

        if (response.ok) {
          const data = await response.json();
          setUploadedFiles(prev => prev.map(f =>
            f.filename === file.name ? { ...f, id: data.document_id, status: "Processing" } : f
          ));

          const pollInterval = setInterval(async () => {
            const statusRes = await fetch(`${API_URL}/api/v1/documents/${data.document_id}`, {
              credentials: "include",
            });
            if (statusRes.ok) {
              const statusData = await statusRes.json();
              if (statusData.status === "Processed") {
                setUploadedFiles(prev => prev.map(f =>
                  f.id === data.document_id ? { ...f, status: "Processed" } : f
                ));
                clearInterval(pollInterval);
              } else if (statusData.status === "Failed") {
                setUploadedFiles(prev => prev.map(f =>
                  f.id === data.document_id ? { ...f, status: "Failed" } : f
                ));
                clearInterval(pollInterval);
              }
            } else {
              setUploadedFiles(prev => prev.map(f =>
                f.id === data.document_id ? { ...f, status: "Failed" } : f
              ));
              clearInterval(pollInterval);
            }
          }, 3000);
        } else {
          const errorData = await response.json().catch(() => ({}));
          setStatusMessage(errorData.detail || "Document upload failed.");
          setUploadedFiles(prev => prev.map(f =>
            f.filename === file.name ? { ...f, status: "Failed" } : f
          ));
        }
      } catch (error) {
        setStatusMessage("Unable to upload the selected document.");
        setUploadedFiles(prev => prev.map(f =>
          f.filename === file.name ? { ...f, status: "Failed" } : f
        ));
      }
    }
    e.target.value = "";
  }

  function removeFile(id: string) {
    setUploadedFiles(prev => prev.filter(f => f.id !== id));
  }

  async function handleSubmit() {
    if (submittingRef.current) return;

    const submittedMessage = message.trim();
    const usableDocumentIds = uploadedFiles
      .filter((file) => file.status === "Processing" || file.status === "Processed")
      .map((file) => file.id);
    const hasPendingUploads = uploadedFiles.some((file) => file.status === "Uploading");

    if (hasPendingUploads) {
      setStatusMessage("Please wait for uploads to finish before sending.");
      return;
    }

    if (!submittedMessage && usableDocumentIds.length === 0) {
      setStatusMessage("Enter a message or attach a processed document.");
      return;
    }

    submittingRef.current = true;
    setStatusMessage(null);
    setLoading(true);
    setThoughtTrace([]);
    setMessages(prev => [...prev, { role: "user", content: submittedMessage }]);

    try {
      const response = await fetch(`${API_URL}/api/v1/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          message: submittedMessage,
          case_id: selectedCase?.case_id ?? null,
          conversation_id: conversationId,
          document_ids: usableDocumentIds,
          country_pair: `${route.origin.country}->${route.destination.country}`,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          await logout();
          router.push("/login");
          return;
        }
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed: ${response.status}`);
      }

      if (!response.body) throw new Error("Response body is null");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "").trim();
            try {
              const data = JSON.parse(dataStr);
              if (data.event === "status") {
                setThoughtTrace(prev => [...prev, data.message]);
              } else if (data.event === "final") {
                if (data.data.conversation_id) setConversationId(data.data.conversation_id);
                setMessages(prev => [...prev, {
                  role: "assistant",
                  content: data.data.answer ?? data.data.summary ?? "Trade Copilot could not generate a response.",
                  findings: data.data.findings ?? [],
                }]);
                setConvosRefreshKey(k => k + 1);
                setMessage("");
              }
            } catch (e) {
              console.error("Error parsing SSE data:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Error submitting analysis:", error);
      setStatusMessage(error instanceof Error ? error.message : "Trade Copilot could not process this request.");
    } finally {
      submittingRef.current = false;
      setLoading(false);
    }
  }

  async function handleNewChat() {
    setConversationId(null);
    setMessages([]);
    setUploadedFiles([]);
    setMessage("");
    setStatusMessage(null);
    setTimeout(() => composerRef.current?.focus(), 100);
  }

  async function handleOpenConversation(convo: ConversationSummary) {
    setStatusMessage(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/conversations/${convo.conversation_id}`, {
        credentials: "include",
      });
      if (!response.ok) {
        setStatusMessage("Unable to open that conversation.");
        return;
      }
      const data = await response.json();
      setConversationId(data.conversation_id);
      setMessages(data.messages.map((m: any) => ({ role: m.role, content: m.content, findings: m.findings })));
      setSelectedCase(data.case_id ? { case_id: data.case_id, name: data.case_id, origin: { country: "" }, destination: { country: "" }, product: "", status: "" } : null);
      setUploadedFiles([]);
      setTimeout(() => endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" }), 150);
    } catch {
      setStatusMessage("Unable to connect to Trade Copilot.");
    }
}

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const displayName = authLoading ? "Loading..." : getUserDisplayName(user);
  const displayInitials = authLoading ? "..." : getUserInitials(user);

  return (
    <AuthGuard>
      <main className="min-h-screen bg-[#FBFAF7] text-[#171914] font-sans selection:bg-[#A1844D]/20">
        <CommandPalette onAction={(action) => console.log("Executing action:", action)} />

        <Header
          user={user}
          logout={handleSignOut}
          route={route}
          onRouteChange={setRoute}
          GeographySelector={GeographySelector}
          HelpPanel={HelpPanel}
          NotificationPanel={NotificationPanel}
        />

        <div className="flex">
          <ConversationSidebar
            activeConversationId={conversationId}
            refreshKey={convosRefreshKey}
            onSelect={handleOpenConversation}
            onNewChat={handleNewChat}
          />

          <div className="flex-1 min-w-0">
            {!messages.length && !loading ? (
              <div className="max-w-[1200px] mx-auto px-4 md:px-6">
                <section className="min-h-[calc(100vh-92px)] pt-[140px] pb-20 relative flex flex-col items-center">

                  <motion.h1
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center font-serif text-5xl md:text-6xl font-medium text-[#171914] tracking-tight mb-5"
                  >
                    Your Trade Intelligence Partner
                  </motion.h1>
                  <motion.p
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-center text-[#777771] text-lg mb-14 max-w-2xl"
                  >
                    Ask a question, upload your trade documents, or analyze a transaction.
                  </motion.p>

                  <div className="w-full max-w-[960px] min-h-[170px] border border-[#E9E5DC] rounded-[24px] bg-[#FFFEFD] shadow-[0_12px_35px_rgba(60,50,30,0.045)] p-6 flex flex-col">
                    <textarea
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Ask Trade Copilot anything..."
                      rows={3}
                      className="w-full bg-transparent border-none outline-none resize-none text-lg text-[#171914] placeholder:text-[#92928D]"
                    />

                    <AnimatePresence>
                      {uploadedFiles.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-4 overflow-hidden">
                          {uploadedFiles.map(file => (
                            <FileUploadBadge key={file.id} file={file} onRemove={removeFile} />
                          ))}
                        </div>
                      )}
                    </AnimatePresence>

                    <AnimatePresence>
                      {statusMessage && (
                        <Badge variant="warning" className="mb-4 w-full">
                          {statusMessage}
                        </Badge>
                      )}
                    </AnimatePresence>

                    <AnimatePresence>
                      {loading && (
                        <div className="flex flex-col gap-2 mb-6 py-4 border-y border-[#E9E5DC]/50">
                          <div className="flex items-center gap-2 text-[10px] font-bold uppercase text-[#A1844D] mb-2 tracking-widest">
                            <Zap size={12} className="animate-pulse" />
                            AI Analysis in Progress
                          </div>
                          <div className="space-y-2">
                            {thoughtTrace.map((step, i) => (
                              <motion.div
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.1 }}
                                key={i}
                                className="flex items-center gap-3 text-sm text-[#5C5B56]"
                              >
                              <div className="w-1.5 h-1.5 rounded-full bg-[#A1844D]" />
                              {step}
                              </motion.div>
                            ))}
                            <div className="flex items-center gap-3 text-sm text-[#A1844D] animate-pulse">
                              <div className="w-1.5 h-1.5 rounded-full bg-[#A1844D]" />
                              Thinking...
                            </div>
                          </div>
                        </div>
                      )}
                    </AnimatePresence>

                    <div className="flex justify-between items-center mt-auto">
                      <div className="flex items-center gap-4">
                        <label className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#F8F6F1] text-sm font-medium cursor-pointer hover:bg-[#F5F0E6] transition-colors">
                          <Paperclip size={16} className="text-[#806633]" />
                          <span>Attach Files</span>
                          <input type="file" multiple hidden onChange={handleFileUpload} />
                        </label>
                        <div className="w-px h-6 bg-[#E9E5DC]" />
                        <CaseSelector
                          selectedCase={selectedCase}
                          onSelect={(c) => {
                            setSelectedCase(c);
                            setStatusMessage(null);
                            setRoute({
                              origin: {
                                country: c.origin.country || route.origin.country,
                                state: c.origin.state || "",
                                city: c.origin.city || "",
                                port: c.origin.port || "",
                              },
                              destination: {
                                country: c.destination.country || route.destination.country,
                                state: c.destination.state || "",
                                city: c.destination.city || "",
                                port: c.destination.port || "",
                              },
                            });
                          }}
                        />
                      </div>
                      <Button
                        variant="primary"
                        className="w-14 h-14 rounded-full flex items-center justify-center text-2xl"
                        onClick={handleSubmit}
                        disabled={loading || uploadedFiles.some(file => file.status === "Uploading")}
                      >
                        {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : "➤"}
                      </Button>
                    </div>
                  </div>

                  <div className="flex flex-wrap justify-center gap-3 mt-12">
                    {[
                      "Analyze this shipment for compliance",
                      "What documents are required for India to USA?",
                      "Check this LC for discrepancies",
                      "Classify this product's HS code"
                    ].map((promptText, idx) => (
                      <Button key={idx} variant="secondary" className="px-5 py-2.5 text-sm">
                        <span className="text-[#8066] mr-2">▣</span> {promptText}
                      </Button>
                    ))}
                  </div>
                </section>
              </div>
            ) : (
              <div className="max-w-3xl mx-auto px-4 md:px-6 pb-44 pt-12">
                <div className="space-y-6">
                  {messages.map((m, idx) => (
                    <MessageBubble
                      key={idx}
                      message={m}
                      onViewEvidence={(docId, field) => setViewingEvidence({ docId, field })}
                    />
                  ))}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="px-5 py-4 rounded-2xl bg-white border border-[#E9E5DC] shadow-sm text-sm text-[#A1844D] flex items-center gap-2">
                        <div className="w-3.5 h-3.5 border-2 border-[#A1844D]/30 border-t-[#A1844D] rounded-full animate-spin" />
                        Trade Copilot is reviewing...
                      </div>
                    </div>
                  )}
                  <div ref={endOfMessagesRef} />
                </div>

                <div className="fixed bottom-8 left-0 sm:left-72 right-0 px-4 md:px-6 flex justify-center pointer-events-none">
                  <div className="w-full max-w-2xl pointer-events-auto">
                    <AnimatePresence>
                      {statusMessage && (
                        <Badge variant="warning" className="mb-2 w-full">
                          {statusMessage}
                        </Badge>
                      )}
                    </AnimatePresence>
                    <div className="p-3 rounded-[24px] bg-white border border-[#E9E5DC] shadow-[0_12px_35px_rgba(60,50,30,0.08)]">
                      <textarea
                        ref={composerRef}
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            handleSubmit();
                          }
                        }}
                        placeholder="Ask a follow-up question..."
                        rows={2}
                        className="w-full bg-transparent border-none outline-none resize-none text-sm text-[#171914] placeholder:text-[#92928D]"
                      />
                      <div className="flex justify-between items-center mt-1">
                        <div className="flex items-center gap-3">
                          <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#F8F6F1] text-xs font-medium cursor-pointer hover:bg-[#F5F0E6] transition-colors">
                          <Paperclip size={14} className="text-[#806633]" />
                          <span className="text-xs">Attach</span>
                          <input type="file" multiple hidden onChange={handleFileUpload} />
                        </label>
                        <CaseSelector
                          selectedCase={selectedCase}
                          onSelect={(c) => {
                            setSelectedCase(c);
                            setStatusMessage(null);
                          }}
                        />
                      </div>
                      <Button
                        variant="primary"
                        className="w-10 h-10 rounded-full flex items-center justify-center"
                        onClick={handleSubmit}
                        disabled={loading || uploadedFiles.some(file => file.status === "Uploading")}
                      >
                        {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : "➤"}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            )}
          </div>
        </div>
      </main>
    </AuthGuard>
  );
}
