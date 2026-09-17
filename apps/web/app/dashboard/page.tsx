"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { productApi } from "@/lib/api/product";
import { BackendHealthIndicator } from "@/components/layout/backend-health";

export default function DashboardPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    productApi.dashboard().then(setData).catch(() => setData({}));
  }, []);

  const name = String(data?.creator_name || "Creator");
  const plan = Array.isArray(data?.today_plan) ? (data?.today_plan as Array<{ title: string; status: string }>) : [];

  return (
    <AppShell title="Dashboard">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-[#0b1230]">Good morning, {name}</h2>
        <p className="mt-1 text-slate-600">Here&apos;s what is happening with your content today.</p>
        <div className="mt-3">
          <BackendHealthIndicator />
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-4">
        <Card>
          <p className="text-sm text-slate-500">Followers</p>
          <p className="mt-2 text-3xl font-semibold">{Number(data?.followers || 0)}</p>
          <p className="mt-1 text-xs text-slate-500">
            {data?.followers_source === "youtube_public" ? "Public YouTube subscribers" : "Connect YouTube on Creator Profile"}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-slate-500">Content</p>
          <p className="mt-2 text-3xl font-semibold">{Number(data?.content_count || 0)}</p>
        </Card>
        <Card>
          <p className="text-sm text-slate-500">Ready to publish</p>
          <p className="mt-2 text-3xl font-semibold">{Number(data?.ready_count || 0)}</p>
        </Card>
        <Card>
          <p className="text-sm text-slate-500">Profile</p>
          <p className="mt-2 text-3xl font-semibold">{Number(data?.profile_completion || 0)}%</p>
        </Card>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Card>
          <h3 className="font-semibold">Today&apos;s Plan</h3>
          <div className="mt-4 space-y-3">
            {plan.length ? (
              plan.map((item) => (
                <div key={item.title} className="rounded-xl bg-slate-50 px-4 py-3 text-sm">
                  {item.title} · {item.status}
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500">No content planned yet. Create your first piece in Studio.</p>
            )}
          </div>
        </Card>
        <Card>
          <h3 className="font-semibold">Creator Brain</h3>
          <p className="mt-2 text-sm text-slate-600">
            {data?.profile_status === "accepted" ? "Your Creator Brain is ready." : "Not fully configured yet."}
          </p>
          <p className="mt-2 text-xs text-slate-500">
            AI {data?.ai_configured ? "is configured" : "is not configured. Add AI_API_KEY to generate profiles and content."}
          </p>
          <div className="mt-4 flex gap-3">
            <Link href="/content-studio">
              <Button>Create Content</Button>
            </Link>
            <Link href="/creator-profile">
              <Button variant="secondary">View Strategy</Button>
            </Link>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
