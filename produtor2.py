import os
import re
import csv
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

import serpapi
import requests
from bs4 import BeautifulSoup
import argparse
import json
import logging
import threading
import random

# ==========================
# Configurações e parâmetros
# ==========================

def _sanitize_api_key(raw: Optional[str]) -> Optional[str]:
    if raw is None:
        return None
    key = raw.strip().strip('"').strip("'")
    # Remove prefixo indevido do tipo SERPAPI_API_KEY=...
    if key.lower().startswith("serpapi_api_key="):
        key = key.split("=", 1)[1].strip()
    # Remove possíveis escapes triviais
    key = key.replace("%0A", "").replace("\n", "").replace("\r", "")
    return key

# Chave da API via variável de ambiente (com sanitização para evitar 401)
SERPAPI_API_KEY = _sanitize_api_key(os.getenv("SERPAPI_API_KEY"))
if not SERPAPI_API_KEY:
    raise RuntimeError("Defina a variável de ambiente SERPAPI_API_KEY com sua chave da SerpAPI.")

# Controle via env vars (com padrões razoáveis)
MAX_WORKERS = int(os.getenv("SEARCH_MAX_WORKERS", "3"))
RESULTS_PER_PAGE = int(os.getenv("SEARCH_RESULTS_PER_PAGE", "10"))  # até 100
MAX_PAGES = int(os.getenv("SEARCH_MAX_PAGES", "1"))  # páginas por consulta (start em 0,10,20,...)
INCLUDE_SOCIAL = os.getenv("SEARCH_INCLUDE_SOCIAL", "true").lower() in {"1", "true", "yes"}
GOOGLE_DOMAIN = os.getenv("SEARCH_GOOGLE_DOMAIN", "google.com.br")
LANG = os.getenv("SEARCH_LANG", "pt-BR")
COUNTRY = os.getenv("SEARCH_COUNTRY", "br")
ENRICH_PAGES = os.getenv("ENRICH_PAGES", "true").lower() in {"1", "true", "yes"}
ENRICH_MAX_WORKERS = int(os.getenv("ENRICH_MAX_WORKERS", "5"))
ENRICH_TIMEOUT_SEC = float(os.getenv("ENRICH_TIMEOUT_SEC", "8"))
ENRICH_MAX_BYTES = int(os.getenv("ENRICH_MAX_BYTES", "400000"))  # ~400KB por página
SKIP_ENRICH_DOMAINS = {
    d.strip().lower()
    for d in (os.getenv(
        "ENRICH_SKIP_DOMAINS",
        "facebook.com, instagram.com, linkedin.com, twitter.com, x.com, youtube.com, whatsapp.com, tiktok.com",
    ).split(","))
    if d.strip()
}
SEARCH_TBS = os.getenv("SEARCH_TBS", "")  # exemplo: qdr:y para 1 ano; qdr:m para 1 mês
INCLUDE_DOMAINS = {
    d.strip().lower() for d in (os.getenv("INCLUDE_DOMAINS", "").split(",")) if d.strip()
}
EXCLUDE_DOMAINS = {
    d.strip().lower() for d in (os.getenv("EXCLUDE_DOMAINS", "").split(",")) if d.strip()
}
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
SAVE_JSON = os.getenv("SAVE_JSON", "false").lower() in {"1", "true", "yes"}
JSON_PATH = os.getenv("JSON_PATH", "leads.json")
TOP_PER_QUERY = int(os.getenv("TOP_PER_QUERY", "0"))  # 0 = sem limite

# Rate limiting e retries contra 429
SERPAPI_MIN_DELAY_SEC = float(os.getenv("SERPAPI_MIN_DELAY_SEC", "2.0"))
SERPAPI_MAX_RETRIES = int(os.getenv("SERPAPI_MAX_RETRIES", "3"))
SERPAPI_BACKOFF_BASE = float(os.getenv("SERPAPI_BACKOFF_BASE", "2.0"))
SERPAPI_JITTER_SEC = float(os.getenv("SERPAPI_JITTER_SEC", "0.5"))

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ==========================
# Dados base
# ==========================

# Lista de organizações e termos-chave que provavelmente contêm dados de contato
keywords_e_entidades: List[str] = [
    '"Coopercisco" contato',
    '"Emater-MG" Uberlândia "contato produtor"',
    '"Sindicato Rural de Uberlândia" diretoria',
    '"Associação dos Produtores de Queijo Minas Artesanal" "perfil produtor"',
    'produtor rural "telefone" "Triângulo Mineiro"',
    'agricultor "redes sociais" "Monte Alegre de Minas"',
    '"Queijo Minas Artesanal" "produtores" "Uberlândia"',
    'Cooperativa agro "membros" "Araguari"',
    'entrevista "produtor de abacaxi" "Monte Alegre de Minas"',
]

# Cidades-alvo (usadas para gerar consultas específicas e/ou localização)
cidades: List[str] = [
    "Uberlândia",
    "Tupaciguara",
    "Monte Alegre de Minas",
    "Araguari",
]

# Sugestões de location reconhecíveis pelo Google/SerpAPI para geolocalizar os resultados
city_to_location: Dict[str, str] = {
    "Uberlândia": "Uberlândia - State of Minas Gerais, Brazil",
    "Tupaciguara": "Tupaciguara - State of Minas Gerais, Brazil",
    "Monte Alegre de Minas": "Monte Alegre de Minas - State of Minas Gerais, Brazil",
    "Araguari": "Araguari - State of Minas Gerais, Brazil",
}


# ==========================
# Utilidades
# ==========================

def normalize_url(url: str) -> str:
    """Remove parâmetros de rastreamento comuns para facilitar deduplicação."""
    if not url:
        return url
    try:
        parsed = urllib.parse.urlsplit(url)
        # Remove parâmetros UTM e afins
        query_params = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        filtered = [(k, v) for k, v in query_params if not k.lower().startswith("utm")]
        new_query = urllib.parse.urlencode(filtered)
        normalized = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, new_query, ""))
        return normalized.rstrip("/")
    except Exception:
        return url


def extract_contacts(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extrai telefone e e-mail de um trecho de texto (heurístico)."""
    if not text:
        return None, None

    # Telefone brasileiro simples (pode pegar algumas variações)
    phone_match = re.search(r"(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?(?:9\s*)?\d{4}[-\s]?\d{4}", text)
    phone = phone_match.group(0) if phone_match else None

    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    email = email_match.group(0) if email_match else None

    return phone, email


def get_source_domain(url: str) -> Optional[str]:
    if not url:
        return None
    try:
        return urllib.parse.urlsplit(url).netloc
    except Exception:
        return None


def confidence_score(lead: Dict) -> int:
    """Pontua heurística simples para priorização de leads."""
    score = 0
    if lead.get("phone"):
        score += 3
    if lead.get("email"):
        score += 3
    domain = (lead.get("source_domain") or "").lower()
    if domain.endswith(".gov.br") or domain.endswith(".org.br"):
        score += 1
    if lead.get("source_type") == "local":
        score += 1
    if lead.get("city"):
        score += 1
    # bônus por perfis sociais encontrados
    for key in ("instagram", "facebook", "linkedin", "youtube", "tiktok", "whatsapp"):
        if lead.get(key):
            score += 1
    return score


# ==========================
# Geração de consultas
# ==========================

def build_queries(include_social: bool = True) -> List[Tuple[str, Optional[str]]]:
    """
    Gera pares (query, location) para execução.
    - Gera variações por cidade (mais precisas que um OR genérico)
    - Inclui filtros para Facebook/Instagram se desejado
    """
    queries: List[Tuple[str, Optional[str]]] = []
    def clean_term_for_social(term: str) -> str:
        # remove palavras que reduzem recall em sociais
        cleaned = re.sub(r"\b(contato|telefone|redes\s+sociais|perfil\s+produtor)\b", "", term, flags=re.I)
        # normaliza espaços
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    for termo in keywords_e_entidades:
        # por cidade alvo
        for cidade in cidades:
            q_base = f'{termo} "{cidade}"'
            location = city_to_location.get(cidade)
            queries.append((q_base, location))
            if include_social:
                # sociais com cidade (mantemos, mas sem imposição de location/tbs na busca)
                neg = "-inurl:explore -inurl:accounts -inurl:login -inurl:share -inurl:reel"
                queries.append((f"{q_base} site:facebook.com", location))
                queries.append((f"{q_base} site:instagram.com {neg}", location))
                queries.append((f"{q_base} site:linkedin.com", location))
                # Mais abrangentes, sem cidade, para aumentar recall
                t_clean = clean_term_for_social(termo)
                queries.append((f"{t_clean} site:facebook.com", None))
                queries.append((f"{t_clean} site:instagram.com {neg}", None))
                queries.append((f"{t_clean} site:linkedin.com", None))
                # variantes com estado
                queries.append((f"{t_clean} MG site:instagram.com {neg}", None))
                queries.append((f"{t_clean} Minas Gerais site:facebook.com", None))
                # TikTok/YouTube opcional: menor recall, mas útil
                queries.append((f"{t_clean} site:tiktok.com", None))
                queries.append((f"{t_clean} site:youtube.com", None))
    return queries


# ==========================
# Busca na SerpAPI (com paralelismo)
# ==========================

def _fetch_serp_page(client: serpapi.Client, query: str, location: Optional[str], start: int, engine: str = "google", apply_tbs: bool = True) -> Dict:
    params = {
        "engine": engine,
        "q": query,
        "hl": LANG,
        "gl": COUNTRY,
        "google_domain": GOOGLE_DOMAIN,
        "num": str(RESULTS_PER_PAGE),
        "start": str(start),
    }
    if location:
        params["location"] = location
    if SEARCH_TBS and apply_tbs and engine == "google":
        params["tbs"] = SEARCH_TBS
    return _search_with_retry(client, params)


_rate_lock = threading.Lock()
_last_request_ts: float = 0.0


def _rate_limited_call(client: serpapi.Client, params: Dict) -> Dict:
    global _last_request_ts
    # enforce min delay across threads
    with _rate_lock:
        now = time.time()
        wait = max(0.0, (_last_request_ts + SERPAPI_MIN_DELAY_SEC) - now)
        if wait > 0:
            time.sleep(wait)
        # jitter para evitar rajadas sincronizadas
        if SERPAPI_JITTER_SEC > 0:
            time.sleep(random.uniform(0.0, SERPAPI_JITTER_SEC))
        result = client.search(params).as_dict()
        _last_request_ts = time.time()
        return result


def _is_rate_limited_error(err: Exception, result: Optional[Dict]) -> bool:
    text = str(err) if err else ""
    if "429" in text or "Too Many Requests" in text:
        return True
    if isinstance(result, dict):
        msg = str(result.get("error", ""))
        if "Too Many Requests" in msg or "Rate limit" in msg:
            return True
    return False


def _search_with_retry(client: serpapi.Client, params: Dict) -> Dict:
    attempt = 0
    last_exc: Optional[Exception] = None
    result: Optional[Dict] = None
    while attempt <= SERPAPI_MAX_RETRIES:
        try:
            return _rate_limited_call(client, params)
        except Exception as exc:
            last_exc = exc
            # Se for claramente rate limit, aplicar backoff exponencial
            if _is_rate_limited_error(exc, result):
                backoff = (SERPAPI_BACKOFF_BASE ** attempt) + random.uniform(0, SERPAPI_JITTER_SEC)
                logger.warning(f"429/Rate limit. Backoff {backoff:.1f}s (tentativa {attempt+1}/{SERPAPI_MAX_RETRIES})")
                time.sleep(backoff)
                attempt += 1
                continue
            # Outros erros: relançar
            raise
    # Se esgotou tentativas, relança última exceção
    if last_exc:
        raise last_exc
    return result or {}


def _parse_results(query: str, raw: Dict, cidade_hint: Optional[str]) -> List[Dict]:
    leads: List[Dict] = []

    # Resultados orgânicos
    for result in raw.get("organic_results", []) or []:
        title = result.get("title", "")
        link = normalize_url(result.get("link", ""))
        snippet = result.get("snippet", "")
        position = result.get("position")
        phone, email = extract_contacts(" ".join([title, snippet]))
        lead_item = {
            "source_type": "organic",
            "query": query,
            "title": title,
            "link": link,
            "snippet": snippet,
            "position": position,
            "phone": phone,
            "email": email,
            "city": cidade_hint,
            "source_domain": get_source_domain(link),
            "instagram": None,
            "facebook": None,
            "linkedin": None,
            "youtube": None,
            "tiktok": None,
            "whatsapp": None,
        }
        # se o próprio link já for um perfil social, classifica
        platform = classify_social_platform(link)
        if platform:
            lead_item[platform] = link
        leads.append(lead_item)

    # Knowledge Graph (se existir)
    kg = raw.get("knowledge_graph") or {}
    if kg:
        kg_title = kg.get("title") or kg.get("name") or ""
        website = normalize_url(kg.get("website", ""))
        phone = kg.get("phone")
        email = None  # raramente disponível
        snippet = kg.get("description", "")
        lead_item = {
            "source_type": "knowledge_graph",
            "query": query,
            "title": kg_title,
            "link": website,
            "snippet": snippet,
            "position": None,
            "phone": phone,
            "email": email,
            "city": cidade_hint,
            "source_domain": get_source_domain(website),
            "instagram": None,
            "facebook": None,
            "linkedin": None,
            "youtube": None,
            "tiktok": None,
            "whatsapp": None,
        }
        platform = classify_social_platform(website)
        if platform:
            lead_item[platform] = website
        leads.append(lead_item)

    # Local pack / resultados locais
    local_results = raw.get("local_results") or {}
    for place in local_results.get("places", []) or []:
        title = place.get("title", "")
        website = normalize_url(place.get("website", ""))
        phone = place.get("phone")
        snippet = place.get("address") or place.get("snippet") or ""
        lead_item = {
            "source_type": "local",
            "query": query,
            "title": title,
            "link": website,
            "snippet": snippet,
            "position": None,
            "phone": phone,
            "email": None,
            "city": cidade_hint,
            "source_domain": get_source_domain(website),
            "instagram": None,
            "facebook": None,
            "linkedin": None,
            "youtube": None,
            "tiktok": None,
            "whatsapp": None,
        }
        platform = classify_social_platform(website)
        if platform:
            lead_item[platform] = website
        leads.append(lead_item)

    return leads


def search_and_collect_leads(queries_with_location: List[Tuple[str, Optional[str]]], api_key: str) -> List[Dict]:
    """Executa buscas em paralelo, com paginação opcional, e retorna lista de leads deduplicados."""
    client = serpapi.Client(api_key=api_key)

    # Execução paralela por (query, location)
    results: List[Dict] = []

    def run_one(query: str, location: Optional[str]) -> List[Dict]:
        cidade_hint = None
        # Tente inferir cidade do location para registrar na saída
        for cidade, loc in city_to_location.items():
            if location and loc == location:
                cidade_hint = cidade
                break

        page_leads: List[Dict] = []
        def is_social_query(q: str) -> bool:
            ql = q.lower()
            return any(f"site:{d}" in ql for d in SOCIAL_PLATFORMS.keys())

        social_q = is_social_query(query)

        for page_idx in range(MAX_PAGES):
            start = page_idx * RESULTS_PER_PAGE
            try:
                # Para consultas a redes sociais, não forçar location/tbs
                raw = _fetch_serp_page(
                    client,
                    query,
                    location=None if social_q else location,
                    start=start,
                    engine="google",
                    apply_tbs=not social_q,
                )
            except Exception as exc:
                logger.warning(f"Erro de rede/cliente em '{query}' (start={start}): {exc}")
                # Peq. backoff para eventuais limites temporários
                time.sleep(1.0)
                continue

            if isinstance(raw, dict) and raw.get("error"):
                err = raw.get('error')
                # Mensagem comum: "Google hasn't returned any results for this query."
                level = logger.info if isinstance(err, str) and "hasn't returned any results" in err else logger.warning
                level(f"Erro ao buscar '{query}' (start={start}): {err}")
                # backoff curto para 429/limites
                time.sleep(1.0)
                # Tenta fallback para Bing quando Google não retorna resultados
                try:
                    raw = _fetch_serp_page(
                        client,
                        query,
                        location=None,
                        start=start,
                        engine="bing",
                        apply_tbs=False,
                    )
                except Exception as exc2:
                    logger.info(f"Fallback Bing falhou para '{query}' (start={start}): {exc2}")
                    continue

            parsed = _parse_results(query, raw, cidade_hint)
            if not parsed:
                # Tenta uma única vez engine Bing se ainda não tentado
                try:
                    raw_bing = _fetch_serp_page(
                        client,
                        query,
                        location=None,
                        start=start,
                        engine="bing",
                        apply_tbs=False,
                    )
                    parsed = _parse_results(query, raw_bing, cidade_hint)
                except Exception:
                    parsed = []
                if not parsed:
                    # Nada encontrado; interrompe paginação para esta query
                    break
            page_leads.extend(parsed)
        return page_leads

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_q = {
            executor.submit(run_one, q, loc): (q, loc) for q, loc in queries_with_location
        }
        for future in as_completed(future_to_q):
            q, loc = future_to_q[future]
            try:
                chunk = future.result()
                results.extend(chunk)
            except Exception as exc:
                logger.error(f"Falha ao processar '{q}': {exc}")

    # Deduplicação: prioriza entradas com telefone/email/website
    def lead_key(lead: Dict) -> Tuple:
        return (
            (lead.get("title") or "").strip().lower(),
            (lead.get("link") or "").strip().lower(),
            lead.get("source_type"),
        )

    deduped: Dict[Tuple, Dict] = {}
    for lead in results:
        key = lead_key(lead)
        current = deduped.get(key)
        if current is None:
            deduped[key] = lead
            continue
        # Se já existe, mantenha aquele com mais sinais de contato
        current_score = int(bool(current.get("phone"))) + int(bool(current.get("email"))) + int(bool(current.get("link")))
        new_score = int(bool(lead.get("phone"))) + int(bool(lead.get("email"))) + int(bool(lead.get("link")))
        if new_score > current_score:
            deduped[key] = lead

    return list(deduped.values())


def _stream_download(url: str, timeout: float, max_bytes: int) -> Optional[bytes]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        with requests.get(url, headers=headers, timeout=timeout, stream=True) as resp:
            if resp.status_code >= 400:
                return None
            content_type = (resp.headers.get("Content-Type") or "").lower()
            if "text/html" not in content_type:
                return None
            total = 0
            chunks: List[bytes] = []
            for chunk in resp.iter_content(chunk_size=8192):
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total >= max_bytes:
                    break
            return b"".join(chunks)
    except Exception:
        return None


def _extract_from_html(html_bytes: bytes) -> Tuple[Optional[str], Optional[str]]:
    try:
        soup = BeautifulSoup(html_bytes, "html.parser")
    except Exception:
        return None, None

    # Prefer links explícitos
    email = None
    phone = None
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if href.startswith("mailto:") and not email:
            email = href.split(":", 1)[1].strip()
        if href.startswith("tel:") and not phone:
            phone = href.split(":", 1)[1].strip()
        if email and phone:
            break

    # Se faltar algo, varre texto
    if not (email and phone):
        text = soup.get_text(" ", strip=True)
        ph, em = extract_contacts(text)
        phone = phone or ph
        email = email or em
    # Pega links sociais
    socials: Dict[str, str] = {}
    for a in soup.select("a[href]"):
        href = a.get("href", "").strip()
        platform = classify_social_platform(href)
        if platform and platform not in socials:
            socials[platform] = href
    return phone, email, socials


def enrich_leads_in_place(leads: List[Dict]) -> None:
    """Tenta enriquecer telefone/e-mail visitando as páginas dos leads que ainda não têm contato."""
    candidates = []
    for idx, ld in enumerate(leads):
        link: str = ld.get("link") or ""
        domain = (ld.get("source_domain") or "").lower()
        if not link:
            continue
        # Evita domínios notoriamente bloqueados ou inúteis para scraping rápido
        if any(dom in domain for dom in SKIP_ENRICH_DOMAINS):
            continue
        if not ld.get("phone") or not ld.get("email"):
            candidates.append((idx, link))

    if not candidates:
        return

    def work(item):
        i, url = item
        html = _stream_download(url, timeout=ENRICH_TIMEOUT_SEC, max_bytes=ENRICH_MAX_BYTES)
        if not html:
            return i, None, None, {}
        phone, email, socials = _extract_from_html(html)
        return i, phone, email, socials

    with ThreadPoolExecutor(max_workers=ENRICH_MAX_WORKERS) as ex:
        futures = [ex.submit(work, c) for c in candidates]
        for fut in as_completed(futures):
            i, phone, email, socials = fut.result()
            if phone and not leads[i].get("phone"):
                leads[i]["phone"] = phone
            if email and not leads[i].get("email"):
                leads[i]["email"] = email
            # social links
            for key, val in socials.items():
                if not leads[i].get(key):
                    leads[i][key] = val
            leads[i]["confidence"] = confidence_score(leads[i])


# ==========================
# Sociais
# ==========================

SOCIAL_PLATFORMS = {
    "instagram.com": "instagram",
    "facebook.com": "facebook",
    "linkedin.com": "linkedin",
    "youtube.com": "youtube",
    "tiktok.com": "tiktok",
    "wa.me": "whatsapp",
    "whatsapp.com": "whatsapp",
}


def classify_social_platform(url: str) -> Optional[str]:
    if not url:
        return None
    try:
        netloc = urllib.parse.urlsplit(url).netloc.lower()
    except Exception:
        return None
    for domain_part, key in SOCIAL_PLATFORMS.items():
        if domain_part in netloc:
            return key
    return None


def filter_by_domains(leads: List[Dict]) -> List[Dict]:
    if not INCLUDE_DOMAINS and not EXCLUDE_DOMAINS:
        return leads
    filtered = []
    for ld in leads:
        domain = (ld.get("source_domain") or "").lower()
        if INCLUDE_DOMAINS and not any(domain.endswith(d) or domain == d for d in INCLUDE_DOMAINS):
            continue
        if EXCLUDE_DOMAINS and any(domain.endswith(d) or domain == d for d in EXCLUDE_DOMAINS):
            continue
        filtered.append(ld)
    return filtered


def top_k_per_query(leads: List[Dict], k: int) -> List[Dict]:
    if k <= 0:
        return leads
    by_query: Dict[str, List[Dict]] = {}
    for ld in leads:
        q = ld.get("query", "")
        by_query.setdefault(q, []).append(ld)
    trimmed: List[Dict] = []
    for q, items in by_query.items():
        for item in items:
            if "confidence" not in item:
                item["confidence"] = confidence_score(item)
        items.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        trimmed.extend(items[:k])
    return trimmed


def write_csv(output_file: str, leads: List[Dict]) -> None:
    headers = [
        "Query",
        "Tipo",
        "Título",
        "Link",
        "Domínio",
        "Instagram",
        "Facebook",
        "LinkedIn",
        "YouTube",
        "TikTok",
        "WhatsApp",
        "Telefone",
        "E-mail",
        "Cidade",
        "Posição",
        "Descrição",
        "Confiança",
    ]
    with open(output_file, "w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(headers)
        for ld in leads:
            # Garante confiança calculada
            if "confidence" not in ld:
                ld["confidence"] = confidence_score(ld)
            writer.writerow([
                ld.get("query", ""),
                ld.get("source_type", ""),
                ld.get("title", ""),
                ld.get("link", ""),
                ld.get("source_domain") or "",
                ld.get("instagram") or "",
                ld.get("facebook") or "",
                ld.get("linkedin") or "",
                ld.get("youtube") or "",
                ld.get("tiktok") or "",
                ld.get("whatsapp") or "",
                ld.get("phone") or "",
                ld.get("email") or "",
                ld.get("city") or "",
                ld.get("position") if ld.get("position") is not None else "",
                ld.get("snippet", ""),
                ld.get("confidence", 0),
            ])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Coletor e enriquecedor de leads via SerpAPI")
    parser.add_argument("--output", default=os.getenv("OUTPUT_FILE", "melhores_leads_qualificados.csv"))
    parser.add_argument("--include-social", action="store_true", default=INCLUDE_SOCIAL)
    parser.add_argument("--no-include-social", dest="include_social", action="store_false")
    parser.add_argument("--max-workers", type=int, default=MAX_WORKERS)
    parser.add_argument("--results-per-page", type=int, default=RESULTS_PER_PAGE)
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES)
    parser.add_argument("--tbs", default=SEARCH_TBS)
    parser.add_argument("--enrich", action="store_true", default=ENRICH_PAGES)
    parser.add_argument("--no-enrich", dest="enrich", action="store_false")
    parser.add_argument("--enrich-workers", type=int, default=ENRICH_MAX_WORKERS)
    parser.add_argument("--include-domains", default=",".join(sorted(INCLUDE_DOMAINS)))
    parser.add_argument("--exclude-domains", default=",".join(sorted(EXCLUDE_DOMAINS)))
    parser.add_argument("--save-json", action="store_true", default=SAVE_JSON)
    parser.add_argument("--json-path", default=JSON_PATH)
    parser.add_argument("--top-per-query", type=int, default=TOP_PER_QUERY)
    return parser.parse_args()


def main() -> None:
    global INCLUDE_SOCIAL, MAX_WORKERS, RESULTS_PER_PAGE, MAX_PAGES
    global SEARCH_TBS, ENRICH_PAGES, ENRICH_MAX_WORKERS
    global INCLUDE_DOMAINS, EXCLUDE_DOMAINS

    args = parse_args()
    output_file = args.output
    INCLUDE_SOCIAL = args.include_social
    MAX_WORKERS = args.max_workers
    RESULTS_PER_PAGE = args.results_per_page
    MAX_PAGES = args.max_pages
    SEARCH_TBS = args.tbs
    ENRICH_PAGES = args.enrich
    ENRICH_MAX_WORKERS = args.enrich_workers
    INCLUDE_DOMAINS = {d.strip().lower() for d in args.include_domains.split(",") if d.strip()}
    EXCLUDE_DOMAINS = {d.strip().lower() for d in args.exclude_domains.split(",") if d.strip()}

    # Gera pares (query, location)
    queries_to_run = build_queries(include_social=INCLUDE_SOCIAL)

    logger.info(
        f"Executando {len(queries_to_run)} consultas (workers={MAX_WORKERS}, páginas={MAX_PAGES}, num={RESULTS_PER_PAGE})..."
    )
    all_leads = search_and_collect_leads(queries_to_run, SERPAPI_API_KEY)
    logger.info(f"Coletados {len(all_leads)} leads após deduplicação.")

    # Filtro por domínios se definido
    before = len(all_leads)
    all_leads = filter_by_domains(all_leads)
    if len(all_leads) != before:
        logger.info(f"Filtrados por domínio: {before} -> {len(all_leads)}")

    # Enriquecimento opcional (scrape leve das páginas)
    if ENRICH_PAGES:
        logger.info("Enriquecendo contatos a partir das páginas (limitado)...")
        enrich_leads_in_place(all_leads)

    # top-k por consulta, se solicitado
    if args.top_per_query and args.top_per_query > 0:
        all_leads = top_k_per_query(all_leads, args.top_per_query)
        logger.info(f"Top-k por consulta aplicado (k={args.top_per_query}). Total agora: {len(all_leads)}")

    # Salvar CSV
    write_csv(output_file, all_leads)
    logger.info(f"CSV salvo em '{output_file}'.")

    # Opcionalmente salvar JSON
    if args.save_json:
        with open(args.json_path, "w", encoding="utf-8") as jf:
            json.dump(all_leads, jf, ensure_ascii=False, indent=2)
        logger.info(f"JSON salvo em '{args.json_path}'.")


if __name__ == "__main__":
    main()