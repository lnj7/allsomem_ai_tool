"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { ErrorState } from "@/components/ui/error-state";
import { productApi } from "@/lib/api/product";
import { ApiError } from "@/lib/api/client";

const steps = ["About You", "Expertise", "Audience", "Goals", "Platforms", "Brand Style"];
const platforms = ["Instagram", "YouTube", "Facebook", "LinkedIn", "X", "TikTok", "Threads", "Pinterest"];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [error, setError] = useState("");
  const [data, setData] = useState<Record<string, string>>({
    name: "",
    creator_type: "Individual Creator",
    introduction: "",
    skills: "",
    experience: "",
    subjects: "",
    interests: "",
    audience_who: "",
    geography: "",
    age_group: "",
    audience_problems: "",
    audience_interests: "",
    primary_goal: "build personal brand",
    secondary_goal: "grow audience",
    desired_audience_size: "",
    time_per_week: "",
    platforms: "Instagram,YouTube",
    preferred_language: "English",
    tone: "Friendly + Technical",
    personality: "Calm, Clear, Practical",
    content_style: "Educational",
    references: "",
  });

  useEffect(() => {
    productApi
      .onboarding()
      .then((result) => {
        setStep(result.step || 1);
        const incoming = Object.fromEntries(
          Object.entries(result.data || {}).map(([key, value]) => [key, Array.isArray(value) ? value.join(",") : String(value ?? "")]),
        );
        setData((current) => ({ ...current, ...incoming }));
      })
      .catch(() => router.replace("/login"));
  }, [router]);

  function update(key: string, value: string) {
    setData((current) => ({ ...current, [key]: value }));
  }

  async function persist(nextStep: number, complete = false) {
    setError("");
    try {
      await productApi.saveOnboarding({ step: nextStep, data, complete });
      if (complete) {
        router.push("/creator-profile");
        return;
      }
      setStep(nextStep);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save onboarding.");
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (step < 6) {
      await persist(step + 1);
      return;
    }
    await persist(6, true);
  }

  return (
    <div className="min-h-screen bg-[#f5f6fb] px-4 py-10">
      <div className="mx-auto grid max-w-5xl gap-6 md:grid-cols-[220px_1fr]">
        <aside className="rounded-3xl bg-white p-5">
          <p className="font-semibold text-[#0b1230]">CreatorOS</p>
          <ol className="mt-6 space-y-3 text-sm">
            {steps.map((label, index) => (
              <li key={label} className={index + 1 === step ? "font-semibold text-[#6d5efc]" : "text-slate-500"}>
                {index + 1}. {label}
              </li>
            ))}
          </ol>
        </aside>
        <Card>
          <p className="text-sm text-[#6d5efc]">Onboarding — Step {step} of 6</p>
          <h1 className="mt-2 text-2xl font-semibold">Tell us about yourself</h1>
          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            {step === 1 ? (
              <>
                <Input value={data.name} onChange={(e) => update("name", e.target.value)} placeholder="What's your name?" required />
                <Select value={data.creator_type} onChange={(e) => update("creator_type", e.target.value)}>
                  <option>Individual Creator</option>
                  <option>Business</option>
                  <option>Agency</option>
                </Select>
                <Textarea value={data.introduction} onChange={(e) => update("introduction", e.target.value)} placeholder="What do you want to be known for?" required />
              </>
            ) : null}
            {step === 2 ? (
              <>
                <Input value={data.skills} onChange={(e) => update("skills", e.target.value)} placeholder="Skills" required />
                <Input value={data.experience} onChange={(e) => update("experience", e.target.value)} placeholder="Experience" />
                <Input value={data.subjects} onChange={(e) => update("subjects", e.target.value)} placeholder="Subjects you know" />
                <Input value={data.interests} onChange={(e) => update("interests", e.target.value)} placeholder="Interests" />
              </>
            ) : null}
            {step === 3 ? (
              <>
                <Input value={data.audience_who} onChange={(e) => update("audience_who", e.target.value)} placeholder="Who do you want to reach?" required />
                <Input value={data.geography} onChange={(e) => update("geography", e.target.value)} placeholder="Geography" />
                <Input value={data.age_group} onChange={(e) => update("age_group", e.target.value)} placeholder="Age group" />
                <Textarea value={data.audience_problems} onChange={(e) => update("audience_problems", e.target.value)} placeholder="Audience problems" />
                <Textarea value={data.audience_interests} onChange={(e) => update("audience_interests", e.target.value)} placeholder="Audience interests" />
              </>
            ) : null}
            {step === 4 ? (
              <>
                <Select value={data.primary_goal} onChange={(e) => update("primary_goal", e.target.value)}>
                  <option>build personal brand</option>
                  <option>grow audience</option>
                  <option>build authority</option>
                  <option>generate leads</option>
                  <option>sell products</option>
                  <option>monetize content</option>
                </Select>
                <Input value={data.secondary_goal} onChange={(e) => update("secondary_goal", e.target.value)} placeholder="Secondary goal" />
                <Input value={data.desired_audience_size} onChange={(e) => update("desired_audience_size", e.target.value)} placeholder="Desired audience size" />
                <Input value={data.time_per_week} onChange={(e) => update("time_per_week", e.target.value)} placeholder="Hours available per week" />
              </>
            ) : null}
            {step === 5 ? (
              <div className="grid grid-cols-2 gap-2">
                {platforms.map((platform) => {
                  const selected = data.platforms.split(",").includes(platform);
                  return (
                    <button
                      type="button"
                      key={platform}
                      className={`rounded-xl border px-3 py-2 text-sm ${selected ? "border-[#6d5efc] bg-[#eef0ff]" : "border-slate-200"}`}
                      onClick={() => {
                        const current = data.platforms.split(",").filter(Boolean);
                        const next = selected ? current.filter((item) => item !== platform) : [...current, platform];
                        update("platforms", next.join(","));
                      }}
                    >
                      {platform}
                    </button>
                  );
                })}
              </div>
            ) : null}
            {step === 6 ? (
              <>
                <Input value={data.preferred_language} onChange={(e) => update("preferred_language", e.target.value)} placeholder="Preferred language" />
                <Input value={data.tone} onChange={(e) => update("tone", e.target.value)} placeholder="Tone" />
                <Input value={data.personality} onChange={(e) => update("personality", e.target.value)} placeholder="Personality" />
                <Select value={data.content_style} onChange={(e) => update("content_style", e.target.value)}>
                  <option>Educational</option>
                  <option>Entertaining</option>
                  <option>Inspirational</option>
                </Select>
                <Textarea value={data.references} onChange={(e) => update("references", e.target.value)} placeholder="Creator references" />
              </>
            ) : null}
            {error ? <ErrorState message={error} /> : null}
            <div className="flex justify-between">
              <Button type="button" variant="secondary" disabled={step === 1} onClick={() => setStep((value) => value - 1)}>
                Previous
              </Button>
              <Button type="submit">{step === 6 ? "Generate my profile" : "Next"}</Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
