# -*- coding: utf-8 -*-
"""Testes do servidor MCP da BNCC."""
import pytest

from bncc_mcp import server as s


# --- casamento de ano (ano único '06' vs faixa '69'/'15'/'35') --------------

@pytest.mark.parametrize("faixa,ano,esperado", [
    ("06", "6", True),    # ano único
    ("07", "6", False),   # NÃO casa (bug histórico: tratava como faixa 0-7)
    ("69", "6", True),    # faixa 6º-9º
    ("69", "8", True),
    ("69", "5", False),
    ("15", "3", True),    # faixa 1º-5º
    ("35", "6", False),
    ("01", "6", False),
    ("12", "1", True),    # faixa 1º-2º
    ("89", "7", False),
    ("06", "6º", True),   # entrada com ordinal
    ("06", "", True),     # sem filtro
])
def test_ano_match(faixa, ano, esperado):
    assert s._ano_match({"ano_ou_faixa": faixa}, ano) is esperado


# --- carga de dados ---------------------------------------------------------

def test_total_registros():
    st = s.bncc_estatisticas()
    assert st["total_habilidades"] == 1576
    assert st["por_etapa"]["Ensino Fundamental"] == 1304
    assert st["em_foco_total"] == 396


# --- lookup -----------------------------------------------------------------

def test_lookup_ok():
    r = s.bncc_lookup("EF06MA01")
    assert r["componente"] == "Matemática"
    assert r["unidade_tematica"] == "Números"
    assert r["em_foco"] is True
    assert r["mapa_foco"]["classificacao"] == "AF"


def test_lookup_case_insensitive():
    assert s.bncc_lookup("ef06ma01")["codigo"] == "EF06MA01"


def test_lookup_inexistente():
    r = s.bncc_lookup("XX99ZZ99")
    assert "erro" in r


def test_ei_sem_unidade():
    r = s.bncc_lookup("EI01CG01")
    assert r["etapa"] == "Educação Infantil"
    assert r["unidade_tematica"] == ""
    assert r["em_foco"] is False


def test_em_lookup():
    r = s.bncc_lookup("EM13LGG101")
    assert r["etapa"] == "Ensino Médio"
    assert r["area"].startswith("Linguagens")


# --- busca ------------------------------------------------------------------

def test_busca_acento_insensivel():
    r = s.bncc_buscar(texto="fracao", componente="Matemática", limite=50)
    assert r["total"] > 0  # 'fracao' casa 'fração'


def test_busca_apenas_em_foco():
    r = s.bncc_buscar(componente="Matemática", apenas_em_foco=True, limite=500)
    assert r["total"] == 123
    assert all(x["em_foco"] for x in r["resultados"])


def test_busca_limite():
    r = s.bncc_buscar(etapa="Ensino Fundamental", limite=5)
    assert r["exibindo"] == 5
    assert r["total"] > 5


# --- listar -----------------------------------------------------------------

def test_listar_ciencias_6():
    r = s.bncc_listar(componente="Ciências", ano="6")
    assert r["total"] == 14  # 6º ano exato, sem vazar 7º/8º/9º


# --- mapa de foco -----------------------------------------------------------

def test_mapa_de_foco_so_em_foco():
    r = s.bncc_mapa_de_foco(componente="História")
    assert r["total"] == 37
    assert all(x["mapa_foco"] for x in r["resultados"])


def test_mapa_de_foco_campos():
    r = s.bncc_mapa_de_foco(componente="História", ano="6", limite=1)
    mf = r["resultados"][0]["mapa_foco"]
    for campo in ("classificacao", "conhecimento_previo", "objetivos_aprendizagem",
                  "competencias_relacionadas", "habilidades_relacionadas", "comentarios"):
        assert campo in mf
