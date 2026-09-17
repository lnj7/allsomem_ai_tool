"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ErrorState } from "@/components/ui/error-state";
import { authApi } from "@/lib/api/product";
import { ApiError } from "@/lib/api/client";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await authApi.login({ email, password });
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed.");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0b1230] px-4">
      <Card className="w-full max-w-md">
        <p className="text-sm font-semibold text-[#6d5efc]">CreatorOS</p>
        <h1 className="mt-2 text-2xl font-semibold">Welcome back</h1>
        <form className="mt-6 space-y-4" onSubmit={onSubmit}>
          <Input type="email" required placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input type="password" required placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          {error ? <ErrorState message={error} /> : null}
          <Button type="submit" className="w-full">
            Login
          </Button>
        </form>
        <p className="mt-4 text-sm text-slate-600">
          New here? <Link href="/register" className="text-[#6d5efc]">Create an account</Link>
        </p>
      </Card>
    </div>
  );
}
