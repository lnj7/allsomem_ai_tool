import { cn } from "@/lib/utils";
import type { TextareaHTMLAttributes } from "react";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-28 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-navy-900 placeholder:text-slate-400",
        className,
      )}
      {...props}
    />
  );
}
