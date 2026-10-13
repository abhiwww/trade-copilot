"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, FileText, ZoomIn, ExternalLink } from "lucide-react";
import { API_URL } from "@/app/lib/api-config";
import * as pdfjs from "pdfjs-dist";

// Initialize PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface EvidenceViewerProps {
  documentId: string;
  fieldName: string;
  onClose: () => void;
}

export default function EvidenceViewer({ documentId, fieldName, onClose }: EvidenceViewerProps) {
  const [evidence, setEvidence] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function fetchEvidence() {
      try {
        const response = await fetch(`${API_URL}/api/v1/documents/${documentId}/evidence/${fieldName}`, {
          credentials: "include",
        });
        if (response.ok) {
          const data = await response.json();
          setEvidence(data);
        }
      } catch (error) {
        console.error("Error fetching evidence:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchEvidence();
  }, [documentId, fieldName]);

  useEffect(() => {
    async function renderPdf() {
      if (!canvasRef.current) return;

      try {
        const loadingTask = pdfjs.getDocument({
          url: `${API_URL}/api/v1/documents/${documentId}/file`,
          withCredentials: true,
        });
        const pdf = await loadingTask.promise;
        const page = await pdf.getPage(evidence?.page || 1);

        const viewport = page.getViewport({ scale: 1.5 });
        const canvas = canvasRef.current;
        const context = canvas.getContext("2d");

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
          canvas,
          canvasContext: context!,
          viewport: viewport,
        };
        await page.render(renderContext).promise;
      } catch (error) {
        console.error("Error rendering PDF:", error);
      }
    }

    if (!loading) {
      renderPdf();
    }
  }, [documentId, loading, evidence]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[60] flex items-center justify-center p-6 bg-black/60 backdrop-blur-md"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-[32px] w-full max-w-5xl h-[80vh] overflow-hidden shadow-2xl flex"
      >
        {/* Left Side: Real PDF Viewer */}
        <div className="flex-1 bg-[#E5E5E5] relative overflow-auto p-12 flex justify-center" ref={containerRef}>
          <div className="relative shadow-2xl">
            <canvas ref={canvasRef} />

            {/* Evidence Highlight Overlay */}
            {evidence && (
              <div
                className="absolute bg-yellow-200/60 border-2 border-yellow-400 pointer-events-none transition-all"
                style={{
                  left: `${evidence.bbox[0]}px`,
                  top: `${evidence.bbox[1]}px`,
                  width: `${evidence.bbox[2]}px`,
                  height: `${evidence.bbox[3]}px`,
                }}
              />
            )}
          </div>
        </div>

        {/* Right Side: Evidence Details */}
        <div className="w-96 bg-[#FBFAF7] border-l border-[#E9E5DC] p-8 flex flex-col">
          <div className="flex justify-between items-center mb-8">
            <h3 className="font-serif text-2xl font-medium">Evidence</h3>
            <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
              <X size={20} />
            </button>
          </div>

          {loading ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <div className="w-6 h-6 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin mb-2" />
              <span className="text-xs">Locating evidence...</span>
            </div>
          ) : evidence ? (
            <div className="space-y-8">
              <div className="space-y-2">
                <label className="text-[10px] uppercase font-bold text-slate-400 block">Field</label>
                <div className="text-lg font-medium">{fieldName}</div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] uppercase font-bold text-slate-400 block">Extracted Snippet</label>
                <div className="p-4 rounded-xl bg-white border border-[#E9E5DC] text-sm italic leading-relaxed">
                  "{evidence.snippet}"
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-400 block">Page</label>
                  <div className="text-sm font-medium">{evidence.page}</div>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-400 block">Confidence</label>
                  <div className="text-sm font-medium">{(evidence.confidence * 100).toFixed(1)}%</div>
                </div>
              </div>

              <div className="pt-8 border-t border-[#E9E5DC] space-y-3">
                <button className="w-full py-3 rounded-full bg-[#A1844D] text-white text-sm font-medium flex items-center justify-center gap-2 hover:bg-[#806633] transition-all">
                  <ZoomIn size={16} />
                  Zoom to region
                </button>
                <button className="w-full py-3 rounded-full border border-[#E9E5DC] bg-white text-sm font-medium flex items-center justify-center gap-2 hover:bg-[#FBFBFB] transition-all">
                  <ExternalLink size={16} />
                  Open full document
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-400 text-sm">
              No evidence found for this field.
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
