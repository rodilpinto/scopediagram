# PPTX — log (append-only, mais novo no topo)

## [2026-07-07] fix | Nova geração de PPTX por template + app ao vivo

Trocada a geração do PowerPoint: em vez de desenhar formas do zero
(`ppt_legacy.py`), o app agora **preenche o template real de referência (SmartArt)**.

- Pacote `templatefill/`: `opc.py` (zip+lxml: delete/clone de slides com partes SmartArt),
  `igoe.py` (título/bandas/eventos + 3 lanes; reflow inferior; auto-fit de fonte nas lanes),
  `builder.py` (ScopeDiagram → capa + IGOE do processo + 1 IGOE por subprocesso, clonando
  a mesma unidade do template p/ consistência). `ppt.py` virou shim; antigo em `ppt_legacy.py`.
- Spikes que fundamentaram a abordagem (verificados por render): edição de texto no XML →
  repack → render é pixel-perfect; LibreOffice NÃO regenera nem "assa" SmartArt; cada lane
  é 1 shape com N parágrafos.
- Bugs achados e corrigidos no QA visual (LibreOffice→PDF→PyMuPDF→PNG): rótulo OBJETIVO
  DO PROCESSO vs SUBPROCESSO; "SUBPROCESSOS" quebrando na label girada; caixas EVENTO
  transbordando a borda inferior (parágrafo vazio + âncora central) → strip de vazios +
  âncora topo + crescer p/ cima + z-order à frente. 2 QA independentes: 5 slides limpos.
- `app.py`: pré-visualização Graphviz tornada não-fatal (o `dot` não está no PATH aqui) —
  o download do PPTX é o entregável e não pode ser bloqueado pela prévia.
- Testes de fumaça `tests/test_generation.py` (pptx válido, contagem de slides, conteúdo
  injetado, sem vazamento do template). `lxml` declarado no requirements.
- App subido em background (id `btd9wtk2a`) em http://localhost:8501; HTTP 200. Usuário
  vai testar a extração por campo + a qualidade do PPTX baixado.
- Nota importante: **extração NÃO foi tocada** (`llm.py`/prompts/schema intactos) — não há
  regressão de extração possível por esta sessão; a mudança é só no render do PPTX.

Commits: `8bdaa34` (spec) · `f2e55aa` (templatefill+shim) · `55d87ea` (auto-fit+z-order) ·
`2b912ea` (testes+lxml) · `5e9d1b7` (prévia não-fatal). Branch `feature/template-ppt-generation`,
ainda não mergeada em `main`.

---
