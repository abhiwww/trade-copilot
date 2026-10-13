"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { API_URL } from "@/app/lib/api-config";

export interface UserProfile {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  name: string;
  display_name?: string;
  avatar_url?: string | null;
  role: string;
  job_title?: string | null;
  phone?: string | null;
  timezone?: string;
  language?: string;
  org_id: string;
  org_name?: string | null;
  organization?: {
    org_id: string;
    name?: string | null;
    plan?: string | null;
  };
}

interface AuthContextType {
  user: UserProfile | null;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const refreshUser = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/me`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error("Auth refresh error:", error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  async function logout() {
    try {
      await fetch(`${API_URL}/api/v1/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setUser(null);
      router.push("/login");
    }
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login: refreshUser, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export function getUserDisplayName(user: UserProfile | null) {
  if (!user) return "";
  const fullName = `${user.first_name || ""} ${user.last_name || ""}`.trim();
  return user.display_name || user.name || fullName || user.email;
}

export function getUserInitials(user: UserProfile | null) {
  if (!user) return "";
  const parts = [user.first_name, user.last_name].filter(Boolean);
  const sourceParts = parts.length > 0 ? parts : getUserDisplayName(user).split(/\s+/);
  return sourceParts
    .map((part) => part.trim()[0])
    .filter(Boolean)
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function getUserRoleLabel(user: UserProfile | null) {
  return user?.job_title || user?.role || "";
}
