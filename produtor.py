import os

from produtor2 import (
    build_queries,
    search_and_collect_leads,
    write_csv,
    SERPAPI_API_KEY,
    INCLUDE_SOCIAL,
)


if __name__ == "__main__":
    output_file = os.getenv("OUTPUT_FILE", "melhores_leads_qualificados.csv")

    # Usa a versão aprimorada do gerador de consultas
    queries_to_run = build_queries(include_social=INCLUDE_SOCIAL)

    # Executa buscas e escreve CSV com campos enriquecidos
    all_leads = search_and_collect_leads(queries_to_run, SERPAPI_API_KEY)
    write_csv(output_file, all_leads)

    print("\nBusca por leads qualificados finalizada.")
    print(f"Resultados salvos em '{output_file}'. Revise os contatos antes de usar.")