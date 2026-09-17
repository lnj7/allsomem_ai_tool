import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const steps = [
  ["Start", "/register"],
  ["Build Profile", "/onboarding"],
  ["Plan", "/content-calendar"],
  ["Create", "/content-studio"],
  ["Grow", "/growth"],
];

export default function JourneyPage() {
  return (
    <AppShell title="Creator Journey">
      <Card>
        <h2 className="text-xl font-semibold">From 0 to a powerful profile</h2>
        <div className="mt-6 grid gap-3 md:grid-cols-5">
          {steps.map(([label, href], index) => (
            <Link key={label} href={href} className="rounded-2xl bg-slate-50 p-4 text-center">
              <p className="text-xs text-[#6d5efc]">{index + 1}</p>
              <p className="mt-2 font-medium">{label}</p>
            </Link>
          ))}
        </div>
        <Link href="/onboarding" className="mt-6 inline-block">
          <Button>Continue</Button>
        </Link>
      </Card>
    </AppShell>
  );
}
