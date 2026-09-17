"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { productApi } from "@/lib/api/product";

export default function GrowthPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  useEffect(() => {
    Promise.all([productApi.dashboard(), productApi.analytics()]).then(([dash, analytics]) => {
      setData({ ...dash, ...analytics });
    });
  }, []);
  return (
    <AppShell title="Growth Center">
      <Card>
        <p className="text-sm text-slate-600">
          Growth recommendations will use real analytics after platforms are connected. Current local content:{" "}
          {Number(data?.content_count || 0)}. Followers shown: {Number(data?.followers || 0)} (not estimated).
        </p>
      </Card>
    </AppShell>
  );
}
