"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { productApi } from "@/lib/api/product";

export default function BrandCenterPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  useEffect(() => {
    productApi.brand().then(setData).catch(() => undefined);
  }, []);
  const brand = (data?.brand || null) as Record<string, unknown> | null;
  const pillars = Array.isArray(data?.pillars) ? (data?.pillars as Array<{ name: string; percentage?: number }>) : [];
  return (
    <AppShell title="Brand Center">
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="text-xl font-semibold">{String(data?.display_name || "Your brand")}</h2>
          <p className="mt-3 text-sm text-slate-600">{String(brand?.positioning || "Generate and accept a profile to fill brand voice.")}</p>
          <p className="mt-4 text-sm">Tone: {String(brand?.tone || "—")}</p>
        </Card>
        <Card>
          <h3 className="font-semibold">Voice & colors</h3>
          <div className="mt-3 flex gap-2">
            {["#6d5efc", "#0b1230", "#22c55e", "#f59e0b", "#ef4444"].map((color) => (
              <span key={color} className="h-8 w-8 rounded-full" style={{ background: color }} />
            ))}
          </div>
          <div className="mt-4 space-y-2">
            {pillars.map((pillar) => (
              <p key={pillar.name} className="text-sm">
                {pillar.name} {pillar.percentage ? `· ${pillar.percentage}%` : ""}
              </p>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
