"""Retrieval layer for jurisprudence with provider toggle.
Simple skeleton with three providers: simple, graph, hybrid.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Protocol
from django.conf import settings
from math import sqrt
import uuid


@dataclass
class JurisItem:
    id: str
    titulo: str
    tribunal: Optional[str] = None
    data: Optional[str] = None
    temas: Optional[List[str]] = None
    teses: Optional[List[str]] = None
    riscos: Optional[List[str]] = None
    citacoes: Optional[List[str]] = None
    link: Optional[str] = None
    vinculante: Optional[bool] = None
    dispositivos_citados: Optional[List[str]] = None
    score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RetrievalService(Protocol):
    def search(self, q: Optional[str], filters: Dict[str, Any], topk: int = 8) -> List[JurisItem]:
        ...

    def sugestoes(self, filters: Dict[str, Any], topk: int = 8) -> List[JurisItem]:
        ...


class SimpleRAGRetrieval:
    """Baseline retrieval usando ORM (sem vetores).
    - Filtros por tema/tribunal
    - Ranqueamento simples por match textual e recência
    """

    def _to_item(self, j) -> JurisItem:
        data_iso = j.data_julgamento.isoformat() if getattr(j, 'data_julgamento', None) else None
        return JurisItem(
            id=str(j.id),
            titulo=j.titulo,
            tribunal=j.tribunal,
            data=data_iso,
            temas=[j.tema] if getattr(j, 'tema', None) else None,
            teses=None,
            riscos=None,
            citacoes=None,
            link=j.link,
            vinculante=getattr(j, 'vinculante', None),
            dispositivos_citados=getattr(j, 'dispositivos_citados', None),
            score=None,
        )

    def _apply_filters(self, qs, filters: Dict[str, Any]):
        tema = (filters.get('tema') or '').strip() if filters else ''
        tribunal = (filters.get('tribunal') or '').strip() if filters else ''
        vinculante = (filters.get('vinculante') or '').strip().lower() if filters else ''
        fase = (filters.get('fase') or '').strip() if filters else ''
        bloco = (filters.get('bloco') or '').strip() if filters else ''
        if tema:
            qs = qs.filter(tema__icontains=tema)
        if tribunal:
            qs = qs.filter(tribunal__icontains=tribunal)
        if vinculante in ['true', '1', 'yes', 'sim']:
            qs = qs.filter(vinculante=True)
        elif vinculante in ['false', '0', 'no', 'nao', 'não']:
            qs = qs.filter(vinculante=False)
        if fase:
            qs = qs.filter(fase__icontains=fase)
        if bloco and bloco.isdigit():
            qs = qs.filter(bloco=int(bloco))
        dispositivo = (filters.get('dispositivo') or '').strip() if filters else ''
        tese = (filters.get('tese') or '').strip() if filters else ''
        if dispositivo:
            qs = qs.filter(dispositivos_citados__icontains=dispositivo)
        if tese:
            qs = qs.filter(teses_defensivas__icontains=tese)
        return qs

    def _score(self, j, q_norm: str) -> float:
        # Pontuação simples baseada em ocorrência no título/ementa/fundamentação e leve bônus por recência
        if not q_norm:
            q_terms = []
        else:
            q_terms = [t for t in q_norm.split() if t]
        title = (j.titulo or '').lower()
        ementa = (j.ementa or '').lower()
        fund = (j.fundamentacao or '').lower()
        def term_count(text: str) -> int:
            total = 0
            for t in q_terms:
                total += text.count(t)
            return total
        score = 0.0
        score += 3.0 * term_count(title)
        score += 1.5 * term_count(ementa)
        score += 1.0 * term_count(fund)
        # bônus de recência: mais recente ganha +0.01 por ano relativo a 2000 (limitado)
        try:
            if j.data_julgamento:
                year = j.data_julgamento.year
                score += max(0.0, min(0.5, 0.01 * (year - 2000)))
        except Exception:
            pass
        return score

    def search(self, q: Optional[str], filters: Dict[str, Any], topk: int = 8) -> List[JurisItem]:
        try:
            from juris.models import Jurisprudencia
        except Exception:
            return []
        qs = Jurisprudencia.objects.all()
        qs = self._apply_filters(qs, filters)
        q_norm = (q or '').strip().lower()
        candidates = list(qs.select_related('embedding')[:300])  # mais candidatos para embeddings
        # Se não houver consulta, ordenar por data desc/id desc
        if not q_norm:
            candidates.sort(key=lambda j: (
                j.data_julgamento or None, j.id
            ), reverse=True)
            return [self._to_item(j) for j in candidates[:topk]]

        # Se tivermos embeddings, usar cosine; senão, fallback no score textual
        def cosine(a: List[float], b: List[float]) -> float:
            if not a or not b or len(a) != len(b):
                return 0.0
            dot = sum(x*y for x, y in zip(a, b))
            na = sqrt(sum(x*x for x in a))
            nb = sqrt(sum(y*y for y in b))
            if na == 0 or nb == 0:
                return 0.0
            return dot / (na * nb)

        # Embed da consulta via OpenAI se chave disponível; caso contrário, fallback textual
        try:
            from ai_engine.processor import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            model = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
            resp = client.embeddings.create(model=model, input=[q_norm])
            q_vec = resp.data[0].embedding
        except Exception:
            q_vec = None

        scored = []
        for j in candidates:
            if q_vec and hasattr(j, 'embedding') and j.embedding and j.embedding.embedding:
                sim = cosine(q_vec, j.embedding.embedding)
                # bônus por recência
                if getattr(j, 'data_julgamento', None):
                    sim += min(0.05, max(0.0, 0.001 * (j.data_julgamento.year - 2000)))
                # bônus leve por vinculância
                try:
                    if getattr(j, 'vinculante', False):
                        sim += 0.02
                except Exception:
                    pass
                scored.append((sim, j))
            else:
                scored.append((self._score(j, q_norm), j))

        scored.sort(key=lambda x: x[0], reverse=True)
        items: List[JurisItem] = []
        for s, j in scored[:topk]:
            item = self._to_item(j)
            item.score = float(s)
            items.append(item)
        return items

    def sugestoes(self, filters: Dict[str, Any], topk: int = 8) -> List[JurisItem]:
        try:
            from juris.models import Jurisprudencia
        except Exception:
            return []
        qs = Jurisprudencia.objects.all()
        qs = self._apply_filters(qs, filters)
        qs = qs.order_by('-data_julgamento', '-id')
        return [self._to_item(j) for j in qs[:topk]]


class GraphRAGRetrieval:
    """Neo4j-backed retrieval com fallback silencioso se driver indisponível."""

    def __init__(self):
        self.url = getattr(settings, 'JURIS_GRAPH_URL', 'bolt://localhost:7687')
        self.user = getattr(settings, 'JURIS_GRAPH_USER', 'neo4j')
        self.password = getattr(settings, 'JURIS_GRAPH_PASSWORD', '')
        self.timeout_ms = getattr(settings, 'JURIS_GRAPH_TIMEOUT_MS', 2000)
        try:
            from neo4j import GraphDatabase  # type: ignore
            self._driver = GraphDatabase.driver(self.url, auth=(self.user, self.password))
        except Exception:
            self._driver = None

    def _run(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self._driver:
            return []
        try:
            with self._driver.session() as session:
                res = session.run(cypher, **params)
                return [r.data() for r in res]
        except Exception:
            return []

    def search(self, q: Optional[str], filters: Dict[str, Any], topk: int = 8) -> List[JurisItem]:
        tema = (filters.get('tema') or '').strip() if filters else ''
        tribunal = (filters.get('tribunal') or '').strip() if filters else ''
        fase = (filters.get('fase') or '').strip() if filters else ''
        bloco = (filters.get('bloco') or '').strip() if filters else ''
        vinculante = (filters.get('vinculante') or '').strip().lower() if filters else ''
        dispositivo = (filters.get('dispositivo') or '').strip() if filters else ''
        tese = (filters.get('tese') or '').strip() if filters else ''
        cypher = """
        MATCH (j:Juris)
        OPTIONAL MATCH (j)-[:HAS_TEMA]->(t:Tema)
        OPTIONAL MATCH (j)-[:APPLIES_TO]->(f:Fase)
        OPTIONAL MATCH (j)-[:APPLIES_TO]->(b:Bloco)
        OPTIONAL MATCH (j)-[:CITES]->(d:Dispositivo)
        OPTIONAL MATCH (j)-[:SUPPORTS]->(s:Tese)
        WHERE ($tema = '' OR toLower(t.nome) CONTAINS toLower($tema))
          AND ($tribunal = '' OR toLower(j.tribunal) CONTAINS toLower($tribunal))
          AND ($fase = '' OR toLower(f.titulo) CONTAINS toLower($fase) OR toLower(f.nome) CONTAINS toLower($fase))
          AND ($bloco = '' OR toString(b.bloco) = $bloco OR toLower(b.titulo) CONTAINS toLower($bloco))
          AND (
            $vinculante = '' OR ($vinculante IN ['true','1','yes','sim'] AND j.vinculante = true) OR ($vinculante IN ['false','0','no','nao','não'] AND (j.vinculante = false OR j.vinculante IS NULL))
          )
          AND ($dispositivo = '' OR toLower(d.titulo) CONTAINS toLower($dispositivo) OR toLower(d.nome) CONTAINS toLower($dispositivo))
          AND ($tese = '' OR toLower(s.titulo) CONTAINS toLower($tese) OR toLower(s.nome) CONTAINS toLower($tese))
        RETURN j AS j, t AS t, f AS f, b AS b
        ORDER BY j.vinculante DESC, j.data DESC
        LIMIT $limit
        """
        rows = self._run(cypher, {'tema': tema, 'tribunal': tribunal, 'fase': fase, 'bloco': bloco, 'vinculante': vinculante, 'dispositivo': dispositivo, 'tese': tese, 'limit': max(topk*3, 20)})
        prelim: List[JurisItem] = []
        for r in rows:
            j = r.get('j') or {}
            item = JurisItem(
                id=str(j.get('id', '')),
                titulo=j.get('titulo', ''),
                tribunal=j.get('tribunal'),
                data=j.get('data'),
                temas=[r.get('t', {}).get('nome')] if r.get('t') else None,
                link=j.get('link'),
                vinculante=j.get('vinculante'),
                dispositivos_citados=None,
                score=None,
            )
            prelim.append(item)
        # Rerank semântico best-effort usando embeddings locais se possível
        if not q:
            return prelim[:topk]
        q_norm = (q or '').strip().lower()
        try:
            from ai_engine.processor import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            model = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
            resp = client.embeddings.create(model=model, input=[q_norm])
            q_vec = resp.data[0].embedding
        except Exception:
            q_vec = None
        def cosine(a: List[float], b: List[float]) -> float:
            if not a or not b or len(a) != len(b):
                return 0.0
            dot = sum(x*y for x, y in zip(a, b))
            na = sqrt(sum(x*x for x in a))
            nb = sqrt(sum(y*y for y in b))
            if na == 0 or nb == 0:
                return 0.0
            return dot / (na * nb)
        scored: List[tuple[float, JurisItem]] = []
        # Tentar mapear por titulo/tribunal no ORM para usar embedding
        try:
            from juris.models import Jurisprudencia
            orm_map = {}
            titles = [it.titulo for it in prelim if it.titulo]
            if titles:
                for j in Jurisprudencia.objects.filter(titulo__in=titles).select_related('embedding'):
                    orm_map[(j.titulo or '') + '|' + (j.tribunal or '')] = j
            for it in prelim:
                key = (it.titulo or '') + '|' + (it.tribunal or '')
                j = orm_map.get(key)
                if q_vec and j is not None and hasattr(j, 'embedding') and j.embedding and j.embedding.embedding:
                    sim = cosine(q_vec, j.embedding.embedding)
                    scored.append((sim, it))
                else:
                    # fallback textual peso no título
                    sim = 0.0
                    for t in q_norm.split():
                        sim += (it.titulo or '').lower().count(t) * 2.0
                    scored.append((sim, it))
        except Exception:
            # fallback: sem ORM
            for it in prelim:
                sim = 0.0
                for t in q_norm.split():
                    sim += (it.titulo or '').lower().count(t) * 2.0
                scored.append((sim, it))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [it for _, it in scored[:topk]]

    def sugestoes(self, filters: Dict[str, Any], topk: int = 8) -> List[JurisItem]:
        return self.search(None, filters, topk)


class HybridRetrieval:
    def __init__(self, simple: SimpleRAGRetrieval, graph: GraphRAGRetrieval):
        self.simple = simple
        self.graph = graph

    def _fallback_needed(self, results: List[JurisItem]) -> bool:
        if not results:
            return True
        # Optionally, check average score threshold when implemented
        return False

    def search(self, q: Optional[str], filters: Dict[str, Any], topk: int = 8) -> List[JurisItem]:
        r = self.graph.search(q, filters, topk)
        return r if not self._fallback_needed(r) else self.simple.search(q, filters, topk)

    def sugestoes(self, filters: Dict[str, Any], topk: int = 8) -> List[JurisItem]:
        r = self.graph.sugestoes(filters, topk)
        return r if not self._fallback_needed(r) else self.simple.sugestoes(filters, topk)


def get_provider(provider_override: Optional[str] = None) -> str:
    if provider_override:
        return provider_override
    return getattr(settings, 'JURIS_RETRIEVAL_PROVIDER', 'simple')


def get_service(provider: Optional[str] = None) -> RetrievalService:
    provider = get_provider(provider)
    simple = SimpleRAGRetrieval()
    graph_enabled = getattr(settings, 'JURIS_GRAPH_ENABLED', False)

    if provider == 'graph' and graph_enabled:
        return GraphRAGRetrieval()
    if provider == 'hybrid' and graph_enabled:
        return HybridRetrieval(simple, GraphRAGRetrieval())
    # default simple or graph disabled
    return simple


def make_response(items: List[JurisItem], provider_used: str) -> Dict[str, Any]:
    return {
        'items': [i.to_dict() for i in items],
        'provider_used': provider_used,
        'trace_id': str(uuid.uuid4()),
    }

