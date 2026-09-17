import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0b1230] text-white">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <p className="text-lg font-semibold">CreatorOS</p>
        <div className="flex items-center gap-3">
          <Link href="/login" className="text-sm text-slate-300">
            Login
          </Link>
          <Link href="/register">
            <Button>Get Started</Button>
          </Link>
        </div>
      </header>
      <main className="mx-auto grid max-w-6xl gap-12 px-6 pb-24 pt-10 lg:grid-cols-2 lg:items-center">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-[#b7a8ff]">
            Your AI Creator Manager
          </p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight sm:text-6xl">
            Build your personal brand across every social platform from one place.
          </h1>
          <p className="mt-5 max-w-xl text-slate-300">
            Define your identity, create better content, schedule with approval, and learn from
            real performance. You stay in control.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link href="/register">
              <Button className="w-full sm:w-auto">Start Building My Profile</Button>
            </Link>
            <Link href="/login">
              <Button variant="secondary" className="w-full sm:w-auto text-slate-800">
                Watch Demo
              </Button>
            </Link>
          </div>
        </div>
        <div className="rounded-[2rem] bg-white/10 p-6 backdrop-blur">
          <p className="text-sm text-slate-300">One AI. Every platform. Your growth.</p>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
            {["Instagram", "YouTube", "LinkedIn", "TikTok", "X", "Pinterest"].map((name) => (
              <div key={name} className="rounded-2xl bg-white/10 px-4 py-3">
                {name}
              </div>
            ))}
          </div>
        </div>
      </main>
      <section className="mx-auto grid max-w-6xl gap-4 px-6 pb-20 md:grid-cols-4">
        {[
          ["Create Content", "Plan and generate content with AI."],
          ["Schedule & Publish", "Manage your social presence from one place."],
          ["Track Performance", "Understand what works and improve continuously."],
          ["Monetize", "Turn attention into a durable creator business."],
        ].map(([title, body]) => (
          <div key={title} className="rounded-3xl bg-white p-5 text-[#0b1230]">
            <h2 className="font-semibold">{title}</h2>
            <p className="mt-2 text-sm text-slate-600">{body}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
