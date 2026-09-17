"use client";

import { Badge } from "@/components/ui/badge";
import { LoadingState } from "@/components/ui/loading-state";
import { getApiHealth } from "@/lib/api/health";
import { useEffect, useState } from "react";

type Status = "loading" | "connected" | "unavailable";

export function BackendHealthIndicator() {
  const [status, setStatus] = useState<Status>("loading");

  useEffect(() => {
    let cancelled = false;
    getApiHealth()
      .then((result) => {
        if (!cancelled) {
          setStatus(result.status === "ok" ? "connected" : "unavailable");
        }
      })
      .catch(() => {
        if (!cancelled) setStatus("unavailable");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "loading") {
    return <LoadingState label="Checking backend..." />;
  }

  return (
    <div className="flex items-center gap-2" data-testid="backend-health">
      <span className="text-sm text-slate-600">Backend:</span>
      <Badge className={status === "connected" ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"}>
        {status === "connected" ? "Connected" : "Unavailable"}
      </Badge>
    </div>
  );
}
