export type Estatisticas = {
  totalProcessos: number;
  totalAnalises: number;
  totalUsuarios: number;
  ultimasAtividades?: Array<{ tipo: string; descricao: string; data: string }>;
};

export * from "./processo";

