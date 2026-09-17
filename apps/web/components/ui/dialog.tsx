"use client";

import { Button } from "@/components/ui/button";
import type { ReactNode } from "react";

export function Dialog({
  open,
  title,
  children,
  onClose,
}: {
  open: boolean;
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy-950/40 px-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl"
      >
        <div className="mb-4 flex items-start justify-between gap-4">
          <h2 id="dialog-title" className="text-lg font-semibold text-navy-900">
            {title}
          </h2>
          <Button variant="ghost" onClick={onClose} aria-label="Close dialog">
            Close
          </Button>
        </div>
        {children}
      </div>
    </div>
  );
}
