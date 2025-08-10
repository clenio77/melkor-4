"use client";
import { useEffect, useState } from "react";
import { getStatusSeguranca } from "@/lib/api";

export default function SegurancaPage() {
  const [status, setStatus] = useState<unknown>(null);

  useEffect(() => {
    const access = localStorage.getItem("access");
    if (!access) return;
    getStatusSeguranca(access).then(setStatus).catch(()=>{});
  }, []);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Status de Segurança</h1>
      <pre className="bg-gray-50 p-3 text-xs overflow-auto border rounded">{JSON.stringify(status, null, 2)}</pre>
    </div>
  );
}

