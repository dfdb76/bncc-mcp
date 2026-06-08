# BNCC MCP

[![CI](https://github.com/dfdb76/bncc-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/dfdb76/bncc-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/bncc-mcp)](https://pypi.org/project/bncc-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/bncc-mcp)](https://pypi.org/project/bncc-mcp/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Servidor [MCP](https://modelcontextprotocol.io) que expõe as habilidades da
**Base Nacional Comum Curricular** (Educação Infantil, Ensino Fundamental e
Ensino Médio) com unidade temática, objeto de conhecimento e a camada de
priorização do **Mapa de Foco** (Instituto Reúna).

A BNCC (MEC) é de livre uso; o Mapa de Foco é © Instituto Reúna, sujeito a atribuição e com permissão de uso não comercial — ver
[`ATTRIBUTION.md`](ATTRIBUTION.md).

---

## Sumário

- [Acervo](#acervo)
- [Instalação](#instalação)
- [Configuração no Claude Code](#configuração-no-claude-code)
- [Tools](#tools)
  - [`bncc_lookup`](#bncc_lookupcodigo)
  - [`bncc_buscar`](#bncc_buscartexto-etapa-componente-ano-apenas_em_foco-limite)
  - [`bncc_listar`](#bncc_listarcomponente-ano-etapa-limite)
  - [`bncc_mapa_de_foco`](#bncc_mapa_de_fococomponente-ano-limite)
  - [`bncc_estatisticas`](#bncc_estatisticas)
- [Esquema dos registros](#esquema-dos-registros)
- [Semântica do filtro de ano](#semântica-do-filtro-de-ano)
- [Procedência dos dados](#procedência-dos-dados)
- [Limitações](#limitações)
- [Estrutura do projeto](#estrutura-do-projeto)

---

## Acervo

| Etapa | Habilidades | Enriquecimento |
|---|---|---|
| Ensino Fundamental | 1304 | 100% com unidade temática + objeto de conhecimento |
| Educação Infantil | 93 | campos de experiência |
| Ensino Médio | 179 | área |
| **Total** | **1576** | |

**Mapa de Foco** — 396 habilidades priorizadas com classificação, conhecimento
prévio, objetivos de aprendizagem, competências e habilidades relacionadas e
comentários:

| Componente | Em foco |
|---|---|
| Língua Portuguesa | 127 |
| Matemática | 123 |
| Ciências | 56 |
| Geografia | 53 |
| História | 37 |

---

## Instalação

Requer Python 3.10+.

```bash
pip install bncc-mcp          # quando publicado no PyPI
# ou, a partir do código-fonte:
pip install .
# para desenvolvimento:
pip install -e .
```

---

## Configuração no Claude Code

Após instalar o pacote:

```bash
claude mcp add bncc --scope user -- python -m bncc_mcp
```

Ou manualmente em `.mcp.json` / configuração de MCP:

```json
{
  "mcpServers": {
    "bncc": {
      "command": "python",
      "args": ["-m", "bncc_mcp"]
    }
  }
}
```

As tools aparecem como `mcp__bncc__<nome>` na sessão seguinte (servidores
adicionados durante uma sessão não carregam retroativamente).

---

## Tools

### `bncc_lookup(codigo)`

Retorna o registro completo de uma habilidade pelo código.

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `codigo` | string | sim | Código da habilidade (ex.: `EF06MA01`, `EF01LP01`, `EM13LGG101`). Case-insensitive. |

Quando a habilidade está no Mapa de Foco, o objeto `mapa_foco` é incluído.
Código inexistente devolve `{"erro": ..., "dica": ...}`.

**Exemplo** — `bncc_lookup("EF06MA01")`:

```json
{
  "codigo": "EF06MA01",
  "etapa": "Ensino Fundamental",
  "componente": "Matemática",
  "ano_ou_faixa": "06",
  "campo_experiencia": "",
  "unidade_tematica": "Números",
  "objeto_conhecimento": "Sistema de numeração decimal: características, leitura, escrita e comparação de números naturais e de números racionais representados na forma decimal",
  "habilidade": "Comparar, ordenar, ler e escrever números naturais e números racionais cuja representação decimal é finita, fazendo uso da reta numérica.",
  "em_foco": true,
  "mapa_foco": {
    "classificacao": "AF",
    "conhecimento_previo": "EF05MA01, EF05MA02, EF05MA05 e EF05MA07",
    "objetivos_aprendizagem": "• Ler e escrever números naturais e números racionais decimais\n• Comparar ...",
    "competencias_relacionadas": "CG: 1 e 4",
    "habilidades_relacionadas": "EF06MA05 EF06MA12",
    "comentarios": "..."
  }
}
```

---

### `bncc_buscar(texto, etapa, componente, ano, apenas_em_foco, limite)`

Busca habilidades por palavra-chave no enunciado/objeto/unidade
(acento-insensível), com filtros opcionais. Todos os termos do `texto` precisam
estar presentes (AND).

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `texto` | string | `""` | Termo(s) a buscar. Vazio = só aplica filtros. |
| `etapa` | string | `""` | `Ensino Fundamental`, `Educação Infantil`, `Ensino Médio` (substring). |
| `componente` | string | `""` | Ex.: `Matemática`, `Língua Portuguesa`, `Ciências` (substring, casa também `area` do EM). |
| `ano` | string | `""` | Ver [semântica do filtro de ano](#semântica-do-filtro-de-ano). |
| `apenas_em_foco` | bool | `false` | Restringe às habilidades do Mapa de Foco. |
| `limite` | int | `30` | Máximo de resultados. |

**Retorno:** `{ "total": int, "exibindo": int, "resultados": [ {codigo, etapa, componente, ano, em_foco, habilidade} ] }`

**Exemplo** — `bncc_buscar(texto="fração", componente="Matemática", apenas_em_foco=true, limite=3)`:

```json
{
  "total": 4,
  "exibindo": 3,
  "resultados": [
    {"codigo": "EF06MA07", "etapa": "Ensino Fundamental", "componente": "Matemática", "ano": "06", "em_foco": true, "habilidade": "Compreender, comparar e ordenar frações associadas às ideias de ..."}
  ]
}
```

---

### `bncc_listar(componente, ano, etapa, limite)`

Lista as habilidades de um recorte (componente + ano), com unidade temática e
objeto de conhecimento de cada uma.

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `componente` | string | — (obrigatório) | Ex.: `Matemática`. |
| `ano` | string | `""` | Vazio = todos os anos do componente. |
| `etapa` | string | `""` | Opcional, para desambiguar. |
| `limite` | int | `100` | Máximo de resultados. |

**Retorno:** `{ "componente", "ano", "total", "exibindo", "resultados": [ {codigo, ano, unidade_tematica, objeto_conhecimento, em_foco, habilidade} ] }`

---

### `bncc_mapa_de_foco(componente, ano, limite)`

Retorna as habilidades priorizadas no Mapa de Foco, com toda a camada
pedagógica.

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `componente` | string | `""` | Vazio = todos os componentes cobertos. |
| `ano` | string | `""` | Vazio = todos os anos. |
| `limite` | int | `100` | Máximo de resultados. |

**Retorno:** `{ "componente", "ano", "total", "exibindo", "resultados": [ {codigo, componente, ano, unidade_tematica, objeto_conhecimento, habilidade, mapa_foco} ] }`

**Exemplo** — `bncc_mapa_de_foco(componente="História", ano="6", limite=1)`:

```json
{
  "componente": "História",
  "ano": "6",
  "total": 23,
  "exibindo": 1,
  "resultados": [
    {
      "codigo": "EF06HI01",
      "componente": "História",
      "ano": "06",
      "unidade_tematica": "História: tempo, espaço e formas de registros",
      "objeto_conhecimento": "A questão do tempo, sincronias e diacronias: reflexões sobre o sentido das cronologias",
      "habilidade": "Identificar diferentes formas de compreensão da noção de tempo e de periodização dos processos históricos (continuidades e rupturas).",
      "mapa_foco": {
        "classificacao": "AF",
        "conhecimento_previo": "EF05HI07",
        "objetivos_aprendizagem": "• Identificar e analisar diferentes noções de tempo.\n• Construir os conceitos de sincronia e de diacronia ...",
        "competencias_relacionadas": "CG: 1 e 2\nCA: 2, 4 e 5\nCE: 2 e 6",
        "habilidades_relacionadas": "AF:\n- EF06GE11: amplia o conhecimento da AF.\n- EF06GE08: amplia o conhecimento da AF.",
        "comentarios": "Ao se trabalhar características físico-naturais da superfície terrestre ..."
      }
    }
  ]
}
```

**Campos do `mapa_foco`:**

| Campo | Conteúdo |
|---|---|
| `classificacao` | Classificação da habilidade no Mapa de Foco (ex.: `AF`). |
| `conhecimento_previo` | Códigos de habilidades pré-requisito de anos anteriores. |
| `objetivos_aprendizagem` | Objetivos de aprendizagem desdobrados (lista com `•`). |
| `competencias_relacionadas` | Competências gerais (CG), de área (CA) e específicas (CE). |
| `habilidades_relacionadas` | Códigos de habilidades relacionadas. |
| `comentarios` | Comentário pedagógico / orientações de trabalho. |

---

### `bncc_estatisticas()`

Resumo do acervo. Sem parâmetros.

```json
{
  "total_habilidades": 1576,
  "por_etapa": {"Ensino Fundamental": 1304, "Educação Infantil": 93, "Ensino Médio": 179},
  "em_foco_total": 396,
  "em_foco_por_componente": {"Ciências": 56, "Geografia": 53, "História": 37, "Língua Portuguesa": 127, "Matemática": 123}
}
```

---

## Esquema dos registros

Campos retornados por `bncc_lookup` (varia conforme a etapa):

| Campo | Etapas | Descrição |
|---|---|---|
| `codigo` | todas | Código da habilidade. |
| `etapa` | todas | `Ensino Fundamental` / `Educação Infantil` / `Ensino Médio`. |
| `componente` | EF | Componente curricular. |
| `area` | EM | Área do Ensino Médio. |
| `ano_ou_faixa` | EF/EI | Ano ('06') ou faixa ('69'); faixa etária para EI. |
| `campo_experiencia` | EI | Campo de experiência. |
| `unidade_tematica` | EF | Unidade temática (ou prática de linguagem / eixo). |
| `objeto_conhecimento` | EF | Objeto de conhecimento. |
| `habilidade` | todas | Enunciado da habilidade. |
| `em_foco` | todas | `true` se está no Mapa de Foco. |
| `mapa_foco` | em foco | Objeto com a camada pedagógica (ver acima). |

---

## Semântica do filtro de ano

O parâmetro `ano` aceita `6`, `06` ou `6º` (a pontuação é ignorada) e segue a
convenção de codificação da BNCC:

- **Ano único** vem com zero à esquerda: `06` = 6º ano.
- **Faixa** vem sem zero, com 1º dígito < 2º: `69` = 6º ao 9º, `15` = 1º ao 5º,
  `35` = 3º ao 5º, `12` = 1º e 2º.

Buscar `ano="6"` retorna tanto as habilidades exclusivas do 6º ano (`EF06...`)
quanto as de faixas que incluem o 6º (`EF69...`, `EF67...`).

---

## Procedência dos dados

Os CSVs em `data/` são gerados por dois scripts no diretório-pai do projeto:

1. **`extrair_objetos.py`** — extrai unidade temática + objeto de conhecimento
   do PDF oficial da BNCC (EI/EF), explorando o layout em spread de duas páginas
   e casando por coordenada vertical. Cobre 100% das 1304 habilidades EF.
2. **`add_mapa_foco.py`** — lê a planilha unificada do Mapa de Foco
   (`MapasDeFocoBncc_Unificados.xlsx`, Instituto Reúna) e acrescenta as 7
   colunas do Mapa de Foco para as 396 habilidades selecionadas.

Para regerar: rodar os dois scripts (nessa ordem) e copiar
`BNCC_habilidades_enriquecido.csv` → `data/bncc_habilidades.csv` e
`bncc_em_habilidades.csv` → `data/bncc_em.csv`.

---

## Limitações

- O **Mapa de Foco** cobre Língua Portuguesa, Matemática, Ciências,
  História e Geografia do Ensino Fundamental. Para Arte, Educação Física,
  Língua Inglesa, Ensino Religioso, Educação Infantil e Ensino Médio, `em_foco`
  é sempre `false` — porque não há Mapa de Foco publicado para esses, não por
  lacuna do acervo.
- Educação Infantil não tem unidade temática nem objeto de conhecimento (usa
  campos de experiência); esses campos ficam vazios para EI.


---

## Estrutura do projeto

```
bncc-mcp/
├── pyproject.toml        # empacotamento; console script `bncc-mcp`
├── README.md             # este arquivo
├── LICENSE               # MIT (cobre o código)
├── ATTRIBUTION.md        # proveniência e licenças dos dados
├── CHANGELOG.md
├── bncc_mcp/
│   ├── __init__.py
│   ├── __main__.py       # `python -m bncc_mcp`
│   ├── server.py         # servidor MCP (FastMCP), 5 tools
│   └── data/
│       ├── bncc_habilidades.csv   # EI + EF, enriquecido + Mapa de Foco
│       └── bncc_em.csv            # Ensino Médio
└── tests/
    └── test_server.py
```

---

## Licença e atribuição

- **Código:** licença MIT (ver `LICENSE`).
- **Dados:** a BNCC (MEC) é de livre uso; o **Mapa de Foco** é © 2020 Instituto
  Reúna e seu reuso exige atribuição e é
  restrito a fins não comerciais. Detalhes e forma de citar em `ATTRIBUTION.md`.

> Dados da BNCC: Ministério da Educação (MEC). Camada de priorização: Mapas de
> Foco da BNCC © 2020 Instituto Reúna (institutoreuna.org.br), usados com
> autorização.
