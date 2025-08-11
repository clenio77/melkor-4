"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { sugestoesJurisprudencia, JurisItem, JurisResponse } from "@/lib/juris";
import { getProfile } from "@/lib/api";
import FilterBar from "@/components/FilterBar";
import MetricsBar from "@/components/MetricsBar";

export default function JurisprudenciaPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [tema, setTema] = useState("");
  const [tribunal, setTribunal] = useState("");
  const [items, setItems] = useState<JurisItem[]>([]);
  const [provider, setProvider] = useState<"simple" | "graph" | "hybrid">("simple");
  const [providerUsed, setProviderUsed] = useState<string>("");
  const [traceId, setTraceId] = useState<string>("");
  const [resState, setResState] = useState<JurisResponse | null>(null);
  const [vinculante, setVinculante] = useState<string>("");
  const [fase, setFase] = useState<string>("");
  const [bloco, setBloco] = useState<string>("");
  const [dispositivo, setDispositivo] = useState<string>("");
  const [tese, setTese] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = localStorage.getItem("access");
    if (!t) {
      router.push("/login");
      return;
    }
    setToken(t);
    // simple auth check
    getProfile(t).catch(() => router.push("/login"));
  }, [router]);

  async function load() {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await sugestoesJurisprudencia(token, {
        tema: tema || undefined,
        tribunal: tribunal || undefined,
        vinculante: vinculante || undefined,
        topk: 10,
        provider,
      });
      setItems(res.items);
      setProviderUsed(res.provider_used);
      setTraceId(res.trace_id);
      setResState(res);
    } catch (e) {
      const err = e as { message?: string };
      setError(err?.message || "Erro ao carregar sugestões");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (token) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Jurisprudência sugerida</h1>
      <FilterBar
        tema={tema} setTema={setTema}
        tribunal={tribunal} setTribunal={setTribunal}
        vinculante={vinculante} setVinculante={setVinculante}
        fase={fase} setFase={setFase}
        bloco={bloco} setBloco={setBloco}
        provider={provider} setProvider={setProvider}
        dispositivo={dispositivo} setDispositivo={setDispositivo}
        tese={tese} setTese={setTese}
        onSearch={load}
      />
      <MetricsBar count={resState?.count} latency={resState?.latency_ms} providerUsed={providerUsed} providerEffective={resState?.provider_effective} />
      {traceId && (
        <div className="text-xs text-gray-400">trace_id: {traceId}</div>
      )}
      {loading && <div>Carregando...</div>}
      {error && <div className="text-red-600">{error}</div>}
      <ul className="space-y-3">
        {items.map((it) => (
          <li key={it.id} className="border rounded p-3">
            <div className="font-medium flex items-center gap-2">
              <span>{it.titulo}</span>
              {it.vinculante ? <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">vinculante</span> : null}
            </div>
            <div className="text-sm text-gray-600">{it.tribunal} {it.data ? `• ${it.data}` : ""}</div>
            {it.temas?.length ? <div className="text-xs text-gray-500">Tema: {it.temas.join(", ")}</div> : null}
            {it.dispositivos_citados?.length ? <div className="text-xs text-gray-500">Dispositivos: {it.dispositivos_citados.join(", ")}</div> : null}
            {it.link ? <a href={it.link} target="_blank" rel="noreferrer" className="text-blue-700 text-sm">Ver decisão</a> : null}
          </li>
        ))}
      </ul>
    </div>
  );
}

