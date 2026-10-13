"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { User, Building, Settings, LogOut, Bell, Globe, ChevronDown, Shield } from "lucide-react";
import { getUserDisplayName, getUserInitials } from "@/app/context/AuthContext";
import { Button } from "../ui/atomic";

interface ProfileMenuItem {
  label: string;
  href?: string;
  action?: () => void;
  icon: React.ReactNode;
  disabled?: boolean;
}

export default function Header({
  user,
  logout,
  route,
  onRouteChange,
  GeographySelector,
  HelpPanel,
  NotificationPanel
}: any) {
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);
  const profileTriggerRef = useRef<HTMLButtonElement>(null);

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

  const profileMenuItems: ProfileMenuItem[] = [
    { label: "Profile", href: "/profile", icon: <User size={16} /> },
    { label: "Organization", href: "/profile?tab=organization", icon: <Building size={16} /> },
    { label: "Preferences", href: "/profile?tab=preferences", icon: <Settings size={16} /> },
    { label: "Security", href: "/profile?tab=security", icon: <Shield size={16} /> },
    { label: "Notifications", href: "/profile?tab=notifications", icon: <Bell size={16} /> },
    { label: "API & Integrations", href: "/profile?tab=integrations", icon: <Globe size={16} /> },
    { label: "Sign out", action: logout, icon: <LogOut size={16} /> },
  ];

  const displayName = getUserDisplayName(user);
  const displayInitials = getUserInitials(user);

  return (
    <header className="h-[92px] px-4 md:px-12 flex items-center justify-between border-b border-[#E9E5DC]/65 bg-[#FFFEFD]/86 backdrop-blur-sm sticky top-0 z-40">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full border-[1.6px] border-[#A1844D] text-[#A1844D] flex items-center justify-center text-3xl relative">
          ◎
          <div className="absolute w-5 h-11 border border-[#A1844D]/70 rounded-full" />
          <div className="absolute w-11 h-5 border border-[#A1844D]/70 rounded-full" />
        </div>
        <div className="hidden sm:block">
          <div className="font-serif text-2xl tracking-widest font-medium">TRADE COPILOT</div>
          <div className="text-[10px] tracking-wider text-[#85847E] uppercase">Global Trade. Clearer. Faster.</div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <GeographySelector currentRoute={route} onRouteChange={onRouteChange} />
        <div className="hidden md:block w-px h-6 bg-[#E9E5DC]" />
        <HelpPanel />
        <NotificationPanel />

        <div className="relative" ref={profileMenuRef}>
          <button
            ref={profileTriggerRef}
            onClick={() => setProfileMenuOpen(!profileMenuOpen)}
            className="flex items-center gap-2 pl-2 pr-3 py-2 rounded-full bg-white/50 border border-[#E9E5DC]/50 hover:bg-white/80 hover:border-[#D9CDB5] transition-all"
          >
            <div className="w-10 h-10 rounded-full bg-[#9A7E48] text-white flex items-center justify-center text-xs font-medium">
              {displayInitials}
            </div>
            <span className="hidden sm:block font-medium text-sm text-[#171914]">{displayName}</span>
            <ChevronDown size={16} className={`text-[#5C5B56] transition-transform ${profileMenuOpen ? "rotate-180" : ""}`} />
          </button>

          {profileMenuOpen && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-white border border-[#E9E5DC] rounded-xl shadow-lg py-2 z-50">
              {profileMenuItems.map((item, idx) => (
                <div key={idx}>
                  {idx === profileMenuItems.length - 1 && <div className="border-t border-[#E9E5DC] my-1" />}
                  {item.href ? (
                    <a href={item.href} className="flex items-center gap-3 px-4 py-2.5 text-sm text-[#171914] hover:bg-[#F8F6F1] transition-colors">
                      {item.icon} {item.label}
                    </a>
                  ) : (
                    <button onClick={item.action} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-[#171914] hover:bg-[#F8F6F1] transition-colors">
                      {item.icon} {item.label}
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
