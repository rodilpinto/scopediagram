# PPTX — log (append-only, mais novo no topo)

## [2026-10-05] feat | Passe do nuati-framework (D-C22/D-C23), framework @ v0.1.0 (`ab3fa66`)

Decisões do Rodrigo no passo 0 (05/10): mapeamento `main` = produção (sem mudança até a promoção) e `homologacao` =
`main` + merge de `feat/llm-cadeia` + framework; branding com rodapé **só da marca** (`rodape(unidades=())`);
**sem** `extracao_texto` (o `input_parser.py` com `pypdf` fica); dado interno sai dos `.example` e dos docs, sem
reescrever o histórico. ⚠ A URL do app de produção do scopediagram ainda não foi informada (a resposta veio com a
do DOU-clipping).
- Tags de volta (anotadas, nos dois remotos): `pre-framework-2026-10-05-main` (`0b5aee1`) e
  `pre-framework-2026-10-05-feat-llm-cadeia` (`265f48a`).
- Linha de base (`feat/llm-cadeia`, requirements instalados): app 19 passam; `llm_cadeia` 1.0.1 23 passam. PPTX do
  exemplo fixo (`tests/test_generation._sample(3)`) renderizado no PowerPoint: 5 PNGs.
- `homologacao` = `de34e02` (merge) + um commit por recurso, todas as pastas com a árvore git idêntica à da v0.1.0:
  `llm_cadeia` 1.1.0 (`28386b1`), `pptx_opc` 1.0.0 (`514d71c`), `tempo_economizado` 1.0.0 (`22ee8e5`, etapas em
  `economia.py`, mesmo número da conta antiga, 5 testes novos), `branding` 1.0.0 (`e4278bc`); dado interno
  (`67beb1b`).
- Testes depois: app 24; `llm_cadeia` 31; `pptx_opc` 9 + 1 pulado (10/10 com `NUATI_TESTE_POWERPOINT=1`);
  `tempo_economizado` 31; `branding` 15.
- pptx_opc: o mesmo exemplo renderizado com `python -m pptx_opc.render_powerpoint` deu 5/5 PNGs iguais pixel a pixel
  aos da linha de base. Primeira vez que o `pptx_opc` roda dentro de um app.
- Ao vivo (PC do trabalho): `python -m llm_cadeia` com todos os provedores configurados respondendo em ao menos um
  modelo; extração real pelo `llm.extract_scope` e pelo app local (porta 8531): "Última resposta: local
  (google/gemma-4)", PPTX gerado e aberto no PowerPoint, "Tempo de trabalho manual poupado: cerca de 7h42min",
  cabeçalho, título da aba e logo no rodapé.
- Próximo: passo do Streamlit (Rodrigo) e conferência no ar; ver `BLOCKED-ON-RODRIGO.md`.

---

## [2026-09-29] checkpoint | Handoff da sessão llm_cadeia + pausa do framework

- State file (`SESSION-ONBOARD-pptx.md`) reescrito: estava em 13/07 (branch D3 "não mergeada", secrets.example
  "pendente"); agora cobre o app inteiro (PPTX + LLM) e a pausa D-C23.
- Criados na raiz: `BLOCKED-ON-RODRIGO.md` (ações só-humano) e `LESSONS.md` (lições transversais desta e da sessão
  de 13/07). `_TODO.md` reorganizado (P0 = aguardar o passe do framework); itens velhos de D3 fechados.
- `_DECISOES-PENDENTES.md`: eco das D-C22/23/24 (fonte: buscador) e marca de "superado" na afirmação da D3 de que
  não havia PowerPoint nesta máquina.
- `/onboard-pptx` reescrito (apontava snapshot inexistente e a branch `feature/template-ppt-generation`).
- Snapshot de memória `pptx_state_2026-09-29.md` (autorizado pelo Rodrigo).

---

## [2026-09-29] pausa | Pausa para o framework (D-C23), branch `feat/llm-cadeia` @ `b972665`

Centralização pedida pela sessão do buscador (decisões D-C22/D-C23/D-C24 em `buscador-normativos/_DECISOES-PENDENTES.md`):
- **D-C22:** dois ambientes por app: `main` = estável/produção (+ espelho no servidor do Nuati) e `homologacao` =
  playground. Substitui a proposta de 29/09 desta sessão (`deploy`/`main`), que não foi executada. A migração é feita
  no passe único da D-C23; aqui nada foi criado, renomeado ou recriado no Streamlit.
- **D-C23:** origem única do que é comum passa a ser `rodilpinto/nuati-framework`.
- **D-C24:** `llm_cadeia/` congelada (versão 1.0.1, procedência `buscador-normativos @ 7f1c069`). Não editar; defeito vira
  pedido à sessão do framework.
Estado: `main` = `0b5aee1` (merge do llm_cadeia 1.0.1, servida pelo Streamlit Cloud segundo os docs do projeto;
não conferido em share.streamlit.io). Branch de trabalho `feat/llm-cadeia` = `b972665` + este registro, empurrada nas
duas remotes. Aguardando o passe do framework.

---

## [2026-09-28] feat | `llm_cadeia` 1.0.1 recopiado + merge de `feat/llm-cadeia` em `main`

Rodrigo esclareceu que a versão do diagrama de escopo apresentada na reunião é outra: liberado mergear aqui.
Os 3 achados da adoção foram corrigidos **na origem** (`buscador-normativos`, `llm_cadeia` 1.0.1) e a pasta foi
recopiada sem edições (`diff -r` = idêntica, fora a linha de procedência):
- "Última resposta" agora aparece na mesma execução (gancho `ao_responder`); o `st.rerun()` do `app.py` foi
  retirado e o app foi verificado ao vivo sem ele (porta 8531): barra lateral "Última resposta: local (google/gemma-4)".
- OpenAI de raciocínio (`gpt-5*`): repete com `max_completion_tokens` e sem `temperature`. ⚠ Só teste com dublê.
- Docstrings desatualizadas do módulo corrigidas.
Testes: `llm_cadeia` 23 passed; `tests` 19 passed.

---

## [2026-09-28] feat | Adoção do llm_cadeia (branch `feat/llm-cadeia`, NÃO mergeada)

Trocadas as chamadas diretas a Gemini/OpenAI de `llm.py` pelo módulo compartilhado
`llm_cadeia` (cópia de `buscador-normativos @ 3edba4d`, v1.0.0, via `git archive`, sem edições;
`diff -r` contra a origem: idêntica). Tag `pre-llm-cadeia` (= `6083a90`) nas duas remotes.
`main` intocada: é dela que o Streamlit Cloud faz deploy; merge só após a reunião, com ok do Rodrigo.

- `llm.py`: `extract_scope(text) -> (ScopeDiagram, origem)`; mesmo prompt (`prompts/extraction.txt`),
  mesma validação pydantic; `gerar(..., json=True, max_tokens=16384)`. `r.texto is None` →
  `LLMUnavailableError` com `r.tentativas`; resposta vazia → `LLMResponseError`.
- `app.py`: seletor Gemini/OpenAI + campo "Modelo" substituídos por `painel_llm()`; "Extraído por"
  abaixo do resultado; `st.rerun()` após extrair para a barra lateral mostrar "Última resposta".
- OpenAI paga deixa de ser segredo do app: vira "Usar minha própria chave de IA" › Outro.
- `requirements.txt`: + `requests`, − `openai` (não é mais importado).
- `.streamlit/secrets.toml.example` restaurado e reescrito com os nomes do `llm_cadeia`; `.env.example` e README idem.

Auditoria de documentação do código removido (o `llm.py` antigo não tinha comentários nem docstrings):
nomes `GEMINI_API_KEY`/`GOOGLE_API_KEY`/`OPENAI_API_KEY`/`LLM_PROVIDER`/`GEMINI_MODEL`/`OPENAI_MODEL`
nas mensagens de erro e na barra lateral → README + `secrets.toml.example` (nomes novos);
`GOOGLE_API_KEY` e `*_MODEL` não existem no `llm_cadeia` (registrado aqui). Modelos padrão antigos
(`gemini-2.5-flash`, `gpt-5-mini`) → substituídos pelas listas do módulo (`GEMINI_MODELOS_PADRAO`).
`response_json_schema` do Gemini não é mais enviado (o `llm_cadeia` só manda `response_mime_type`);
o schema continua no texto do prompt e o pydantic continua validando.

Verificado ao vivo nesta máquina (rede da Câmara), segredos de `~/.streamlit/secrets.toml` carregados
via `tomllib` no processo:
- `pytest llm_cadeia/test_llm_cadeia.py` → 19 passed; `pytest tests` → 19 passed (antes e depois).
- `python -m llm_cadeia`: local (gemma-4) ok; gemini, gemini-2, groq-2, cerebras-2 e openrouter-2
  respondem (os erros foram 503/404/429 de modelo, não de rede) → **o proxy da Câmara deixa passar
  os 5 serviços externos**.
- Gemma local com `sistema=` + `json=True` (só `LLM_*` no ambiente, `LLM_ORDEM=local`): 11,8 s,
  JSON sem cerca, `json.loads` OK, acentos corretos. (Na origem isso estava "não verificado".)
- `extract_scope` de texto real (Liquidar NF): só local 48,8 s; cadeia inteira 46,3 s (local);
  `LLM_ORDEM=gemini,...` 79,5 s → `gemini (gemini-3-flash-preview)` após 503/404 nos anteriores.
  Todos passaram no pydantic.
- App (`streamlit run`, porta 8502) pelo navegador: gerou, barra lateral "Última resposta: local
  (google/gemma-4)", prévia + "Baixar PowerPoint" presentes.

Lições:
- No Windows, o Bloco de Notas salva `secrets.toml` como `secrets.toml.toml` (extensão oculta);
  o Streamlit não acha. Conferir com `ls`.
- Console do Git Bash mostra `�` em acentos de saída Python: é só a codificação do console
  (`PYTHONIOENCODING=utf-8` resolve), não defeito do LLM.
- A chave `GEMINI_API_KEY` (sem sufixo, criada em set/2026) recebe 404 em `gemini-2.5-flash` e
  `gemini-2.5-flash-lite` ("no longer available to new users"). A `main` publicada usa
  `gemini-2.5-flash` por padrão: se o Cloud usar essa chave, é preciso `GEMINI_MODEL` com um modelo 3.x.
- `painel_llm()` roda antes de `gerar`, então "Última resposta" só aparece na execução seguinte
  do script; aqui resolvido com `st.rerun()` no app (sugestão para o README da origem).

---

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
