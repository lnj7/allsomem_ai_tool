"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { productApi, type Profile } from "@/lib/api/product";
import { ApiError } from "@/lib/api/client";

export default function CreatorProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [status, setStatus] = useState("missing");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);

  async function load() {
    const result = await productApi.strategy();
    setStatus(result.status);
    setProfile(result.profile);
  }

  useEffect(() => {
    load().catch(() => undefined);
  }, []);

  async function generate() {
    setError("");
    setLoading(true);
    try {
      const result = await productApi.generateProfile();
      setProfile(result.profile);
      setStatus(result.status);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not generate profile.");
    } finally {
      setLoading(false);
    }
  }

  async function save(accept: boolean) {
    if (!profile) return;
    setError("");
    try {
      const result = await productApi.saveProfile(profile, accept);
      setProfile(result.profile);
      setStatus(result.status);
      setEditing(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save profile.");
    }
  }

  return (
    <AppShell title="Your Creator Profile">
      <div className="mb-4 flex flex-wrap gap-3">
        <Button onClick={generate} disabled={loading}>
          {loading ? "Generating..." : "Generate / Regenerate"}
        </Button>
        <Button variant="secondary" onClick={() => setEditing(true)} disabled={!profile}>
          Edit
        </Button>
        <Button variant="dark" onClick={() => save(true)} disabled={!profile}>
          Accept Profile
        </Button>
      </div>
      {loading ? <LoadingState label="Creating your strategy..." /> : null}
      {error ? <ErrorState message={error} /> : null}
      {!profile ? (
        <Card className="mt-4">
          <p className="text-sm text-slate-600">
            Complete onboarding, then generate a profile. If you see “AI provider is not configured.”, add AI_API_KEY
            to `.env` and restart the API.
          </p>
        </Card>
      ) : (
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <Card>
            <p className="text-xs uppercase text-[#6d5efc]">Status · {status}</p>
            <h2 className="mt-2 text-xl font-semibold">{profile.niche}</h2>
            {editing ? (
              <Textarea className="mt-3" value={profile.positioning} onChange={(e) => setProfile({ ...profile, positioning: e.target.value })} />
            ) : (
              <p className="mt-3 text-slate-600">{profile.positioning}</p>
            )}
            <p className="mt-4 text-sm font-medium">Tone: {editing ? <Input value={profile.tone} onChange={(e) => setProfile({ ...profile, tone: e.target.value })} /> : profile.tone}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {profile.brand_personality.map((item) => (
                <span key={item} className="rounded-full bg-[#eef0ff] px-3 py-1 text-xs text-[#6d5efc]">
                  {item}
                </span>
              ))}
            </div>
          </Card>
          <Card>
            <h3 className="font-semibold">Audience</h3>
            <p className="mt-2 text-sm text-slate-600">{profile.audience.description}</p>
            <p className="mt-3 text-sm font-medium">Pain points</p>
            <ul className="mt-1 list-disc pl-5 text-sm text-slate-600">
              {profile.audience.pain_points.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </Card>
          <Card className="lg:col-span-2">
            <h3 className="font-semibold">Content pillars</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {profile.content_pillars.map((pillar) => (
                <div key={pillar.name} className="rounded-2xl bg-slate-50 p-4">
                  <p className="font-medium">{pillar.name}</p>
                  <p className="mt-1 text-sm text-slate-600">{pillar.description}</p>
                  <p className="mt-2 text-sm text-[#6d5efc]">{pillar.percentage}%</p>
                </div>
              ))}
            </div>
            <h3 className="mt-6 font-semibold">Initial strategy</h3>
            <ul className="mt-2 list-disc pl-5 text-sm text-slate-600">
              {profile.initial_strategy.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            {editing ? (
              <Button className="mt-4" onClick={() => save(false)}>
                Save edits
              </Button>
            ) : null}
          </Card>
        </div>
      )}
    </AppShell>
  );
}
