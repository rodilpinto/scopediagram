---
title: "Decisões abertas — ledger consolidado (PPTX)"
maintained_by: Claude Code sessions; só Rodrigo resolve
last_updated: 2026-10-05
related: [_TODO.md, SESSION-ONBOARD-pptx.md, log.md]
---

# Decisões abertas — o que precisa da chamada do humano

> `_TODO.md` é o ledger de TAREFAS; este é o de DECISÕES. Status: 🔴 OPEN · 🟡 EM ANÁLISE · 🟢 DECIDIDA.
> Sugestões aqui são propostas, não fatos validados.

## D1 — Resultado do teste ao vivo do app define os próximos ajustes
- **Status:** 🟢 DECIDIDA (2026-07-08)
- **Tipo:** validação / direção
- **Onde aparece:** app em http://localhost:8501; PPTX baixado

**A questão.** O usuário testou o app com conteúdo real. O que ele reportasse
(campos extraídos corretos? algum overflow? traceback?) decidiria o próximo trabalho.

**Decisão tomada:** ✅ Testou e funcionou bem — sem overflow, sem traceback reportado.
Auto-fit das bandas não foi necessário (não houve relato de overflow nelas).

---

## D2 — Mergear a branch `feature/template-ppt-generation` em `main`?
- **Status:** 🟢 DECIDIDA (2026-07-08)
- **Tipo:** git / release
- **Onde aparece:** repositório; deploy no Streamlit Cloud

**A questão.** A nova geração vivia numa branch. Quando o usuário validasse o app,
mergear em `main` (a `main` é o que o Streamlit Cloud faz deploy).

**Decisão tomada:** ✅ Opção A — merge direto (o usuário optou por simplicidade em
vez de PR, após validar o app ao vivo). Testes passaram antes e depois do merge.
Push feito para os dois remotes configurados (`github` e `origin`, o remoto interno).

---

## D3 — Precisamos de editabilidade fiel do SmartArt no PowerPoint?
- **Status:** 🟢 DECIDIDA (2026-07-08) — implementada
- **Tipo:** arquitetura
- **Onde aparece:** `templatefill/igoe.py::_sync_data_nodes` / `_rebuild_lane_nodes` / `_find_lane_roots`

**A questão.** O render usa o desenho em cache (correto). Mas o **modelo de dados**
do SmartArt só era sincronizado best-effort (`_sync_data_text`, removida). Se o
usuário editasse o SmartArt dentro do PowerPoint, o layout podia regenerar a partir
do modelo de dados desatualizado e reexibir texto do template.

**Decisão tomada:** ✅ Opção B — reconstruir os nós do modelo de dados. Implementado
e verificado:
- Spec (`docs/superpowers/specs/2026-07-08-smartart-data-model-editability-design.md`)
  verificada em 2 rodadas por subagentes independentes antes da implementação.
- Implementação em 3 camadas: `_find_lane_roots` (descoberta por texto, nunca por
  ordem de documento) → `_rebuild_lane_nodes` (mutator puro em memória, replica o
  padrão nativo do SmartArt) → `_sync_data_nodes` (orquestrador transacional: só
  grava se as 3 lanes reconstruírem sem exceção — nunca escreve XML pela metade).
- 6 tasks TDD, cada uma implementada e revisada por subagentes independentes
  (aprovadas), plano em `docs/superpowers/plans/2026-07-08-smartart-data-model-editability.md`.
- Revisão final de branch inteira (Opus): pronta pra merge, com 1 achado importante
  (faltava `<dgm:spPr/>` vazio nos nós reconstruídos — presente no template nativo,
  opcional pelo schema mas corrigido por segurança) — corrigido e commitado.
- QA visual (LibreOffice→PDF→PNG) confirma zero mudança no render (esta feature só
  toca o modelo de dados).
- ⚠ **Superado em 2026-07-13:** o PowerPoint real ESTÁ instalado nesta máquina e a validação foi feita com sucesso via COM (ver `SESSION-ONBOARD-pptx.md` §3 e `LESSONS.md`). Texto original, mantido como histórico: **Limite conhecido, não coberto por esta decisão:** a validação real de "abrir no
  PowerPoint de verdade, editar um item do SmartArt, e o resultado continuar
  consistente" não pôde ser testada nesta máquina (sem PowerPoint instalado;
  LibreOffice não recalcula SmartArt a partir do modelo de dados). Isso é do usuário
  confirmar manualmente.

---

## D4 — Mergear `feat/llm-cadeia` em `main` (deploy do llm_cadeia)?
- **Status:** 🟢 DECIDIDA (2026-09-28)
- **Tipo:** deploy
- **Onde aparece:** branch `feat/llm-cadeia` (github + remoto interno); tag de volta `pre-llm-cadeia`

**A questão.** A branch troca Gemini/OpenAI diretos pela cadeia `llm_cadeia` (verificada ao vivo,
ver log 2026-09-28). Mergear muda o app publicado: a OpenAI paga sai dos Secrets e vira chave do
usuário; o Gemini deixa de receber `response_json_schema`; os modelos passam a ser os do módulo.

📝 Sugestão minha (não validada): mergear depois da reunião, com os Secrets do Cloud já só com as
chaves gratuitas (sem `LLM_BASE_URL`), e testar uma geração no Cloud logo após o Reboot.

**Decisão tomada:** ✅ Rodrigo autorizou o merge + push em 28/09 (a versão da reunião é outra).

---

## D5 — Como este app adota o nuati-framework (passe D-C22/D-C23)
- **Status:** 🟢 DECIDIDA (2026-10-05, Rodrigo, passo 0 do passe)
- **Tipo:** escopo / deploy

**Decisão tomada:**
- **(b) Branches:** `main` continua sendo a produção; `homologacao` = `main` + merge de `feat/llm-cadeia` + framework
  (promoção futura por fast-forward). O framework vai para a produção depois da conferência no ar, com o ok dele.
- **(c) Branding:** sim, rodapé **só com a marca** (`cd_brand.rodape(unidades=())`): app público (MIV p.14; F-A10 do
  framework). Ficam "Feito por Rodrigo Pinto" e a versão.
- **(d) extracao_texto:** não adotar ("não precisa"); `input_parser.py` (pypdf) fica.
- **(e) Dado interno:** sai dos `.example` e dos docs; o histórico não é reescrito.
- 📝 Escolhas minhas (não validadas): tempo economizado sem descontar o tempo da ferramenta (`automatico_min=0`), para
  manter o número de antes; etapas num módulo próprio (`economia.py`), para testar sem Streamlit.

## D6 — URL e branch do app de produção; existe app de teste?
- **Status:** 🔴 OPEN (pergunta do passo 0, 05/10)
- **Tipo:** deploy

A resposta de 05/10 trouxe a do DOU-clipping (`dou-clipping-app.streamlit.app`, `master`), não a deste app. Sem a
URL do scopediagram, o passo do Streamlit (apagar e recriar a produção na `main`, criar a homologação) não pode ser
entregue com os endereços certos.

---

## Decisões de outro repo que valem para este app (eco; a fonte manda)

Fonte: `github.com/rodilpinto/buscador-normativos`, arquivo `_DECISOES-PENDENTES.md`, seção
"Decididas em 2026-09-29" (ler com `git -C ../buscador-normativos show origin/master:_DECISOES-PENDENTES.md`).
Todas 🟢 decididas pelo Rodrigo em 29/09; aqui só o que cada uma bloqueia neste app.
- **D-C22 · dois ambientes:** `main` = estável/produção (+ espelho no servidor do Nuati), `homologacao` = playground.
  Bloqueia: criar `homologacao`, recriar os apps no Streamlit (não dá para trocar a branch de um app), apagar
  `feat/llm-cadeia`. Tudo isso acontece **só** no passe da D-C23. A proposta `deploy`/`main` desta sessão (29/09)
  foi superada e não executada.
- **D-C23 · framework central** `rodilpinto/nuati-framework` = origem única do que é comum. Bloqueia: o passe único
  deste app (adotar o framework + migrar os ambientes). Candidatos daqui ao framework: `log.md` 29/09.
- **D-C24 · `llm_cadeia/` congelada.** Não editar a cópia; defeito vira pedido à sessão do framework.

