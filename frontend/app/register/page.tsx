"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { API_URL } from "@/app/lib/api-config";

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    org_name: ""
  });
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const router = useRouter();

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        router.push("/login");
      } else {
        const err = await response.json();
        setErrorMessage(err.detail || "Registration failed. Please try again.");
      }
    } catch (error) {
      console.error("Registration error:", error);
      setErrorMessage("Unable to connect to Trade Copilot.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#FBFAF7] flex flex-col items-center justify-center px-6 py-12">
      <div className="flex flex-col items-center mb-12">
        <div className="w-16 h-16 rounded-full border-[2px] border-[#A1844D] text-[#A1844D] flex items-center justify-center text-4xl mb-4">
          ◎
        </div>
        <div className="text-center">
          <h1 className="font-serif text-3xl tracking-widest font-medium text-[#171914]">TRADE COPILOT</h1>
          <p className="text-[10px] tracking-wider text-[#85847E] uppercase mt-1">Global Trade. Clearer. Faster.</p>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg bg-white border border-[#E9E5DC] rounded-[24px] p-10 shadow-[0_12px_35px_rgba(60,50,30,0.04)]"
      >
        <div className="text-center mb-8">
          <h2 className="font-serif text-2xl font-medium text-[#171914] mb-2">Create your account</h2>
          <p className="text-sm text-[#777771]">Join the global network of trade intelligence</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-5">
          {errorMessage && (
            <div className="rounded-xl border border-[#E2B4A8] bg-[#FFF4F1] px-4 py-3 text-sm text-[#8A3F31]">
              {errorMessage}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="block text-xs font-medium text-[#8B8A85] uppercase tracking-wider">First Name</label>
              <input
                type="text"
                required
                value={formData.first_name}
                onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
                placeholder="John"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-xs font-medium text-[#8B8A85] uppercase tracking-wider">Last Name</label>
              <input
                type="text"
                required
                value={formData.last_name}
                onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
                placeholder="Doe"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-medium text-[#8B8A85] uppercase tracking-wider">Work Email</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
              placeholder="name@company.com"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-medium text-[#8B8A85] uppercase tracking-wider">Organization Name</label>
            <input
              type="text"
              required
              value={formData.org_name}
              onChange={(e) => setFormData({...formData, org_name: e.target.value})}
              className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
              placeholder="Buildora Trading Ltd"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-medium text-[#8B8A85] uppercase tracking-wider">Password</label>
            <input
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-full bg-[#A1844D] text-white font-medium text-sm transition-all hover:bg-[#806633] active:scale-95 disabled:opacity-50 mt-4"
          >
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <div className="relative my-8">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-[#E9E5DC]"></div>
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-2 text-[#8B8A85]">Already have an account?</span>
          </div>
        </div>

        <div className="text-center">
          <a href="/login" className="text-sm text-[#A1844D] font-medium hover:underline">Sign in to your account</a>
        </div>
      </motion.div>
    </main>
  );
}
