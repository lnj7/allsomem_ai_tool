"use client";

import { FormEvent, useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { ErrorState } from "@/components/ui/error-state";
import { productApi } from "@/lib/api/product";
import { ApiError } from "@/lib/api/client";

export default function ContentStudioPage() {
  const [topic, setTopic] = useState("");
  const [platform, setPlatform] = useState("Instagram");
  const [format, setFormat] = useState("Reel");
  const [goal, setGoal] = useState("Teach a useful concept");
  const [error, setError] = useState("");
  const [asset, setAsset] = useState<Record<string, unknown> | null>(null);
  const [assets, setAssets] = useState<Array<Record<string, unknown>>>([]);

  useEffect(() => {
    productApi.assets().then(setAssets).catch(() => undefined);
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const result = (await productApi.generateContent({ topic, platform, format, goal })) as Record<string, unknown>;
      setAsset(result);
      const list = await productApi.assets();
      setAssets(list);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not generate content.");
    }
  }

  return (
    <AppShell title="AI Content Studio">
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="font-semibold">Create publish-ready content</h2>
          <form className="mt-4 space-y-3" onSubmit={onSubmit}>
            <Input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Topic" required />
            <Select value={platform} onChange={(e) => setPlatform(e.target.value)}>
              {["Instagram", "YouTube", "LinkedIn", "TikTok", "X"].map((item) => (
                <option key={item}>{item}</option>
              ))}
            </Select>
            <Select value={format} onChange={(e) => setFormat(e.target.value)}>
              {["Reel", "Shorts", "Carousel", "Thread", "Long-form"].map((item) => (
                <option key={item}>{item}</option>
              ))}
            </Select>
            <Input value={goal} onChange={(e) => setGoal(e.target.value)} placeholder="Goal" />
            {error ? <ErrorState message={error} /> : null}
            <Button type="submit">Generate</Button>
          </form>
        </Card>
        <Card>
          <h2 className="font-semibold">Generated content</h2>
          {asset ? (
            <div className="mt-3 space-y-2 text-sm">
              <p className="text-lg font-semibold">{String(asset.title)}</p>
              <p className="whitespace-pre-wrap text-slate-600">{String(asset.script || "")}</p>
              <p className="text-slate-600">{String(asset.caption || "")}</p>
            </div>
          ) : (
            <p className="mt-3 text-sm text-slate-500">Generate a piece to see script, caption, and CTA here.</p>
          )}
        </Card>
      </div>
      <Card className="mt-6">
        <h3 className="font-semibold">Your assets</h3>
        <div className="mt-3 space-y-2">
          {assets.map((item) => (
            <div key={String(item.id)} className="rounded-xl bg-slate-50 px-4 py-3 text-sm">
              {String(item.title)} · {String(item.status)}
            </div>
          ))}
        </div>
      </Card>
    </AppShell>
  );
}
