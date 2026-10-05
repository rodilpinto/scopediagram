# scopediagram

App Streamlit que extrai um modelo IGOE de texto (via LLM) e gera um PowerPoint de
diagrama de escopo. A geração do PPTX **preenche o template real de referência
(SmartArt)** — pacote `templatefill/`; o gerador antigo (formas do zero) está em
`ppt_legacy.py`.

## Resuming work
- **pptx** (cobre o app inteiro: PPTX + LLM via `llm_cadeia/`) — rode `/onboard-pptx`. Estado:
  `docs/SESSION-ONBOARD-pptx.md`. Ações só do Rodrigo: `BLOCKED-ON-RODRIGO.md`. Checkpoint com `/checkpoint`.
- `llm_cadeia/` é cópia congelada de um módulo compartilhado: não editar (ver `docs/_DECISOES-PENDENTES.md`).
