"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ErrorState } from "@/components/ui/error-state";
import { APP_NAME } from "@creatoros/shared";
import { authApi } from "@/lib/api/product";
import { ApiError } from "@/lib/api/client";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await authApi.register({ email, password, full_name: fullName });
      router.push("/onboarding");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed.");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0b1230] px-4">
      <Card className="w-full max-w-md">
        <p className="text-sm font-semibold text-[#6d5efc]">{APP_NAME}</p>
        <h1 className="mt-2 text-2xl font-semibold">Start building your profile</h1>
        <form className="mt-6 space-y-4" onSubmit={onSubmit}>
          <Input required placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          <Input type="email" required placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input type="password" required minLength={8} placeholder="Password (8+ characters)" value={password} onChange={(e) => setPassword(e.target.value)} />
          {error ? <ErrorState message={error} /> : null}
          <Button type="submit" className="w-full">
            Create account
          </Button>
        </form>
        <p className="mt-4 text-sm text-slate-600">
          Already registered? <Link href="/login" className="text-[#6d5efc]">Login</Link>
        </p>
      </Card>
    </div>
  );
}
