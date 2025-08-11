import { apiFetch } from "./api";

export interface JurisItem {
  id: string;
  titulo: string;
  tribunal?: string | null;
  data?: string | null;
  temas?: string[] | null;
  link?: string | null;
  vinculante?: boolean | null;
  dispositivos_citados?: string[] | null;
  score?: number | null;
}

export interface JurisResponse {
  items: JurisItem[];
  provider_used: string;
  trace_id: string;
  // Optional telemetry fields returned by backend
  count?: number;
  latency_ms?: number;
  provider_effective?: string;
  filters?: Record<string, unknown>;
}

export async function buscarJurisprudencia(token: string, params: { q?: string; tema?: string; tribunal?: string; vinculante?: string; topk?: number; provider?: string }) {
  const s = new URLSearchParams();
  if (params.q) s.append("q", params.q);
  if (params.tema) s.append("tema", params.tema);
  if (params.tribunal) s.append("tribunal", params.tribunal);
  if (params.vinculante) s.append("vinculante", params.vinculante);
  if (params.topk) s.append("topk", String(params.topk));
  if (params.provider) s.append("provider", params.provider);
  return apiFetch<JurisResponse>(`/api/ai/jurisprudencia/search/?${s.toString()}`, { method: "GET" }, token);
}

export async function sugestoesJurisprudencia(token: string, params: { tema?: string; tribunal?: string; vinculante?: string; fase?: string; bloco?: string; dispositivo?: string; tese?: string; topk?: number; provider?: string }) {
  const s = new URLSearchParams();
  if (params.tema) s.append("tema", params.tema);
  if (params.tribunal) s.append("tribunal", params.tribunal);
  if (params.vinculante) s.append("vinculante", params.vinculante);
  if (params.fase) s.append("fase", params.fase);
  if (params.bloco) s.append("bloco", params.bloco);
  if (params.dispositivo) s.append("dispositivo", params.dispositivo);
  if (params.tese) s.append("tese", params.tese);
  if (params.topk) s.append("topk", String(params.topk));
  if (params.provider) s.append("provider", params.provider);
  return apiFetch<JurisResponse>(`/api/ai/jurisprudencia/sugestoes/?${s.toString()}`, { method: "GET" }, token);
}

