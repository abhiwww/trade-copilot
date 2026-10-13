"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Globe, Package, Tag, Plus } from "lucide-react";
import { API_URL } from "@/app/lib/api-config";

interface CreateCaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (caseData: any) => void;
}

export default function CreateCaseModal({ isOpen, onClose, onCreate }: CreateCaseModalProps) {
  const [formData, setFormData] = useState({
    name: "",
    product: "",
    hs_code: "",
    origin: { country: "", state: "", city: "", port: "" },
    destination: { country: "", state: "", city: "", port: "" },
  });
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleChange = (section: "root" | "origin" | "destination", field: string, value: string) => {
    if (section === "root") {
      setFormData(prev => ({ ...prev, [field]: value }));
    } else if (section === "origin") {
      setFormData(prev => ({
        ...prev,
        origin: { ...prev.origin, [field]: value }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        destination: { ...prev.destination, [field]: value }
      }));
    }
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/cases/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: formData.name,
          product: formData.product,
          hs_code: formData.hs_code,
          origin_country: formData.origin.country,
          origin_state: formData.origin.state,
          origin_city: formData.origin.city,
          origin_port: formData.origin.port,
          dest_country: formData.destination.country,
          dest_state: formData.destination.state,
          dest_city: formData.destination.city,
          dest_port: formData.destination.port,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // The backend returns { message, case_id }.
        // We need to fetch the full case object to pass to onCreate.
        const caseRes = await fetch(`${API_URL}/api/v1/cases/${data.case_id}`, {
          credentials: "include",
        });
        const caseData = await caseRes.json();
        onCreate(caseData);
        onClose();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setErrorMessage(errorData.detail || "Unable to create the trade case.");
      }
    } catch (error) {
      console.error("Create case error:", error);
      setErrorMessage("Unable to connect to Trade Copilot.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/40 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            className="bg-white rounded-[32px] w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col"
          >
            {/* Header */}
            <div className="px-8 py-6 border-b border-[#E9E5DC] flex justify-between items-center bg-[#FBFAF7]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#A1844D] text-white flex items-center justify-center">
                  <Plus size={20} />
                </div>
                <h2 className="font-serif text-2xl font-medium">New Trade Case</h2>
              </div>
              <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
                <X size={20} />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-8 space-y-8 max-h-[70vh] overflow-y-auto">
              {errorMessage && (
                <div className="rounded-xl border border-[#E2B4A8] bg-[#FFF4F1] px-4 py-3 text-sm text-[#8A3F31]">
                  {errorMessage}
                </div>
              )}

              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-[10px] uppercase font-bold text-slate-400 block">Case Name</label>
                  <div className="relative">
                    <input
                      required
                      value={formData.name}
                      onChange={(e) => handleChange("root", "name", e.target.value)}
                      className="w-full pl-10 pr-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
                      placeholder="e.g. Q3 Electronics Shipment"
                    />
                    <Tag size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] uppercase font-bold text-slate-400 block">HS Code</label>
                  <input
                    required
                    value={formData.hs_code}
                    onChange={(e) => handleChange("root", "hs_code", e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
                    placeholder="e.g. 8517.12"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] uppercase font-bold text-slate-400 block">Product Description</label>
                <div className="relative">
                  <input
                    required
                    value={formData.product}
                    onChange={(e) => handleChange("root", "product", e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
                    placeholder="e.g. High-end Smartphones"
                  />
                  <Package size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-8">
                {/* Origin */}
                <div className="space-y-4 p-6 rounded-2xl bg-[#F8F6F1] border border-[#E9E5DC]">
                  <div className="flex items-center gap-2 mb-2">
                    <Globe size={14} className="text-[#A1844D]" />
                    <span className="text-xs font-bold uppercase text-[#A1844D]">Origin</span>
                  </div>
                  <div className="space-y-3">
                    <input
                      required
                      placeholder="Country"
                      value={formData.origin.country}
                      onChange={(e) => handleChange("origin", "country", e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-[#E9E5DC] bg-white text-xs"
                    />
                    <input
                      placeholder="State/Province"
                      value={formData.origin.state}
                      onChange={(e) => handleChange("origin", "state", e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-[#E9E5DC] bg-white text-xs"
                    />
                    <input
                      placeholder="City"
                      value={formData.origin.city}
                      onChange={(e) => handleChange("origin", "city", e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-[#E9E5DC] bg-white text-xs"
                    />
                    <input
                      placeholder="Port/Airport"
                      value={formData.origin.port}
                      onChange={(e) => handleChange("origin", "port", e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-[#E9E5DC] bg-white text-xs"
                    />
                  </div>
                </div>

                {/* Destination */}
                <div className="space-y-4 p-6 rounded-2xl bg-[#F8F6F1] border border-[#E9E5DC]">
                  <div className="flex items-center gap-2 mb-2">
                    <Globe size={14} className="text-[#A1844D]" />
                    <span className="text-xs font-bold uppercase text-[#A1844D]">Destination</span>
                  </div>
                  <div className="space-y-3">
                    <input
                      required
                      placeholder="Country"
                      value={formData.destination.country}
                      onChange={(e) => handleChange("destination", "country", e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-[#E9E5DC] bg-white text-xs"
                    />
                    <input
                      placeholder="State/Province"
                      value={formData.destination.state}
                      onChange={(e) => handleChange("destination", "state", e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-[#E9E5DC] bg-white text-xs"
                    />
                    <input
                      placeholder="City"
                      value={formData.destination.city}
                      onChange={(e) => handleChange("destination", "city", e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-[#E9E5DC] bg-white text-xs"
                    />
                    <input
                      placeholder="Port/Airport"
                      value={formData.destination.port}
                      onChange={(e) => handleChange("destination", "port", e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-[#E9E5DC] bg-white text-xs"
                    />
                  </div>
                </div>
              </div>
            </form>

            {/* Footer */}
            <div className="px-8 py-6 border-t border-[#E9E5DC] bg-[#FBFAF7] flex justify-end gap-3">
              <button
                onClick={onClose}
                className="px-6 py-2 rounded-full text-sm font-medium text-slate-500 hover:bg-slate-100 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-8 py-2 rounded-full bg-[#A1844D] text-white text-sm font-medium hover:bg-[#806633] transition-all active:scale-95 disabled:opacity-50"
              >
                {loading ? "Creating..." : "Create Trade Case"}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
