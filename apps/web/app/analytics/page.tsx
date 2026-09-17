"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { productApi } from "@/lib/api/product";

export default function AnalyticsPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  useEffect(() => {
    productApi.analytics().then(setData).catch(() => undefined);
  }, []);
  return (
    <AppShell title="Content Performance">
      <div className="grid gap-4 sm:grid-cols-4">
        {["views", "likes", "comments", "shares"].map((key) => (
          <Card key={key}>
            <p className="text-sm capitalize text-slate-500">{key}</p>
            <p className="mt-2 text-3xl font-semibold">{Number(data?.[key] || 0)}</p>
          </Card>
        ))}
      </div>
      <Card className="mt-6">
        <p className="text-sm text-slate-600">{String(data?.note || "")}</p>
        <p className="mt-2 text-sm text-slate-500">Tracked local assets: {Number(data?.content_count || 0)}</p>
      </Card>
    </AppShell>
  );
}
