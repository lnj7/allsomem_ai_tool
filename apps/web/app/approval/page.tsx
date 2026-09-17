"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { productApi } from "@/lib/api/product";
import { ErrorState } from "@/components/ui/error-state";
import { ApiError } from "@/lib/api/client";

export default function ApprovalPage() {
  const [assets, setAssets] = useState<Array<Record<string, unknown>>>([]);
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);
  const [when, setWhen] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    const list = await productApi.assets();
    setAssets(list);
    setSelected(list[0] || null);
  }

  useEffect(() => {
    load().catch(() => undefined);
  }, []);

  async function approve() {
    if (!selected?.id) return;
    setError("");
    await productApi.approve(String(selected.id));
    setNotice("Marked ready. Social publishing is not connected, so this stays in CreatorOS.");
    await load();
  }

  async function schedule() {
    if (!selected?.id || !when) return;
    setError("");
    try {
      await productApi.schedule(String(selected.id), new Date(when).toISOString(), "manual");
      setNotice("Saved to the calendar. It will not post to social platforms until official APIs are connected.");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not schedule.");
    }
  }

  return (
    <AppShell title="Ready to Publish">
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          {assets.map((item) => (
            <button
              key={String(item.id)}
              className="mb-2 block w-full rounded-xl bg-slate-50 px-4 py-3 text-left text-sm"
              onClick={() => setSelected(item)}
            >
              {String(item.title)} · {String(item.status)}
            </button>
          ))}
          {!assets.length ? <p className="text-sm text-slate-500">Generate content in Studio first.</p> : null}
        </Card>
        <Card>
          {selected ? (
            <>
              <h2 className="text-lg font-semibold">{String(selected.title)}</h2>
              <p className="mt-3 whitespace-pre-wrap text-sm text-slate-600">{String(selected.caption || selected.script || "")}</p>
              <Input className="mt-4" type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} />
              {error ? <ErrorState message={error} /> : null}
              {notice ? <p className="mt-3 text-sm text-emerald-700">{notice}</p> : null}
              <div className="mt-4 flex gap-3">
                <Button variant="secondary" onClick={approve}>
                  Approve
                </Button>
                <Button onClick={schedule}>Schedule</Button>
              </div>
            </>
          ) : null}
        </Card>
      </div>
    </AppShell>
  );
}
