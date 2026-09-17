"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { productApi } from "@/lib/api/product";

export default function SettingsPage() {
  const [mode, setMode] = useState("REVIEW_REQUIRED");
  const [saved, setSaved] = useState("");
  useEffect(() => {
    productApi.settings().then((result) => setMode(result.approval_mode)).catch(() => undefined);
  }, []);
  return (
    <AppShell title="Settings">
      <Card className="max-w-xl">
        <h2 className="font-semibold">Publishing approval</h2>
        <p className="mt-2 text-sm text-slate-600">
          Default is Review required. CreatorOS will not auto-publish to social networks until you connect official
          APIs and choose Auto-approve.
        </p>
        <Select className="mt-4" value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="MANUAL">Manual</option>
          <option value="REVIEW_REQUIRED">Review required</option>
          <option value="AUTO_APPROVE">Auto-approve (still local until platforms are connected)</option>
        </Select>
        <Button
          className="mt-4"
          onClick={async () => {
            await productApi.saveSettings(mode);
            setSaved("Saved.");
          }}
        >
          Save
        </Button>
        {saved ? <p className="mt-2 text-sm text-emerald-700">{saved}</p> : null}
      </Card>
    </AppShell>
  );
}
