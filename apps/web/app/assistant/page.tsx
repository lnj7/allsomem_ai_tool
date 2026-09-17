"use client";

import { FormEvent, useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ErrorState } from "@/components/ui/error-state";
import { productApi } from "@/lib/api/product";
import { ApiError } from "@/lib/api/client";

export default function AssistantPage() {
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    productApi.assistantHistory().then(setMessages).catch(() => undefined);
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const result = await productApi.askAssistant(message);
      setMessages((current) => [...current, { role: "user", content: message }, { role: "assistant", content: result.reply }]);
      setMessage("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Assistant failed.");
    }
  }

  return (
    <AppShell title="AI Assistant">
      <Card className="max-w-3xl">
        <div className="space-y-3">
          {messages.map((item, index) => (
            <div key={`${item.role}-${index}`} className={`rounded-2xl px-4 py-3 text-sm ${item.role === "assistant" ? "bg-[#eef0ff]" : "bg-slate-50"}`}>
              <p className="text-xs uppercase text-slate-400">{item.role}</p>
              <p className="mt-1 whitespace-pre-wrap">{item.content}</p>
            </div>
          ))}
        </div>
        <form className="mt-4 space-y-3" onSubmit={onSubmit}>
          <Textarea value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Ask Jadon Family creatorOS & co." required />
          {error ? <ErrorState message={error} /> : null}
          <Button type="submit">Send</Button>
        </form>
      </Card>
    </AppShell>
  );
}
