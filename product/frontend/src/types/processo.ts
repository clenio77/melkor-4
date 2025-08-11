export type Documento = {
  id: number | string;
  nome_arquivo: string;
  tamanho_formatado?: string;
};

export type Processo = {
  id: number | string;
  titulo: string;
  numero_processo?: string | null;
};

export type MenuOpcoes = Record<string, { titulo: string; subetapas: number }>;

