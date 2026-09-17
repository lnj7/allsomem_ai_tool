"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { ErrorState } from "@/components/ui/error-state";

export default function VideoStudioPage() {
  return (
    <AppShell title="AI Video Studio">
      <Card>
        <h2 className="font-semibold">Create your video</h2>
        <p className="mt-3 text-sm text-slate-600">
          Script, duration, language, and style controls are ready in the product UI. Video generation requires a
          configured video provider. No fake video is created.
        </p>
        <div className="mt-4">
          <ErrorState message="Video provider is not configured." />
        </div>
      </Card>
    </AppShell>
  );
}
