# -*- coding: utf-8 -*-
"""Servidor MCP da BNCC.

Expõe as habilidades da Base Nacional Comum Curricular (Educação Infantil,
Ensino Fundamental e Ensino Médio) com unidade temática, objeto de
conhecimento e a camada de priorização do Mapa de Foco (Instituto Reúna).

Dados públicos da BNCC — livre para compartilhar.
"""
from __future__ import annotations

import csv
import os
import re
from typing import Any

from mcp.server.fastmcp import FastMCP

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
HAB_CSV = os.path.join(DATA_DIR, "bncc_habilidades.csv")
EM_CSV = os.path.join(DATA_DIR, "bncc_em.csv")

mcp = FastMCP("bncc")

# ----------------------------------------------------------------------------
# Carga dos dados (em memória; ~1500 registros)
# ----------------------------------------------------------------------------

def _norm(s: str) -> str:
    """Normaliza texto para busca: minúsculas e sem acentos."""
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def _load() -> dict[str, dict[str, Any]]:
    registros: dict[str, dict[str, Any]] = {}

    # Educação Infantil + Ensino Fundamental (CSV enriquecido)
    with open(HAB_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            cod = (r.get("código") or r.get("codigo") or "").strip()
            if not cod:
                continue
            rec = {
                "codigo": cod,
                "etapa": r.get("etapa", "").strip(),
                "componente": r.get("componente", "").strip(),
                "ano_ou_faixa": r.get("ano_ou_faixa", "").strip(),
                "campo_experiencia": (r.get("campo_experiência")
                                      or r.get("campo_experiencia") or "").strip(),
                "unidade_tematica": r.get("unidade_tematica", "").strip(),
                "objeto_conhecimento": r.get("objeto_conhecimento", "").strip(),
                "habilidade": r.get("habilidade", "").strip(),
                "em_foco": (r.get("em_foco", "").strip().lower() == "sim"),
            }
            if rec["em_foco"]:
                rec["mapa_foco"] = {
                    "classificacao": r.get("mf_classificacao", "").strip(),
                    "conhecimento_previo": r.get("mf_conhecimento_previo", "").strip(),
                    "objetivos_aprendizagem": r.get("mf_objetivos", "").strip(),
                    "competencias_relacionadas": r.get("mf_competencias", "").strip(),
                    "habilidades_relacionadas": r.get("mf_habilidades_relacionadas", "").strip(),
                    "comentarios": r.get("mf_comentarios", "").strip(),
                }
            registros[cod] = rec

    # Ensino Médio
    with open(EM_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cod = (r.get("codigo") or "").strip()
            if not cod or cod in registros:
                continue
            registros[cod] = {
                "codigo": cod,
                "etapa": "Ensino Médio",
                "componente": "",
                "area": r.get("area", "").strip(),
                "ano_ou_faixa": "",
                "unidade_tematica": "",
                "objeto_conhecimento": "",
                "habilidade": r.get("habilidade", "").strip(),
                "em_foco": False,
            }
    return registros


REGISTROS = _load()
# índice de busca pré-computado (codigo -> texto normalizado)
_INDICE = {c: _norm(" ".join(str(v) for v in r.values() if isinstance(v, str)))
           for c, r in REGISTROS.items()}


def _ano_match(rec: dict, ano: str) -> bool:
    """Casa filtro de ano com o campo ano_ou_faixa. Convenção da BNCC:
    ano único vem com zero à esquerda ('06' = 6º ano); faixa vem sem zero e
    com 1º dígito < 2º ('69' = 6º-9º, '15' = 1º-5º, '12' = 1º-2º). Aceita
    entrada '6', '06' ou '6º'."""
    if not ano:
        return True
    alvo = re.sub(r"\D", "", str(ano))
    digitos = re.sub(r"\D", "", rec.get("ano_ou_faixa", ""))
    if not alvo or not digitos:
        return not alvo
    alvo = int(alvo)
    if len(digitos) == 2 and digitos[0] != "0" and int(digitos[0]) < int(digitos[1]):
        return int(digitos[0]) <= alvo <= int(digitos[1])  # faixa
    return int(digitos) == alvo  # ano único


def _filtra(recs, etapa="", componente="", ano="", apenas_foco=False):
    ne, nc = _norm(etapa), _norm(componente)
    out = []
    for r in recs:
        if apenas_foco and not r.get("em_foco"):
            continue
        if ne and ne not in _norm(r.get("etapa", "")):
            continue
        if nc and nc not in _norm(r.get("componente", "") + " " + r.get("area", "")):
            continue
        if not _ano_match(r, ano):
            continue
        out.append(r)
    return out

# ----------------------------------------------------------------------------
# Tools
# ----------------------------------------------------------------------------

@mcp.tool()
def bncc_lookup(codigo: str) -> dict:
    """Retorna o registro completo de uma habilidade da BNCC pelo código
    (ex.: 'EF06MA01', 'EF01LP01', 'EM13LGG101').

    Inclui enunciado, etapa, componente, ano, unidade temática, objeto de
    conhecimento e — quando a habilidade está no Mapa de Foco — toda a camada
    de priorização (classificação, conhecimento prévio, objetivos de
    aprendizagem, competências e habilidades relacionadas, comentários).
    """
    cod = codigo.strip().upper()
    rec = REGISTROS.get(cod)
    if not rec:
        return {"erro": f"código '{cod}' não encontrado",
                "dica": "use bncc_buscar para localizar por palavra-chave"}
    return rec


@mcp.tool()
def bncc_buscar(texto: str = "", etapa: str = "", componente: str = "",
                ano: str = "", apenas_em_foco: bool = False,
                limite: int = 30) -> dict:
    """Busca habilidades por palavra-chave no enunciado (acento-insensível),
    com filtros opcionais por etapa, componente, ano e Mapa de Foco.

    Args:
        texto: termo(s) a buscar no enunciado/objeto/unidade (vazio = só filtros).
        etapa: 'Ensino Fundamental', 'Educação Infantil', 'Ensino Médio'.
        componente: ex. 'Matemática', 'Língua Portuguesa', 'Ciências'.
        ano: ex. '6' ou '06'; casa também intervalos ('69' = 6º ao 9º).
        apenas_em_foco: se True, restringe às habilidades do Mapa de Foco.
        limite: máximo de resultados (padrão 30).
    """
    cands = _filtra(REGISTROS.values(), etapa, componente, ano, apenas_em_foco)
    nt = _norm(texto)
    if nt:
        termos = nt.split()
        cands = [r for r in cands
                 if all(t in _INDICE[r["codigo"]] for t in termos)]
    cands.sort(key=lambda r: r["codigo"])
    total = len(cands)
    res = [{"codigo": r["codigo"], "etapa": r["etapa"],
            "componente": r.get("componente") or r.get("area", ""),
            "ano": r.get("ano_ou_faixa", ""), "em_foco": r.get("em_foco", False),
            "habilidade": r["habilidade"]}
           for r in cands[:limite]]
    return {"total": total, "exibindo": len(res), "resultados": res}


@mcp.tool()
def bncc_listar(componente: str, ano: str = "", etapa: str = "",
                limite: int = 100) -> dict:
    """Lista as habilidades de um recorte (componente + ano), com a unidade
    temática e o objeto de conhecimento de cada uma.

    Args:
        componente: ex. 'Matemática' (obrigatório).
        ano: ex. '6'; vazio = todos os anos do componente.
        etapa: opcional, para desambiguar.
        limite: máximo de resultados (padrão 100).
    """
    cands = _filtra(REGISTROS.values(), etapa, componente, ano)
    cands.sort(key=lambda r: r["codigo"])
    res = [{"codigo": r["codigo"], "ano": r.get("ano_ou_faixa", ""),
            "unidade_tematica": r.get("unidade_tematica", ""),
            "objeto_conhecimento": r.get("objeto_conhecimento", ""),
            "em_foco": r.get("em_foco", False),
            "habilidade": r["habilidade"]}
           for r in cands[:limite]]
    return {"componente": componente, "ano": ano or "todos",
            "total": len(cands), "exibindo": len(res), "resultados": res}


@mcp.tool()
def bncc_mapa_de_foco(componente: str = "", ano: str = "",
                      limite: int = 100) -> dict:
    """Retorna as habilidades priorizadas no Mapa de Foco da BNCC (Instituto
    Reúna), com toda a camada pedagógica: classificação, conhecimento prévio,
    objetivos de aprendizagem, competências e habilidades relacionadas e
    comentários.

    O Mapa de Foco cobre Língua Portuguesa, Matemática, Ciências, História e
    Geografia (Ensino Fundamental). Não há Mapa de Foco para Arte, Educação
    Física, Língua Inglesa, Ensino Religioso, Educação Infantil ou Ensino Médio.

    Args:
        componente: ex. 'Matemática'; vazio = todos os componentes cobertos.
        ano: ex. '6'; vazio = todos os anos.
        limite: máximo de resultados (padrão 100).
    """
    cands = _filtra(REGISTROS.values(), "", componente, ano, apenas_foco=True)
    cands.sort(key=lambda r: r["codigo"])
    res = [{"codigo": r["codigo"], "componente": r.get("componente", ""),
            "ano": r.get("ano_ou_faixa", ""),
            "unidade_tematica": r.get("unidade_tematica", ""),
            "objeto_conhecimento": r.get("objeto_conhecimento", ""),
            "habilidade": r["habilidade"],
            "mapa_foco": r.get("mapa_foco", {})}
           for r in cands[:limite]]
    return {"componente": componente or "todos", "ano": ano or "todos",
            "total": len(cands), "exibindo": len(res), "resultados": res}


@mcp.tool()
def bncc_estatisticas() -> dict:
    """Resumo do acervo: contagem de habilidades por etapa e por componente,
    e quantas estão no Mapa de Foco."""
    import collections
    por_etapa = collections.Counter(r["etapa"] for r in REGISTROS.values())
    foco = collections.Counter(r["componente"] for r in REGISTROS.values()
                               if r.get("em_foco"))
    return {"total_habilidades": len(REGISTROS),
            "por_etapa": dict(por_etapa),
            "em_foco_total": sum(foco.values()),
            "em_foco_por_componente": dict(foco)}


def main() -> None:
    """Ponto de entrada do servidor MCP (usado pelo console script)."""
    mcp.run()


if __name__ == "__main__":
    main()
