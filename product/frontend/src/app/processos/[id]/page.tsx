"use client";
import { useEffect, useState, useCallback } from "react";
import { listDocumentosDoProcesso, uploadDocumento, iniciarAnalise, getMenuOpcoes } from "@/lib/api";
import type { Documento, MenuOpcoes } from "@/types";
import Link from "next/link";

import { useParams } from "next/navigation";

export default function ProcessoDetail() {
  const params = useParams<{ id: string }>();
  const id = params?.id as string;
  const [docs, setDocs] = useState<Documento[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [tipo, setTipo] = useState("geral");
  const [sessao, setSessao] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  const [menu, setMenu] = useState<MenuOpcoes | null>(null);
  const [blocoSel, setBlocoSel] = useState<number>(1);
  const [subetapaSel, setSubetapaSel] = useState<number>(1);

  const loadDocs = useCallback(async () => {
    setError(null);
    try {
      const access = localStorage.getItem("access")!;
      const data = await listDocumentosDoProcesso(access, id);
      setDocs(data as Documento[]);
    } catch (e: unknown) {
      const msg = (e as { body?: { error?: string } })?.body?.error || "Erro";
      setError(String(msg));
    }
  }, [id]);

  useEffect(() => { loadDocs(); }, [loadDocs]);

  useEffect(() => {
    const access = localStorage.getItem("access");
    if (!access) return;
    getMenuOpcoes(access).then((d)=>setMenu(d as MenuOpcoes)).catch(()=>{});
  }, []);

  const onUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    try {
      const access = localStorage.getItem("access")!;
      await uploadDocumento(access, { processo: id, tipo_documento: tipo, file });
      setFile(null);
      await loadDocs();
    } catch (e: unknown) {
      const msg = (e as { body?: { error?: string } })?.body?.error || "Erro no upload";
      setError(String(msg));
    }
  };

  const onAnalisar = async (modo: "individual"|"completa", bloco?: number, subetapa?: number) => {
    try {
      const access = localStorage.getItem("access")!;
      const payload: { processo_id: string; modo_analise: "individual"|"completa"; bloco?: number; subetapa?: number } = { processo_id: id, modo_analise: modo };
      if (modo === "individual") { payload.bloco = bloco; payload.subetapa = subetapa; }
      const resp = await iniciarAnalise(access, payload);
      setSessao(resp as unknown);
    } catch (e: unknown) {
      const msg = (e as { body?: { error?: string } })?.body?.error || "Erro ao iniciar análise";
      setError(String(msg));
    }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Processo {id}</h1>
        <Link href="/processos" className="underline">Voltar</Link>
      </div>
      {error && <div className="text-red-600 text-sm">{error}</div>}

      <section className="space-y-2">
        <h2 className="font-medium">Documentos</h2>
        <form onSubmit={onUpload} className="space-x-2">
          <input type="file" accept="application/pdf" onChange={(e)=> setFile(e.target.files?.[0]||null)} />
          <select className="border p-1" value={tipo} onChange={(e)=> setTipo(e.target.value)}>
            <option value="geral">Geral</option>
            <option value="inquerito">Inquérito</option>
          </select>
          <button className="bg-black text-white px-3 py-2 rounded" type="submit">Upload</button>
        </form>
        <ul className="space-y-2">
          {docs.map((d)=> (
            <li key={String(d.id)} className="border rounded p-2 text-sm">
              {d.nome_arquivo} — {d.tamanho_formatado}
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-2">
        <h2 className="font-medium">Análise</h2>
        <div className="space-x-2">
          <button className="border px-3 py-2" onClick={() => onAnalisar("completa")}>Análise Completa</button>
        </div>
        {menu && (
          <div className="text-xs text-gray-700 space-y-2">
            <div className="font-medium mt-2">Blocos disponíveis</div>
            <ul className="list-disc pl-5">
              {Object.entries(menu).map(([k, v]) => (
                <li key={k}>{k} — {v.titulo} ({v.subetapas} subetapas)</li>
              ))}
            </ul>
            <div className="flex items-center gap-2">
              <label>Bloco</label>
              <select className="border p-1" value={blocoSel} onChange={(e)=> setBlocoSel(parseInt(e.target.value))}>
                {Object.keys(menu).filter(k=>k!=='5').map((k)=> (
                  <option key={k} value={k}>{k}</option>
                ))}
              </select>
              <label>Subetapa</label>
              <input type="number" min={1} className="border p-1 w-20" value={subetapaSel} onChange={(e)=> setSubetapaSel(parseInt(e.target.value||'1'))} />
              <button className="border px-3 py-2" onClick={()=> onAnalisar("individual", blocoSel, subetapaSel)}>Análise Individual</button>
            </div>
          </div>
        )}
        {Boolean(sessao) && (
          <pre className="bg-gray-50 p-3 rounded border overflow-auto text-xs">{JSON.stringify(sessao as object, null, 2)}</pre>
        )}
      </section>
    </div>
  );
}

