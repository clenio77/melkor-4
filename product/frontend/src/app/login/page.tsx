"use client";
import { useState } from "react";
import { performLogin } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const tokens = await performLogin(email, password);
      localStorage.setItem("access", tokens.access);
      localStorage.setItem("refresh", tokens.refresh);
      router.push("/dashboard");
    } catch (e: unknown) {
      const msg = (e as { body?: { detail?: string } })?.body?.detail || "Erro ao autenticar";
      setError(String(msg));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <form onSubmit={onSubmit} className="space-y-4 w-full max-w-sm">
        <h1 className="text-2xl font-semibold">Login</h1>
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <div>
          <label className="block text-sm">Email</label>
          <input className="border rounded p-2 w-full" value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm">Senha</label>
          <input type="password" className="border rounded p-2 w-full" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <button className="bg-black text-white px-4 py-2 rounded" type="submit">Entrar</button>
      </form>
    </div>
  );
}

