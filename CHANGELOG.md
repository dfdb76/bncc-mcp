# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/).

## [0.2.1] - 2026-07-24

### Corrigido
- Habilidades do Ensino Médio (`bncc_em.csv`) cujo enunciado trazia texto
  extraído **além da própria habilidade** — rodapés de página, cabeçalhos de
  área, blocos de comentário e marcadores de nota de rodapé. 76 habilidades
  reprocessadas contra o PDF oficial da BNCC-EM; nenhuma passa de ~800
  caracteres (antes, casos com dezenas de milhares). Corrigido também um
  artefato de hifenização ("pe la" → "pela") em EM13LP26.


## [0.2.0] - 2026-06-09

### Adicionado
- Dataset de **Computação** (complemento à BNCC, anexo ao Parecer CNE/CEB
  nº 2/2022): 141 habilidades (`bncc_comp.csv`) — 11 Educação Infantil,
  104 Ensino Fundamental, 26 Ensino Médio — com o campo `eixo` (Pensamento
  Computacional, Mundo Digital, Cultura Digital). Acervo total: 1717
  habilidades. Fonte: computacional.com.br (Prof. Christian Brackmann /
  IFFAR, CC BY-NC-SA 4.0) — ver `ATTRIBUTION.md`.

## [0.1.0] - 2026-05-29

### Adicionado
- Servidor MCP da BNCC com 5 tools: `bncc_lookup`, `bncc_buscar`,
  `bncc_listar`, `bncc_mapa_de_foco`, `bncc_estatisticas`.
- 1576 habilidades (1304 Ensino Fundamental, 93 Educação Infantil,
  179 Ensino Médio).
- Unidade temática + objeto de conhecimento em 100% das habilidades EF.
- Camada do Mapa de Foco (Instituto Reúna) para 396 habilidades selecionadas.
- Empacotamento instalável (`pip install`), console script `bncc-mcp`.
