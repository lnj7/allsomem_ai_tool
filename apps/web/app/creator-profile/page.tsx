"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { productApi, type Profile, type YouTubeSnapshot } from "@/lib/api/product";
import { ApiError } from "@/lib/api/client";

export default function CreatorProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [status, setStatus] = useState("missing");
  const [youtube, setYoutube] = useState<YouTubeSnapshot | null>(null);
  const [channelUrl, setChannelUrl] = useState("https://www.youtube.com/@laxminarayan308");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [editing, setEditing] = useState(false);

  async function load() {
    const [strategy, connection] = await Promise.all([productApi.strategy(), productApi.youtube()]);
    setStatus(strategy.status);
    setProfile(strategy.profile);
    setYoutube(connection.snapshot);
    if (connection.snapshot?.url) setChannelUrl(connection.snapshot.url);
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

  async function connectChannel() {
    setError("");
    setSyncing(true);
    try {
      const result = await productApi.connectYouTube(channelUrl);
      setYoutube(result.snapshot);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load that YouTube channel.");
    } finally {
      setSyncing(false);
    }
  }

  async function refreshChannel() {
    setError("");
    setSyncing(true);
    try {
      const result = await productApi.refreshYouTube();
      setYoutube(result.snapshot);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not refresh YouTube.");
    } finally {
      setSyncing(false);
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
      <Card className="mb-4">
        <p className="text-xs uppercase tracking-wide text-[#6d5efc]">YouTube channel</p>
        <h2 className="mt-1 text-lg font-semibold">Connect a public channel URL or @handle</h2>
        <p className="mt-2 text-sm text-slate-600">
          This loads the live public page (name, subscribers, videos). It is not a YouTube password login and cannot
          publish or read Studio-only stats.
        </p>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <Input
            value={channelUrl}
            onChange={(e) => setChannelUrl(e.target.value)}
            placeholder="https://www.youtube.com/@yourhandle"
          />
          <Button onClick={connectChannel} disabled={syncing}>
            {syncing ? "Loading..." : youtube ? "Reconnect" : "Load channel"}
          </Button>
          {youtube ? (
            <Button variant="secondary" onClick={refreshChannel} disabled={syncing}>
              Refresh
            </Button>
          ) : null}
        </div>
      </Card>

      {youtube ? (
        <div className="mb-6 grid gap-4 lg:grid-cols-3">
          <Card>
            <p className="text-sm text-slate-500">Channel</p>
            <h3 className="mt-1 text-xl font-semibold">{youtube.title}</h3>
            <p className="text-sm text-[#6d5efc]">{youtube.handle}</p>
            <p className="mt-3 text-3xl font-semibold">{youtube.subscriber_count ?? 0}</p>
            <p className="text-sm text-slate-500">{youtube.subscriber_label || "public subscribers"}</p>
            <p className="mt-2 text-sm text-slate-600">{youtube.video_count ?? 0} public videos</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">Milestone progress</p>
            <p className="mt-2 text-3xl font-semibold">{youtube.progress.percent}%</p>
            <p className="mt-1 text-sm text-slate-600">
              {youtube.progress.current} / {youtube.progress.next_milestone} subscribers
            </p>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-[#6d5efc]" style={{ width: `${youtube.progress.percent}%` }} />
            </div>
            <p className="mt-3 text-xs text-slate-500">{youtube.note}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">Next actions</p>
            <ul className="mt-3 space-y-3">
              {youtube.next_actions.slice(0, 3).map((action) => (
                <li key={action.id}>
                  <p className="text-sm font-medium">{action.title}</p>
                  <p className="text-xs text-slate-600">{action.detail}</p>
                </li>
              ))}
            </ul>
          </Card>
          <Card className="lg:col-span-3">
            <h3 className="font-semibold">Current public content</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {(youtube.videos || []).length ? (
                youtube.videos.map((video) => (
                  <a key={video.video_id} href={video.url} target="_blank" rel="noreferrer" className="rounded-2xl bg-slate-50 p-4 hover:bg-[#eef0ff]">
                    <p className="font-medium">{video.title}</p>
                    <p className="mt-1 text-sm text-slate-500">
                      {video.views_label || `${video.views ?? 0} views`} · {video.published_label || "date unknown"}
                    </p>
                  </a>
                ))
              ) : (
                <p className="text-sm text-slate-500">No public videos were listed on the channel page.</p>
              )}
            </div>
          </Card>
        </div>
      ) : null}

      <div className="mb-4 flex flex-wrap gap-3">
        <Button onClick={generate} disabled={loading}>
          {loading ? "Generating..." : "Generate / Regenerate AI strategy"}
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
            Channel stats above come from YouTube&apos;s public page. Generate an AI strategy after onboarding. If
            generation fails, check OpenAI billing — not the YouTube URL.
          </p>
        </Card>
      ) : (
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <Card>
            <p className="text-xs uppercase text-[#6d5efc]">AI strategy · {status}</p>
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
