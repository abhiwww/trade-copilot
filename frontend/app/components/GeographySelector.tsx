"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Globe, ChevronDown, MapPin, Ship, Plane } from "lucide-react";
import { API_URL } from "@/app/lib/api-config";

interface RouteState {
  origin: { country: string; state: string; city: string; port: string };
  destination: { country: string; state: string; city: string; port: string };
}

interface GeographySelectorProps {
  currentRoute: RouteState;
  onRouteChange: (newRoute: RouteState) => void;
}

interface GeographyData {
  countries: string[];
  states: string[];
  cities: string[];
  ports: string[];
}

interface SelectorProps {
  label: string;
  options: string[];
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function GeographySelector({ currentRoute, onRouteChange }: GeographySelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const [origin, setOrigin] = useState(currentRoute.origin);
  const [destination, setDestination] = useState(currentRoute.destination);

  const [originData, setOriginData] = useState<GeographyData>({ countries: [], states: [], cities: [], ports: [] });
  const [destData, setDestData] = useState<GeographyData>({ countries: [], states: [], cities: [], ports: [] });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen) {
      fetchCountries();
    }
  }, [isOpen]);

  async function fetchCountries() {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/geography/countries`);
      const data = await res.json();
      setOriginData(prev => ({ ...prev, countries: data.countries }));
      setDestData(prev => ({ ...prev, countries: data.countries }));
    } finally {
      setLoading(false);
    }
  }

  async function updateOrigin(level: string, value: string) {
    if (level === "country") {
      setOrigin(prev => ({ ...prev, country: value, state: "", city: "", port: "" }));
      const res = await fetch(`${API_URL}/api/v1/geography/states/${value}`);
      const data = await res.json();
      setOriginData(prev => ({ ...prev, states: data.states, cities: [], ports: [] }));
    } else if (level === "state") {
      setOrigin(prev => ({ ...prev, state: value, city: "", port: "" }));
      const res = await fetch(`${API_URL}/api/v1/geography/cities/${origin.country}/${value}`);
      const data = await res.json();
      setOriginData(prev => ({ ...prev, cities: data.cities, ports: [] }));
    } else if (level === "city") {
      setOrigin(prev => ({ ...prev, city: value, port: "" }));
      const res = await fetch(`${API_URL}/api/v1/geography/ports/${origin.country}/${origin.state}/${value}`);
      const data = await res.json();
      setOriginData(prev => ({ ...prev, ports: data.ports }));
    } else if (level === "port") {
      setOrigin(prev => ({ ...prev, port: value }));
    }
  }

  async function updateDestination(level: string, value: string) {
    if (level === "country") {
      setDestination(prev => ({ ...prev, country: value, state: "", city: "", port: "" }));
      const res = await fetch(`${API_URL}/api/v1/geography/states/${value}`);
      const data = await res.json();
      setDestData(prev => ({ ...prev, states: data.states, cities: [], ports: [] }));
    } else if (level === "state") {
      setDestination(prev => ({ ...prev, state: value, city: "", port: "" }));
      const res = await fetch(`${API_URL}/api/v1/geography/cities/${destination.country}/${value}`);
      const data = await res.json();
      setDestData(prev => ({ ...prev, cities: data.cities, ports: [] }));
    } else if (level === "city") {
      setDestination(prev => ({ ...prev, city: value, port: "" }));
      const res = await fetch(`${API_URL}/api/v1/geography/ports/${destination.country}/${destination.state}/${value}`);
      const data = await res.json();
      setDestData(prev => ({ ...prev, ports: data.ports }));
    } else if (level === "port") {
      setDestination(prev => ({ ...prev, port: value }));
    }
  }

  const handleApply = () => {
    onRouteChange({ origin, destination });
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={containerRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="h-10 px-5 rounded-full border border-[#E9E5DC] bg-white flex items-center gap-2 text-sm font-medium hover:bg-[#f7f4ee] transition-colors"
      >
        <span className="text-[#806633] text-lg">↔</span> {origin.country || "Origin"} → {destination.country || "Destination"}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute top-full mt-3 right-0 w-[450px] glass-card bg-white border border-[#E9E5DC] shadow-2xl z-50 p-6"
          >
            <div className="flex items-center gap-2 mb-6 pb-2 border-b border-[#E9E5DC]">
              <Globe size={18} className="text-[#A1844D]" />
              <h3 className="font-serif text-lg font-medium">Configure Trade Route</h3>
            </div>

            <div className="grid grid-cols-2 gap-8">
              {/* Origin Column */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-xs font-bold uppercase text-slate-400 mb-2">
                  <MapPin size={12} /> Origin
                </div>
                <Selector
                  label="Country"
                  options={originData.countries}
                  value={origin.country}
                  onChange={(v) => updateOrigin("country", v)}
                />
                <Selector
                  label="State"
                  options={originData.states}
                  value={origin.state}
                  onChange={(v) => updateOrigin("state", v)}
                  disabled={!origin.country}
                />
                <Selector
                  label="City"
                  options={originData.cities}
                  value={origin.city}
                  onChange={(v) => updateOrigin("city", v)}
                  disabled={!origin.state}
                />
                <Selector
                  label="Port/Airport"
                  options={originData.ports}
                  value={origin.port}
                  onChange={(v) => updateOrigin("port", v)}
                  disabled={!origin.city}
                />
              </div>

              {/* Destination Column */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-xs font-bold uppercase text-slate-400 mb-2">
                  <MapPin size={12} className="rotate-180" /> Destination
                </div>
                <Selector
                  label="Country"
                  options={destData.countries}
                  value={destination.country}
                  onChange={(v) => updateDestination("country", v)}
                />
                <Selector
                  label="State"
                  options={destData.states}
                  value={destination.state}
                  onChange={(v) => updateDestination("state", v)}
                  disabled={!destination.country}
                />
                <Selector
                  label="City"
                  options={destData.cities}
                  value={destination.city}
                  onChange={(v) => updateDestination("city", v)}
                  disabled={!destination.state}
                />
                <Selector
                  label="Port/Airport"
                  options={destData.ports}
                  value={destination.port}
                  onChange={(v) => updateDestination("port", v)}
                  disabled={!destination.city}
                />
              </div>
            </div>

            <div className="mt-8 flex justify-end gap-3">
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 text-sm text-slate-500 hover:text-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleApply}
                className="px-6 py-2 bg-[#A1844D] text-white rounded-full text-sm font-medium hover:bg-[#806633] transition-colors"
              >
                Apply Route
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function Selector({ label, options, value, onChange, disabled = false }: SelectorProps) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-[10px] uppercase font-bold text-slate-400">{label}</label>
      <select
        disabled={disabled}
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 rounded-lg border border-[#E9E5DC] bg-white text-sm outline-none focus:border-[#A1844D] disabled:bg-slate-50 disabled:text-slate-300 transition-all"
      >
        <option value="">Select {label}...</option>
        {options.map((opt: string) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </div>
  );
}
