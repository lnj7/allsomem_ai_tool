"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const items = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/creator-profile", label: "Profile" },
  { href: "/content-calendar", label: "Calendar" },
  { href: "/content-studio", label: "Studio" },
  { href: "/analytics", label: "Analytics" },
  { href: "/community", label: "Community" },
  { href: "/brand-center", label: "Brand" },
  { href: "/settings", label: "Settings" },
];

export function Sidebar({ className }: { className?: string }) {
  const pathname = usePathname();
  return (
    <nav className={cn("flex flex-col gap-1", className)} aria-label="Primary">
      {items.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "rounded-xl px-3 py-2 text-sm font-medium",
              active ? "bg-white/10 text-white" : "text-slate-300 hover:bg-white/5 hover:text-white",
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
