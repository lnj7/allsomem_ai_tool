"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { productApi } from "@/lib/api/product";

export default function ContentCalendarPage() {
  const [assets, setAssets] = useState<Array<Record<string, unknown>>>([]);
  useEffect(() => {
    productApi.assets().then(setAssets).catch(() => undefined);
  }, []);

  return (
    <AppShell title="Content Calendar">
      <Card>
        <h2 className="font-semibold">Scheduled and saved content</h2>
        <p className="mt-2 text-sm text-slate-500">
          Items appear here after you generate them in Studio. Official social posting is not connected yet, so
          nothing is published automatically.
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {assets.map((item) => (
            <div key={String(item.id)} className="rounded-2xl border border-slate-200 p-4">
              <p className="font-medium">{String(item.title)}</p>
              <p className="mt-1 text-sm text-slate-500">{String(item.status)}</p>
              <p className="mt-1 text-xs text-slate-400">{item.scheduled_at ? String(item.scheduled_at) : "Unscheduled"}</p>
            </div>
          ))}
          {!assets.length ? <p className="text-sm text-slate-500">No calendar items yet.</p> : null}
        </div>
      </Card>
    </AppShell>
  );
}
