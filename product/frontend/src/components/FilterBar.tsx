"use client";
import React from "react";
import ProviderSelector from "./ProviderSelector";

export default function FilterBar({
  tema, setTema,
  tribunal, setTribunal,
  vinculante, setVinculante,
  fase, setFase,
  bloco, setBloco,
  dispositivo, setDispositivo,
  tese, setTese,
  provider, setProvider,
  onSearch,
}: {
  tema: string; setTema: (v: string) => void;
  tribunal: string; setTribunal: (v: string) => void;
  vinculante: string; setVinculante: (v: string) => void;
  fase: string; setFase: (v: string) => void;
  bloco: string; setBloco: (v: string) => void;
  dispositivo: string; setDispositivo: (v: string) => void;
  tese: string; setTese: (v: string) => void;
  provider: "simple" | "graph" | "hybrid"; setProvider: (v: "simple" | "graph" | "hybrid") => void;
  onSearch: () => void;
}) {
  return (
    <div className="flex flex-wrap gap-2 items-center">
      <input className="border p-2 rounded" placeholder="Tema" value={tema} onChange={e => setTema(e.target.value)} />
      <input className="border p-2 rounded" placeholder="Tribunal" value={tribunal} onChange={e => setTribunal(e.target.value)} />
      <select className="border p-2 rounded" value={vinculante} onChange={e => setVinculante(e.target.value)}>
        <option value="">Vinculante?</option>
        <option value="true">Sim</option>
        <option value="false">Não</option>
      </select>
      <input className="border p-2 rounded w-40" placeholder="Fase" value={fase} onChange={e => setFase(e.target.value)} />
      <input className="border p-2 rounded w-28" placeholder="Bloco (número)" value={bloco} onChange={e => setBloco(e.target.value)} />
      <input className="border p-2 rounded w-56" placeholder="Dispositivo (ex: CPP 158-B)" value={dispositivo} onChange={e => setDispositivo(e.target.value)} />
      <input className="border p-2 rounded w-56" placeholder="Tese (ex: nulidade por falta de defesa técnica)" value={tese} onChange={e => setTese(e.target.value)} />
      <ProviderSelector value={provider} onChange={setProvider} />
      <button onClick={onSearch} className="px-4 py-2 bg-blue-600 text-white rounded">Buscar</button>
    </div>
  );
}

