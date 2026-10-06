---
title: scopediagram (PPTX + LLM) · session onboarding / state snapshot
maintained_by: Claude Code sessions; humans can edit too
last_updated: 2026-10-06
related: [_TODO.md, _DECISOES-PENDENTES.md, log.md, ../BLOCKED-ON-RODRIGO.md, ../LESSONS.md]
---

# scopediagram: session onboarding

Ponto de entrada único (a área `pptx` cobre o app inteiro). ≤ 1 página. Histórico em `log.md`; tarefas em
`_TODO.md`; decisões em `_DECISOES-PENDENTES.md`; ações só-humano em `../BLOCKED-ON-RODRIGO.md`; lições em
`../LESSONS.md`.

## 1. O que é (30s)
App Streamlit (`app.py`): extrai um modelo IGOE de texto via LLM (`llm.py` → `ScopeDiagram` em `schema.py`) e gera
o PowerPoint **preenchendo o template real (SmartArt)**, pacote `templatefill/`. O LLM passa pelo módulo
compartilhado `llm_cadeia/` (cadeia local Gemma → Gemini → Groq → Cerebras → OpenRouter). Remotes: `github`
(github.com/rodilpinto/scopediagram) e `origin` (remoto interno; URL em `git remote -v`).

## 2. Estado na última pausa (2026-10-06)
**Passe do nuati-framework concluído** (D5/D7; log 05-06/10), falta só a limpeza (apagar `feat/llm-cadeia`).
- **`main` = `a4acec5` = tag `v1.1.0`** (produção, `diagrama-escopo.streamlit.app`), com `llm_cadeia` 1.1.0,
  `pptx_opc` 1.0.0, `tempo_economizado` 1.0.0 e `branding` 1.0.0 (pastas com a árvore git idêntica à do framework
  v0.1.0) e "Versão 1.1.0" no rodapé. Conferida no ar em 06/10.
- **`homologacao`** (trabalho do dia a dia, `diagrama-escopo-homologacao.streamlit.app`): igual à `main` mais commits
  de journal. A URL antiga `diagramadeescopo.streamlit.app` não existe mais.
- **Promover:** trocar `VERSAO_APP` em `app.py`, `git switch main && git merge --ff-only homologacao`,
  `git tag -a vX.Y.Z`, push de `main` e da tag nos dois remotos; só com ok do Rodrigo.
- **Retorno:** tags anotadas `pre-framework-2026-10-05-main` e `pre-framework-2026-10-05-feat-llm-cadeia`; voltar a
  `main` por `git revert`, nunca por push forçado.
- **Working tree:** arquivos não rastreados do usuário (2 `.pptx` na raiz e `.claude/settings.local.json`), intocados.

## 3. Achados críticos (não perder)
- Pastas do framework (`llm_cadeia/`, `pptx_opc/`, `tempo_economizado/`, `branding/`): não editar; defeito vira
  pedido ao `nuati-framework`. Procedência só no registro de cópias do framework (README §4), nunca na pasta.
  O que é do app fica fora delas: etapas do tempo economizado em `economia.py`, tema em `.streamlit/config.toml`.
- Da rede da Câmara (PC do trabalho, 28/09) os 4 serviços externos passaram: Gemini, Groq, Cerebras, OpenRouter. O Gemma (servidor local, `LLM_BASE_URL`) só é alcançável daqui;
  no Cloud, sem `LLM_BASE_URL`.
- Testes locais: `py -3.13 -m pytest tests -q` e `py -3.13 -m pytest llm_cadeia/test_llm_cadeia.py -q` (o `python`
  do PATH é o atalho da Store; use o launcher `py`). Segredos locais em `~/.streamlit/secrets.toml` (fora do repo).
- Porta 8502 pode estar ocupada pelo app de Checklist; suba o scopediagram em outra (`--server.port 8531`).
- PPTX: template é **SmartArt**; `python-pptx` não o edita → `templatefill/` mexe no XML (zip + lxml). O LibreOffice
  **não** regenera SmartArt; o `drawingN.xml` em cache é obrigatório. Cada lane = 1 `dsp:sp` com N parágrafos; no
  `data*.xml` cada item é um `dgm:pt` (D3). Lanes são achadas **por texto**, nunca por ordem.
- QA visual fiel: PowerPoint real via COM, `py -3.13 -m pptx_opc.render_powerpoint <pptx> <pasta>`; aproximação: LibreOffice → PDF →
  PyMuPDF.

## 4. Disciplina
Um chunk por vez → verificar → atualizar durables → commit → `/checkpoint`. Trabalho em `homologacao`; push na `main` só com ok do
Rodrigo (promoção).

## 5. Próximo movimento (recomendação)
1. Com a confirmação do Rodrigo: apagar `feat/llm-cadeia` (`../BLOCKED-ON-RODRIGO.md`).
2. Trabalho novo em `homologacao`; P2 de `_TODO.md` (rótulo SUBPROCESSOS, `use_container_width`).

## 6. Ponteiros
| Doc | Propósito |
|---|---|
| `_TODO.md` · `_DECISOES-PENDENTES.md` · `log.md` | tarefas · decisões (+ eco D-C22/23/24) · timeline |
| `../BLOCKED-ON-RODRIGO.md` · `../LESSONS.md` | ações só-humano · lições transversais |
| `../llm_cadeia/README.md` | módulo de LLM (uso, segredos, changelog) |
| `../.streamlit/secrets.toml.example` | nomes dos segredos (sem valores) |
| `superpowers/specs/2026-07-02-template-based-ppt-generation-design.md` | arquitetura do PPTX |
| `superpowers/specs/2026-07-08-smartart-data-model-editability-design.md` | editabilidade do SmartArt (D3) |
| `../templatefill/{igoe,builder}.py` · `../pptx_opc/` (OPC + render, do framework) | motor PPTX · QA via PowerPoint |

## 7. Como atualizar
Ao mudar de estado: §2/§5, `last_updated`, entrada no `log.md`, ledgers; snapshot de memória datado se mudou muito.
