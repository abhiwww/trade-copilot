"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { API_URL } from "@/app/lib/api-config";
import { useAuth } from "@/app/context/AuthContext";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const router = useRouter();
  const { refreshUser } = useAuth();

  async function handleLogin(e?: React.FormEvent) {
    if (e) e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
        credentials: "include",
      });

      if (response.ok) {
        await refreshUser();
        router.push("/");
      } else {
        const err = await response.json().catch(() => ({}));
        setErrorMessage(err.detail || "Invalid credentials. Please try again.");
      }
    } catch (error) {
      console.error("[LOGIN] error:", error);
      setErrorMessage("Unable to connect to Trade Copilot.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#FBFAF7] flex flex-col items-center justify-center px-6">
      {/* Logo Section */}
      <div className="flex flex-col items-center mb-12">
        <div className="w-16 h-16 rounded-full border-[2px] border-[#A1844D] text-[#A1844D] flex items-center justify-center text-4xl mb-4">
          ◎
        </div>
        <div className="text-center">
          <h1 className="font-serif text-3xl tracking-widest font-medium text-[#171914]">TRADE COPILOT</h1>
          <p className="text-[10px] tracking-wider text-[#85847E] uppercase mt-1">Global Trade. Clearer. Faster.</p>
        </div>
      </div>

      {/* Login Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-white border border-[#E9E5DC] rounded-[24px] p-10 shadow-[0_12px_35px_rgba(60,50,30,0.04)]"
      >
        <div className="text-center mb-8">
          <h2 className="font-serif text-2xl font-medium text-[#171914] mb-2">Welcome back</h2>
          <p className="text-sm text-[#777771]">Enter your credentials to access your workspace</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          {errorMessage && (
            <div className="rounded-xl border border-[#E2B4A8] bg-[#FFF4F1] px-4 py-3 text-sm text-[#8A3F31]">
              {errorMessage}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-[#8B8A85] uppercase tracking-wider mb-2">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
              placeholder="name@company.com"
            />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="block text-xs font-medium text-[#8B8A85] uppercase tracking-wider">Password</label>
              <a href="#" className="text-xs text-[#A1844D] hover:underline">Forgot password?</a>
            </div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl border border-[#E9E5DC] bg-[#FBFBFB] outline-none focus:border-[#A1844D] transition-colors text-sm"
              placeholder="••••••••"
            />
          </div>

          <div className="flex items-center gap-2">
            <input type="checkbox" id="remember" className="w-4 h-4 accent-[#A1844D] rounded" />
            <label htmlFor="remember" className="text-xs text-[#777771] cursor-pointer">Remember me</label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-full bg-[#A1844D] text-white font-medium text-sm transition-all hover:bg-[#806633] active:scale-95 disabled:opacity-50"
          >
            {loading ? "Authenticating..." : "Sign In"}
          </button>
        </form>

        <div className="relative my-8">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-[#E9E5DC]"></div>
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-2 text-[#8B8A85]">Or continue with</span>
          </div>
        </div>

        <button
          disabled
          className="w-full py-3 rounded-full border border-[#E9E5DC] bg-white text-[#8B8A85] font-medium text-sm flex items-center justify-center gap-3 opacity-60"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24">
            <path fill="#EA4335" d="M12.48 10.92v3.28h7.84c-.24 1.84-2.28 5.32-7.84 5.32-4.6 0-8.32-3.72-8.32-8.32s3.72-8.32 8.32-8.32c2.72 0 4.6 1.16 5.84 2.32l2.6-2.6C19.48 3.16 16.56 1.4 12.48 1.4 6.64 1.4 2 6.32 2 12.16s4.64 10.76 10.48 10.76c4.64 0 8.12-3.32 8.12-8.12 0-.52-.08-1.04-.24-1.52z"/>
          </svg>
          Google Account
        </button>

        <div className="mt-8 text-center">
          <p className="text-sm text-[#777771]">
            Don't have an account?{" "}
            <a href="/register" className="text-[#A1844D] font-medium hover:underline">Create account</a>
          </p>
        </div>
      </motion.div>
    </main>
  );
}
