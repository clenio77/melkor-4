"use client";
import { useEffect, useState } from "react";
import { createProcesso, listProcessos } from "@/lib/api";
import type { Processo } from "@/types";
import Link from "next/link";

export default function ProcessosPage() {
  const [items, setItems] = useState<Processo[]>([]);
  const [form, setForm] = useState<{ titulo: string; numero_processo?: string | null }>({ titulo: "", numero_processo: "" });
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setError(null);
    try {
      const access = localStorage.getItem("access")!;
      const data = await listProcessos(access);
      setItems(data as Processo[]);
    } catch (e: unknown) {
      const msg = (e as { body?: { error?: string } })?.body?.error || "Erro ao carregar";
      setError(String(msg));
    }
  };

  useEffect(() => { load(); }, []);

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const access = localStorage.getItem("access")!;
      await createProcesso(access, form);
      setForm({ titulo: "", numero_processo: "" });
      await load();
    } catch (e: unknown) {
      const msg = (e as { body?: { error?: string } })?.body?.error || "Erro ao criar";
      setError(String(msg));
    }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Processos</h1>
        <Link href="/dashboard" className="underline">Voltar</Link>
      </div>
      {error && <div className="text-red-600 text-sm">{error}</div>}
      <form onSubmit={onCreate} className="space-x-2">
        <input placeholder="Título" className="border p-2" value={form.titulo} onChange={e=>setForm({...form, titulo:e.target.value})} />
        <input placeholder="Número" className="border p-2" value={form.numero_processo ?? ""} onChange={e=>setForm({...form, numero_processo:e.target.value})} />
        <button className="bg-black text-white px-3 py-2 rounded" type="submit">Criar</button>
      </form>
      <ul className="space-y-2">
        {items.map((p)=> (
          <li key={String(p.id)} className="border rounded p-3">
            <div className="font-medium">{p.titulo}</div>
            <div className="text-sm text-gray-600">Nº {p.numero_processo || "—"}</div>
            <Link className="underline text-sm" href={`/processos/${p.id}`}>Abrir</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

