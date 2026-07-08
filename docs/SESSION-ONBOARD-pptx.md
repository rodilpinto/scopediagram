---
title: PPTX generation — session onboarding / state snapshot
maintained_by: Claude Code sessions; humans can edit too
last_updated: 2026-07-07
related: [_TODO.md, _DECISOES-PENDENTES.md, log.md]
---

# PPTX (geração do PowerPoint) — session onboarding

Ponto de entrada único para qualquer sessão nova nesta área. ≤ 1 página; atualizado
em cada pausa. Histórico em `log.md`; backlog em `_TODO.md`; decisões abertas em
`_DECISOES-PENDENTES.md`. Snapshot completo em
`~/.claude/projects/C--Users-P-8106-Documents-solucoes-scopediagram/memory/pptx_state_2026-07-07.md`.

## 1. O que é (30s)
App Streamlit (`app.py`) que extrai um modelo IGOE de um texto via LLM (`llm.py` →
`ScopeDiagram` em `schema.py`) e gera um PowerPoint de diagrama de escopo. **Esta
sessão trocou a geração do PPTX**: em vez de desenhar formas do zero (`ppt_legacy.py`),
agora **preenche o template real de referência** (que é SmartArt) — pacote `templatefill/`.

## 2. Estado na última pausa (2026-07-07)
### Feito & commitado (branch `feature/template-ppt-generation`)
- `8bdaa34` — spec da abordagem (`docs/superpowers/specs/2026-07-02-...-design.md`).
- `f2e55aa` — pacote `templatefill/` (opc.py, igoe.py, builder.py) + `ppt.py` vira shim + `ppt_legacy.py`.
- `55d87ea` — auto-fit de fonte nas lanes + z-order das caixas de evento.
- `2b912ea` — testes de fumaça (`tests/test_generation.py`) + `lxml` no requirements.
- `5e9d1b7` — pré-visualização não-fatal (Graphviz `dot` opcional) em `app.py`.
### Working tree
- Limpo, EXCETO `D .streamlit/secrets.toml.example` (deleção NÃO desta sessão — não staged; provavelmente do usuário ao criar o `secrets.toml` real).
- Branch `feature/template-ppt-generation` **não** mergeada em `main`.
### Verificado (não assumido)
- Deck LGPD de 5 slides renderiza limpo — 2 QA independentes por subagente, sem overflow/sobreposição.
- Testes de fumaça passam; N variável de subprocessos funciona; auto-fit testado com 14 itens.
- App subiu e respondeu HTTP 200 em http://localhost:8501; o server em background foi **encerrado** no limite de sessão. **Relançar:** `python -m streamlit run app.py --server.headless true --server.port 8501` (chave em `.streamlit/secrets.toml`).
### Pendente / em aberto
- **Usuário ia testar o app ao vivo** (extração por campo + qualidade do render). Relançar o app antes de retomar; aguardando o retorno do teste dele.
- Bandas (REGULADORES/RECURSOS/OBJETIVO) **não** têm auto-fit — listas longas ali podem transbordar.

## 3. Achados críticos (não perder — custam tempo se redescobertos)
- Template de referência é **SmartArt** (17 diagramas). `python-pptx` NÃO edita SmartArt de forma confiável → por isso o `templatefill/` mexe no XML direto (zip + lxml).
- **LibreOffice NÃO regenera SmartArt** a partir do modelo de dados quando o desenho em cache é removido (render vira lixo). Logo o `drawingN.xml` em cache é obrigatório e é o que editamos. LibreOffice também NÃO "assa" SmartArt→formas no round-trip.
- Cada lane = **1 `dsp:sp` com N parágrafos**; lista variável = editar parágrafos. Bandas/título/eventos = caixas de texto comuns do slide, ordem de shape estável 0–8 nos slides 15/18/21.
- Caixas EVENTO transbordavam (âncora central + parágrafo vazio inicial); corrigido com strip de parágrafos vazios + âncora topo + crescer p/ cima + trazer p/ frente.
- Novo gerador depende **só de lxml** (não de python-pptx). `ppt.py` reexporta `templatefill.builder.generate_ppt_bytes`, com fallback p/ `ppt_legacy`.
- **Extração NÃO foi tocada** (`llm.py`, `prompts/extraction.txt`, `schema.py` intactos) → impossível haver regressão de extração por esta sessão.
- QA visual: LibreOffice `C:\Program Files\LibreOffice\program\soffice.exe` → PDF → PyMuPDF (`fitz`) → PNG. poppler/`dot` NÃO instalados nesta máquina (bash); Read não renderiza PDF aqui.

## 4. Disciplina de trabalho
Um chunk = uma onda; carregue só o contexto necessário. Fecha o chunk: limpeza → verificar/render → atualizar durables → commit. `/onboard-pptx` retoma daqui.

## 5. Próximo movimento (recomendação, não decidido)
1. **Ler o retorno do teste ao vivo do usuário** (traceback? campos certos? render limpo?) e corrigir o que aparecer.
2. Se bandas transbordarem → estender auto-fit às bandas REGULADORES/RECURSOS/OBJETIVO.
3. Considerar merge da branch em `main` (finishing-a-development-branch) + PR.
4. Opcional: melhorar sync do modelo de dados do SmartArt (editabilidade pós-abertura).

## 6. Ponteiros (só caminhos — sem duplicar conteúdo)
| Doc | Propósito |
|---|---|
| `_TODO.md` | ledger de tarefas |
| `_DECISOES-PENDENTES.md` | decisões só-humano |
| `log.md` | timeline append-only |
| `docs/superpowers/specs/2026-07-02-template-based-ppt-generation-design.md` | spec da arquitetura |
| `templatefill/{opc,igoe,builder}.py` | motor OPC / preenchimento IGOE / orquestrador |

## 7. Como atualizar
Ao mudar de estado: atualize §2/§5, bump `last_updated`, prepend em `log.md`, refresque o
ledger de decisões, drope um snapshot de memória datado se o estado mudou materialmente. ≤ 1 página.
