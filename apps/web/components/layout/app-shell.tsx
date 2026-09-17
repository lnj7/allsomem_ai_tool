"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { APP_NAME } from "@creatoros/shared";
import { cn } from "@/lib/utils";
import { authApi } from "@/lib/api/product";
import { Button } from "@/components/ui/button";

const items = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/creator-profile", label: "Creator Profile" },
  { href: "/content-calendar", label: "Content Calendar" },
  { href: "/content-studio", label: "Content Studio" },
  { href: "/video-studio", label: "Video Studio" },
  { href: "/approval", label: "Approval" },
  { href: "/analytics", label: "Analytics" },
  { href: "/growth", label: "Growth Center" },
  { href: "/community", label: "Community" },
  { href: "/brand-center", label: "Brand Center" },
  { href: "/assistant", label: "AI Assistant" },
  { href: "/settings", label: "Settings" },
];

export function AppShell({ title, children }: { title: string; children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [name, setName] = useState("Creator");

  useEffect(() => {
    authApi
      .me()
      .then((user) => setName(user.full_name))
      .catch(() => router.replace("/login"));
  }, [router]);

  return (
    <div className="min-h-screen bg-[#f5f6fb]">
      <aside className="hidden md:fixed md:inset-y-0 md:flex md:w-60 md:flex-col border-r border-slate-200 bg-white px-4 py-6">
        <Link href="/dashboard" className="mb-8 px-2 text-base font-semibold leading-snug text-[#0b1230]">
          {APP_NAME}
        </Link>
        <nav className="flex flex-1 flex-col gap-1 overflow-y-auto" aria-label="Primary">
          {items.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "rounded-xl px-3 py-2 text-sm",
                  active ? "bg-[#6d5efc] text-white" : "text-slate-600 hover:bg-slate-100",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="md:pl-60">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-4 sm:px-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[#6d5efc]">{APP_NAME}</p>
            <h1 className="text-lg font-semibold text-[#0b1230]">{title}</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-slate-500 sm:inline">{name}</span>
            <Button
              variant="ghost"
              onClick={async () => {
                await authApi.logout();
                router.push("/login");
              }}
            >
              Log out
            </Button>
          </div>
        </header>
        <main className="px-4 py-6 sm:px-8 pb-24">{children}</main>
      </div>
      <nav className="fixed inset-x-0 bottom-0 z-40 flex gap-2 overflow-x-auto border-t bg-white px-3 py-2 md:hidden">
        {items.slice(0, 5).map((item) => (
          <Link key={item.href} href={item.href} className="whitespace-nowrap rounded-full px-3 py-2 text-xs text-slate-600">
            {item.label}
          </Link>
        ))}
      </nav>
    </div>
  );
}
