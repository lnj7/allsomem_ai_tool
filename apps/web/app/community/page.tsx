"use client";

import { FormEvent, useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { productApi } from "@/lib/api/product";

export default function CommunityPage() {
  const [comments, setComments] = useState<Array<Record<string, unknown>>>([]);
  const [author, setAuthor] = useState("");
  const [body, setBody] = useState("");
  const [reply, setReply] = useState("");

  async function load() {
    setComments(await productApi.comments());
  }
  useEffect(() => {
    load().catch(() => undefined);
  }, []);

  async function add(event: FormEvent) {
    event.preventDefault();
    await productApi.addComment({ author_name: author, body });
    setAuthor("");
    setBody("");
    await load();
  }

  return (
    <AppShell title="Community">
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="font-semibold">Inbox</h2>
          <p className="mt-1 text-xs text-slate-500">These are comments you save here. They are not pulled from social APIs yet.</p>
          <div className="mt-4 space-y-3">
            {comments.map((item) => (
              <div key={String(item.id)} className="rounded-xl bg-slate-50 p-3 text-sm">
                <p className="font-medium">{String(item.author_name)}</p>
                <p className="mt-1 text-slate-600">{String(item.body)}</p>
                {item.reply ? <p className="mt-2 text-[#6d5efc]">Reply: {String(item.reply)}</p> : null}
                <div className="mt-2 flex gap-2">
                  <Input value={reply} onChange={(e) => setReply(e.target.value)} placeholder="Reply" />
                  <Button
                    type="button"
                    onClick={async () => {
                      await productApi.replyComment(String(item.id), reply);
                      setReply("");
                      await load();
                    }}
                  >
                    Send
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
        <Card>
          <h2 className="font-semibold">Add a comment to triage</h2>
          <form className="mt-4 space-y-3" onSubmit={add}>
            <Input value={author} onChange={(e) => setAuthor(e.target.value)} placeholder="Author" required />
            <Textarea value={body} onChange={(e) => setBody(e.target.value)} placeholder="Comment" required />
            <Button type="submit">Save to inbox</Button>
          </form>
        </Card>
      </div>
    </AppShell>
  );
}
