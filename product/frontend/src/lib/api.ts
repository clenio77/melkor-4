export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

export async function apiFetch<T = unknown>(path: string, opts: RequestInit = {}, token?: string): Promise<T> {
  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  // Only set JSON content-type when body is not FormData
  const body: unknown = (opts as { body?: unknown }).body;
  if (!body || !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers: { ...headers, ...(opts.headers as Record<string, string> | undefined) } });
  const isJson = res.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await res.json() : await res.text();
  if (!res.ok) throw new ApiError(`HTTP ${res.status}`, res.status, data);
  return data as T;
}

export interface LoginResponse { access: string; refresh: string }
export async function login(email: string, password: string) {
  return apiFetch<LoginResponse>("/api/auth/login/", { method: "POST", body: JSON.stringify({ username: email, password }) });
}

export interface RefreshResponse { access: string }
export async function refresh(refreshToken: string) {
  return apiFetch<RefreshResponse>("/api/auth/refresh/", { method: "POST", body: JSON.stringify({ refresh: refreshToken }) });
}

export async function registerUser(data: Record<string, unknown>) {
  return apiFetch("/api/auth/register/", { method: "POST", body: JSON.stringify(data) });
}

export async function getProfile(token: string) {
  return apiFetch("/api/auth/profile/", { method: "GET" }, token);
}

export async function getEstatisticas(token: string) {
  // backend route is /api/estatisticas/dashboard/
  return apiFetch("/api/estatisticas/dashboard/", { method: "GET" }, token);
}

export async function listProcessos(token: string) {
  return apiFetch("/api/processos/", { method: "GET" }, token);
}

export async function createProcesso(token: string, data: { titulo: string; numero_processo?: string | null }) {
  return apiFetch("/api/processos/", { method: "POST", body: JSON.stringify(data) }, token);
}

export async function listDocumentosDoProcesso(token: string, processoId: string | number) {
  return apiFetch(`/api/processos/${processoId}/documentos/`, { method: "GET" }, token);
}

export async function uploadDocumento(token: string, payload: { processo: string; tipo_documento: string; file: File; }) {
  const form = new FormData();
  form.append("arquivo_original", payload.file);
  form.append("tipo_documento", payload.tipo_documento);
  form.append("processo", payload.processo);
  const res = await fetch(`${API_BASE}/api/documentos/`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  const data = await res.json();
  if (!res.ok) throw new ApiError(`HTTP ${res.status}`, res.status, data);
  return data as unknown;
}

export async function iniciarAnalise(token: string, data: { processo_id: string | number; modo_analise: "individual" | "completa" | "personalizada"; bloco?: number; subetapa?: number; blocos_selecionados?: number[]; }) {
  return apiFetch("/api/analises/iniciar/", { method: "POST", body: JSON.stringify(data) }, token);
}

export async function getAnaliseResultados(token: string, sessaoId: string) {
  return apiFetch(`/api/analises/${sessaoId}/resultados/`, { method: "GET" }, token);
}

export async function getAnaliseResumo(token: string, sessaoId: string) {
  return apiFetch(`/api/analises/${sessaoId}/resumo/`, { method: "GET" }, token);
}

export async function getStatusSeguranca(token: string) {
  return apiFetch("/api/ai/status-seguranca/", { method: "GET" }, token);
}

export async function getMenuOpcoes(token: string) {
  return apiFetch("/api/menu/opcoes/", { method: "GET" }, token);
}

