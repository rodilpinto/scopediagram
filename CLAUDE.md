# scopediagram

App Streamlit que extrai um modelo IGOE de texto (via LLM) e gera um PowerPoint de
diagrama de escopo. A geração do PPTX **preenche o template real de referência
(SmartArt)** — pacote `templatefill/`; o gerador antigo (formas do zero) está em
`ppt_legacy.py`.

## Resuming work
- **scopediagram** (área única, cobre o app inteiro; chamava-se `pptx` até 06/10): rode `/onboard-scopediagram`. Estado:
  `docs/SESSION-ONBOARD-scopediagram.md`. Ações só do Rodrigo: `BLOCKED-ON-RODRIGO.md`. Checkpoint com `/checkpoint`.
- `llm_cadeia/`, `pptx_opc/`, `tempo_economizado/` e `branding/` são cópias do `nuati-framework` (v0.1.0): não
  editar; defeito vira pedido ao framework (D5 em `docs/_DECISOES-PENDENTES.md`). Branches: `main` = produção,
  `homologacao` = trabalho (D-C22).
