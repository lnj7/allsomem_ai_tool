"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { productApi, type YouTubeSnapshot } from "@/lib/api/product";

export default function GrowthPage() {
  const [youtube, setYoutube] = useState<YouTubeSnapshot | null>(null);
  const [followers, setFollowers] = useState(0);
  useEffect(() => {
    Promise.all([productApi.dashboard(), productApi.youtube()]).then(([dash, connection]) => {
      setFollowers(Number(dash.followers || 0));
      setYoutube(connection.snapshot);
    });
  }, []);
  return (
    <AppShell title="Growth Center">
      <Card className="mb-4">
        <p className="text-sm text-slate-600">
          {youtube
            ? `Public snapshot for ${youtube.title}: ${followers} subscribers, next milestone ${youtube.progress.next_milestone}. These actions are based on the live channel page. They are not a promise of faster growth.`
            : "Connect a YouTube URL on Creator Profile to load public status and a milestone plan."}
        </p>
      </Card>
      {youtube ? (
        <div className="grid gap-3">
          {youtube.next_actions.map((action) => (
            <Card key={action.id}>
              <h3 className="font-semibold">{action.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{action.detail}</p>
            </Card>
          ))}
        </div>
      ) : null}
    </AppShell>
  );
}
