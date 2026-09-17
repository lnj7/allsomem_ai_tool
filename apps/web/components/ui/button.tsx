"use client";

import { cn } from "@/lib/utils";
import type { ButtonHTMLAttributes } from "react";

const variants = {
  primary:
    "bg-[#6d5efc] text-white hover:bg-[#5b4ee8] shadow-sm disabled:opacity-50",
  secondary:
    "bg-white text-slate-800 border border-slate-200 hover:bg-slate-50",
  ghost: "bg-transparent text-slate-600 hover:bg-slate-100",
  dark: "bg-[#0b1230] text-white hover:bg-[#151b3d]",
};

export function Button({
  className,
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: keyof typeof variants }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-full px-5 py-2.5 text-sm font-medium transition",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}
