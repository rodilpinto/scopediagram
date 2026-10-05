---
title: scopediagram (PPTX + LLM) · session onboarding / state snapshot
maintained_by: Claude Code sessions; humans can edit too
last_updated: 2026-09-29
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

## 2. Estado na última pausa (2026-09-29)
**⏸ Em pausa para o framework central** (D-C22/D-C23/D-C24, decididas no buscador; eco e o que bloqueiam em
`_DECISOES-PENDENTES.md`). O próximo trabalho neste app é o passe único que vem da sessão do framework.
- **`main` = `0b5aee1`** (merge do `llm_cadeia` 1.0.1, D4). Os docs dizem que o Streamlit Cloud serve a `main`;
  **não conferido** no painel, e **nenhuma geração no Cloud foi verificada** (ver `BLOCKED-ON-RODRIGO.md`).
- **Branch de trabalho `feat/llm-cadeia`**: à frente da `main` só com docs (procedência 7f1c069, log, este
  checkpoint). Igual no `github` e no `origin` (`git ls-remote`); se o push do `origin` falhar por auth, `LESSONS.md`.
  Esta sessão: `bc75099` → `7a2c6ba` → `b972665` → `9d52dc5` → commit do checkpoint. ⚠ O SHA mais novo listado
  aqui está sempre um atrás do commit que gravou este arquivo; a cadeia real termina em `git log --oneline -3`.
- **Retorno:** tag `pre-llm-cadeia` ("antes do llm_cadeia", = `6083a90`): `git checkout pre-llm-cadeia`.
- **Working tree:** arquivos não rastreados do usuário (`git status --short`: 2 `.pptx` na raiz e
  `.claude/settings.local.json`), intocados de propósito; não são necessários para retomar.
- **Verificado ao vivo (28/09, rede da Câmara):** Gemma `google/gemma-4` com `sistema=`+`json=True`; extração IGOE
  via Gemma e via Gemini passando no pydantic; app gerando com "Última resposta: local (google/gemma-4)" sem
  `st.rerun()`. **Assumido/não verificado:** repetição `max_completion_tokens` da OpenAI (só dublê).

## 3. Achados críticos (não perder)
- `llm_cadeia/` está **congelada** (D-C24): não editar; defeito vira pedido à sessão do framework. Procedência na
  1ª linha de `llm_cadeia/README.md`. A spec que esse README cita (`docs/superpowers/specs/2026-09-28-llm-cadeia-portatil-design.md`)
  **não existe aqui**: vive no repo buscador-normativos.
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
Um chunk por vez → verificar → atualizar durables → commit → `/checkpoint`. Push só da branch de trabalho, nunca
da `main` sem ok do Rodrigo.

## 5. Próximo movimento (recomendação)
1. Aguardar o passe do framework (D-C23); não começar feature nova aqui antes dele.
2. Enquanto isso, só o que está em `../BLOCKED-ON-RODRIGO.md` (ações do Rodrigo).

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
