"use client";
import React from "react";

export default function MetricsBar({ count, latency, providerUsed, providerEffective }: { count?: number; latency?: number; providerUsed?: string; providerEffective?: string; }) {
  return (
    <div className="text-xs text-gray-600">
      {typeof count === 'number' && <span className="mr-3">Resultados: {count}</span>}
      {typeof latency === 'number' && <span className="mr-3">Latência: {latency} ms</span>}
      {providerUsed && <span className="mr-3">provider_used: {providerUsed}</span>}
      {providerEffective && <span>provider_effective: {providerEffective}</span>}
    </div>
  );
}

