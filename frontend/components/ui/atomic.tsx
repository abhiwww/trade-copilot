import React from "react";

export const Button = ({
  children,
  className = "",
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" }) => {
  const variants = {
    primary: "bg-[#A1844D] text-white hover:bg-[#806633]",
    secondary: "bg-[#F8F6F1] text-[#5C5B56] border border-[#E9E5DC] hover:bg-[#F5F0E6]",
    ghost: "bg-transparent text-[#5C5B56] hover:bg-[#F8F6F1]"
  };

  return (
    <button
      className={`px-4 py-2 rounded-full transition-all active:scale-95 disabled:opacity-50 font-medium text-sm ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export const Badge = ({
  children,
  className = "",
  variant = "default"
}: React.HTMLAttributes<HTMLDivElement> & { variant?: "default" | "success" | "error" | "warning" }) => {
  const variants = {
    default: "bg-[#F8F6F1] border-[#E9E5DC] text-[#5C5B56]",
    success: "bg-green-100 border-green-200 text-green-700",
    error: "bg-rose-100 border-rose-200 text-rose-700",
    warning: "bg-[#FFF4F1] border-[#E2B4A8] text-[#8A3F31]",
  };

  return (
    <div className={`flex items-center gap-2 px-3 py-1 rounded-full border text-xs ${variants[variant]} ${className}`}>
      {children}
    </div>
  );
};

export const Card = ({ children, className = "" }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={`bg-white border border-[#E9E5DC] rounded-2xl shadow-sm ${className}`}>
    {children}
  </div>
);
