# scopediagram

App Streamlit que extrai um modelo IGOE de texto (via LLM) e gera um PowerPoint de
diagrama de escopo. A geração do PPTX **preenche o template real de referência
(SmartArt)** — pacote `templatefill/`; o gerador antigo (formas do zero) está em
`ppt_legacy.py`.

## Resuming work
- **pptx** (cobre o app inteiro: PPTX + LLM via `llm_cadeia/`) — rode `/onboard-pptx`. Estado:
  `docs/SESSION-ONBOARD-pptx.md`. Ações só do Rodrigo: `BLOCKED-ON-RODRIGO.md`. Checkpoint com `/checkpoint`.
- `llm_cadeia/`, `pptx_opc/`, `tempo_economizado/` e `branding/` são cópias do `nuati-framework` (v0.1.0): não
  editar; defeito vira pedido ao framework (D5 em `docs/_DECISOES-PENDENTES.md`). Branches: `main` = produção,
  `homologacao` = trabalho (D-C22).
