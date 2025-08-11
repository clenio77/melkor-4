"use client";
import React from "react";

type Provider = "simple" | "graph" | "hybrid";

export default function ProviderSelector({ value, onChange }: { value: Provider; onChange: (v: Provider) => void }) {
  return (
    <div className="flex items-center gap-2">
      <label className="text-sm text-gray-700">Provider:</label>
      <select className="border p-1 rounded" value={value} onChange={(e) => onChange(e.target.value as Provider)}>
        <option value="simple">simple</option>
        <option value="graph">graph</option>
        <option value="hybrid">hybrid</option>
      </select>
    </div>
  );
}

