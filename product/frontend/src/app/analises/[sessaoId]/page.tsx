"use client";
import { useEffect, useState } from "react";
import { getAnaliseResultados, getAnaliseResumo } from "@/lib/api";
import { useParams } from "next/navigation";

export default function AnaliseResultados() {
  const p = useParams<{ sessaoId: string }>();
  const sessaoId = p?.sessaoId as string;
  const [resultados, setResultados] = useState<unknown>(null);
  const [resumo, setResumo] = useState<unknown>(null);

  useEffect(() => {
    const access = localStorage.getItem("access");
    if (!access || !sessaoId) return;
    getAnaliseResultados(access, sessaoId).then(setResultados).catch(()=>{});
    getAnaliseResumo(access, sessaoId).then(setResumo).catch(()=>{});
  }, [sessaoId]);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Resultados</h1>
      <div>
        <h2 className="font-medium">Resumo</h2>
        <pre className="bg-gray-50 p-3 text-xs overflow-auto border rounded">{JSON.stringify(resumo, null, 2)}</pre>
      </div>
      <div>
        <h2 className="font-medium">Detalhes</h2>
        <pre className="bg-gray-50 p-3 text-xs overflow-auto border rounded">{JSON.stringify(resultados, null, 2)}</pre>
      </div>
    </div>
  );
}

