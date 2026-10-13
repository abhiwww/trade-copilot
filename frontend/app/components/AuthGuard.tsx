"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/context/AuthContext";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [isLoading, router, user]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#FBFAF7] flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-[#A1844D]/20 border-t-[#A1844D] rounded-full animate-spin" />
      </div>
    );
  }

  return user ? <>{children}</> : null;
}
