"use client";

import React, { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { User, Building, Bell, Lock, Globe, LogOut, KeyRound } from "lucide-react";
import AuthGuard from "@/app/components/AuthGuard";
import {
  getUserDisplayName,
  getUserInitials,
  getUserRoleLabel,
  useAuth,
} from "@/app/context/AuthContext";
import { API_URL } from "@/app/lib/api-config";

const tabs = [
  { id: "personal", label: "Personal", icon: User },
  { id: "organization", label: "Organization", icon: Building },
  { id: "preferences", label: "Preferences", icon: Globe },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "security", label: "Security", icon: Lock },
  { id: "integrations", label: "API", icon: KeyRound },
];

export default function ProfilePage() {
  const { user, logout, refreshUser } = useAuth();
  const [activeTab, setActiveTab] = useState("personal");
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    job_title: "",
    phone: "",
    timezone: "UTC",
    language: "en",
  });
  const [saving, setSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tab = params.get("tab");
    if (tab && tabs.some((item) => item.id === tab)) setActiveTab(tab);
  }, []);

  useEffect(() => {
    if (!user) return;
    setFormData({
      first_name: user.first_name || "",
      last_name: user.last_name || "",
      email: user.email || "",
      job_title: user.job_title || "",
      phone: user.phone || "",
      timezone: user.timezone || "UTC",
      language: user.language || "en",
    });
  }, [user]);

  const displayName = getUserDisplayName(user);
  const initials = getUserInitials(user);
  const roleLabel = getUserRoleLabel(user);
  const organizationName = user?.org_name || user?.organization?.name || "Organization";
  const organizationPlan = user?.organization?.plan || "Enterprise";

  const updateField = (field: keyof typeof formData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  async function handleSaveProfile(e?: React.FormEvent) {
    e?.preventDefault();
    setSaving(true);
    setStatusMessage(null);
    setErrorMessage(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/me`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Unable to save profile changes.");
      }

      await refreshUser();
      setStatusMessage("Profile updated.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to save profile changes.");
    } finally {
      setSaving(false);
    }
  }

  const notificationSettings = useMemo(
    () => [
      { label: "Risk Alerts", desc: "High-risk findings and review-required events.", active: true },
      { label: "Processing Updates", desc: "Document processing completion and failures.", active: true },
      { label: "Case Updates", desc: "Trade case activity for your organization.", active: true },
    ],
    []
  );

  return (
    <AuthGuard>
      <main className="min-h-screen bg-[#FBFAF7] text-[#171914] p-6 lg:p-12">
        <div className="max-w-4xl mx-auto">
          <header className="mb-12">
            <h1 className="font-serif text-4xl font-medium mb-2">Account Settings</h1>
            <p className="text-[#777771]">Manage your personal information and organization preferences.</p>
          </header>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
            <nav className="md:col-span-1 space-y-1" aria-label="Account sections">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    activeTab === tab.id
                      ? "bg-white text-[#A1844D] shadow-sm border border-[#E9E5DC]"
                      : "text-[#777771] hover:bg-white/50 hover:text-[#171914]"
                  }`}
                >
                  <tab.icon size={18} />
                  {tab.label}
                </button>
              ))}
              <div className="pt-8 mt-8 border-t border-[#E9E5DC]">
                <button
                  onClick={logout}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-rose-600 hover:bg-rose-50 transition-all"
                >
                  <LogOut size={18} />
                  Sign Out
                </button>
              </div>
            </nav>

            <div className="md:col-span-3">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-white border border-[#E9E5DC] rounded-[24px] p-8 shadow-sm min-h-[500px]"
              >
                {activeTab === "personal" && (
                  <form onSubmit={handleSaveProfile} className="space-y-8">
                    <div className="flex items-center gap-6 mb-8">
                      <div className="w-20 h-20 rounded-full bg-[#9A7E48] text-white flex items-center justify-center text-2xl font-medium">
                        {initials}
                      </div>
                      <div>
                        <h3 className="text-xl font-serif font-medium">{displayName}</h3>
                        <p className="text-sm text-[#777771]">{roleLabel}</p>
                      </div>
                    </div>

                    {(statusMessage || errorMessage) && (
                      <div
                        className={`rounded-xl border px-4 py-3 text-sm ${
                          errorMessage
                            ? "border-[#E2B4A8] bg-[#FFF4F1] text-[#8A3F31]"
                            : "border-[#C9D9B8] bg-[#F6FBF1] text-[#4E6B34]"
                        }`}
                      >
                        {errorMessage || statusMessage}
                      </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <label className="block text-xs font-bold text-[#8B8A85] uppercase tracking-wider">First Name</label>
                        <input
                          type="text"
                          value={formData.first_name}
                          onChange={(e) => updateField("first_name", e.target.value)}
                          className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="block text-xs font-bold text-[#8B8A85] uppercase tracking-wider">Last Name</label>
                        <input
                          type="text"
                          value={formData.last_name}
                          onChange={(e) => updateField("last_name", e.target.value)}
                          className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
                        />
                      </div>
                      <div className="space-y-2 md:col-span-2">
                        <label className="block text-xs font-bold text-[#8B8A85] uppercase tracking-wider">Work Email</label>
                        <input
                          type="email"
                          value={formData.email}
                          onChange={(e) => updateField("email", e.target.value)}
                          className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="block text-xs font-bold text-[#8B8A85] uppercase tracking-wider">Job Title</label>
                        <input
                          type="text"
                          value={formData.job_title}
                          onChange={(e) => updateField("job_title", e.target.value)}
                          className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="block text-xs font-bold text-[#8B8A85] uppercase tracking-wider">Phone</label>
                        <input
                          type="tel"
                          value={formData.phone}
                          onChange={(e) => updateField("phone", e.target.value)}
                          className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
                        />
                      </div>
                    </div>
                    <button
                      type="submit"
                      disabled={saving}
                      className="px-6 py-2 bg-[#A1844D] text-white rounded-full text-sm font-medium hover:bg-[#806633] transition-all disabled:opacity-50"
                    >
                      {saving ? "Saving..." : "Save Changes"}
                    </button>
                  </form>
                )}

                {activeTab === "organization" && (
                  <div className="space-y-8">
                    <div className="p-6 rounded-2xl bg-[#F8F6F1] border border-[#E9E5DC]">
                      <h3 className="text-lg font-serif font-medium">{organizationName}</h3>
                      <p className="text-sm text-[#777771]">{organizationPlan} Plan</p>
                    </div>
                    <div className="space-y-4">
                      <h4 className="text-sm font-bold text-[#171914] uppercase tracking-wider">Your Membership</h4>
                      <div className="flex items-center justify-between p-4 rounded-xl border border-[#E9E5DC] bg-[#FFFEFD]">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-[#9A7E48] text-white flex items-center justify-center text-xs font-medium">
                            {initials}
                          </div>
                          <div>
                            <div className="text-sm font-medium">{displayName}</div>
                            <div className="text-[11px] text-[#8B8A85]">{user?.role}</div>
                          </div>
                        </div>
                        <span className="text-[10px] px-2 py-1 rounded-full bg-green-100 text-green-700">Active</span>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === "preferences" && (
                  <form onSubmit={handleSaveProfile} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="block text-xs font-medium text-[#8B8A85]">Timezone</label>
                        <select
                          value={formData.timezone}
                          onChange={(e) => updateField("timezone", e.target.value)}
                          className="w-full px-4 py-2 rounded-lg border border-[#E9E5DC] bg-[#FBFBFB] text-sm outline-none focus:border-[#A1844D]"
                        >
                          <option value="UTC">UTC</option>
                          <option value="Asia/Kolkata">Asia/Kolkata</option>
                          <option value="America/New_York">America/New_York</option>
                          <option value="Europe/London">Europe/London</option>
                        </select>
                      </div>
                      <div className="space-y-2">
                        <label className="block text-xs font-medium text-[#8B8A85]">Language</label>
                        <select
                          value={formData.language}
                          onChange={(e) => updateField("language", e.target.value)}
                          className="w-full px-4 py-2 rounded-lg border border-[#E9E5DC] bg-[#FBFBFB] text-sm outline-none focus:border-[#A1844D]"
                        >
                          <option value="en">English</option>
                          <option value="fr">French</option>
                          <option value="de">German</option>
                        </select>
                      </div>
                    </div>
                    <button
                      type="submit"
                      disabled={saving}
                      className="px-6 py-2 bg-[#A1844D] text-white rounded-full text-sm font-medium hover:bg-[#806633] transition-all disabled:opacity-50"
                    >
                      {saving ? "Saving..." : "Save Preferences"}
                    </button>
                  </form>
                )}

                {activeTab === "notifications" && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-serif font-medium mb-4">Notification Settings</h3>
                    <div className="space-y-4">
                      {notificationSettings.map((item) => (
                        <div key={item.label} className="flex items-center justify-between p-4 rounded-xl border border-[#E9E5DC] bg-[#FFFEFD]">
                          <div>
                            <div className="text-sm font-medium">{item.label}</div>
                            <div className="text-xs text-[#777771]">{item.desc}</div>
                          </div>
                          <div className={`w-10 h-5 rounded-full relative transition-colors ${item.active ? "bg-[#A1844D]" : "bg-slate-300"}`}>
                            <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${item.active ? "right-1" : "left-1"}`} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === "security" && (
                  <div className="space-y-8">
                    <div className="space-y-4 max-w-sm">
                      <h4 className="text-sm font-bold text-[#171914] uppercase tracking-wider">Account Security</h4>
                      <div className="p-4 rounded-xl border border-[#E9E5DC] bg-[#FFFEFD]">
                        <div className="text-sm font-medium">Signed in as {user?.email}</div>
                        <div className="text-xs text-[#777771] mt-1">Session is managed by the secure server cookie.</div>
                      </div>
                      <button
                        onClick={logout}
                        className="px-6 py-2 rounded-full border border-rose-200 text-rose-600 text-sm font-medium hover:bg-rose-50 transition-all"
                      >
                        Sign Out
                      </button>
                    </div>
                  </div>
                )}

                {activeTab === "integrations" && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-serif font-medium">API & Integrations</h3>
                    <div className="p-4 rounded-xl border border-[#E9E5DC] bg-[#FFFEFD]">
                      <div className="text-sm font-medium">No API keys have been created.</div>
                      <div className="text-xs text-[#777771] mt-1">Organization: {organizationName}</div>
                    </div>
                  </div>
                )}
              </motion.div>
            </div>
          </div>
        </div>
      </main>
    </AuthGuard>
  );
}
