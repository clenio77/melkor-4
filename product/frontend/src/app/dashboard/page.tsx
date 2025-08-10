"use client";
import { useEffect, useState } from "react";
import { getEstatisticas } from "@/lib/api";
import type { Estatisticas } from "@/types";
import Link from "next/link";

export default function DashboardPage() {
  const [stats, setStats] = useState<Estatisticas | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const access = localStorage.getItem("access");
    if (!access) return;
    getEstatisticas(access)
      .then((data) => setStats(data as Estatisticas))
      .catch((e: unknown) => {
        const msg = (e as { body?: { error?: string } })?.body?.error || "Erro";
        setError(String(msg));
      });
  }, []);

  return (
    <div className="p-6 space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <Link href="/processos" className="underline">Ir para Processos</Link>
      </div>
      {error && <div className="text-red-600 text-sm">{error}</div>}
      {stats ? (
        <pre className="bg-gray-50 p-4 rounded border overflow-auto">{JSON.stringify(stats, null, 2)}</pre>
      ) : (
        <div>Carregando...</div>
      )}
    </div>
  );
}

