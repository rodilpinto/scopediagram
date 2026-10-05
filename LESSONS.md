# LESSONS: scopediagram

<!-- Append-only. Mais novas no topo. Formato: Problema / Causa-raiz / Conserto / Regra (+ Cobertura quando o
     conserto é estrutural). Lições específicas do PPTX ficam em docs/SESSION-ONBOARD-pptx.md §3 e docs/log.md. -->

## 2026-10-05 · Comparar PPTX gerados: pelos PNGs do PowerPoint, não pelos bytes

**Problema.** Duas gerações do mesmo exemplo dão `.pptx` com bytes e tamanho diferentes (o zip não é determinístico),
o que impede provar "nada mudou" por hash do arquivo.
**Causa-raiz.** Metadados do zip variam a cada `to_bytes`; o conteúdo renderizado não.
**Conserto.** Renderizar os dois com `python -m pptx_opc.render_powerpoint` e comparar os PNGs pixel a pixel
(PIL `ImageChops.difference(...).getbbox() is None`). Duas gerações seguidas deram 5/5 iguais, então a comparação
não tem ruído (passe do framework, 05/10).
**Regra.** QA de "mesmo resultado" no PPTX = PNGs do PowerPoint iguais, com uma dupla de controle antes.

## 2026-10-05 · O Playwright MCP grava snapshots e prints dentro do repo (`.playwright-mcp/`)

**Problema.** Ao conferir o app local pelo navegador, apareceu a pasta `.playwright-mcp/` (snapshots, log do console,
prints) na raiz do repo, sem ser ignorada pelo git. O print de página inteira também não pega a área abaixo da dobra
(o Streamlit rola dentro de um contêiner).
**Conserto.** Salvar prints com caminho relativo em `.playwright-mcp/`, mover o que importa para fora e apagar a
pasta antes do `git add`; para ler a página inteira, usar o snapshot de acessibilidade.
**Regra.** Depois de usar o navegador, `git status --short` antes de qualquer commit.

## 2026-09-28 · Credencial do remoto interno expira: push do `origin` falha com "Authentication failed"

**Problema.** Pushes para `origin` (remoto interno) falharam 3 vezes em 28-29/09, com o GitHub funcionando.
**Causa-raiz.** Credencial HTTPS do Git Credential Manager expira; não é erro de rede nem de permissão.
**Conserto.** `! git fetch origin` (ou o próprio push) no prompt do Claude Code abre o login; depois disso passa.
**Regra.** Push que envolve `origin`: se falhar por auth, empurre o GitHub, registre no `BLOCKED-ON-RODRIGO.md` e
peça o login; nunca contornar trocando credencial ou URL.

## 2026-09-28 · Chave Gemini nova recebe 404 em `gemini-2.5-flash`

**Problema.** A chave sem sufixo (`GEMINI_API_KEY`, criada em set/2026) recebe 404 "no longer available to new users" em
`gemini-2.5-flash` e `gemini-2.5-flash-lite`; o `llm.py` antigo fixava `gemini-2.5-flash`.
**Causa-raiz.** O Google tirou os 2.5 de chaves novas; chaves antigas ainda funcionam, então o erro só aparece ao
trocar de chave.
**Conserto.** O `llm_cadeia` roda uma lista de modelos e pula 404 (`GEMINI_MODELOS_PADRAO` começa nos 3.x).
**Regra.** Nunca fixar um único modelo Gemini no app; trocar de chave exige um teste de geração no ar.

## 2026-09-28 · `secrets.toml` salvo como `secrets.toml.toml` e acentos `�` no console

**Problema.** O Streamlit não achava `~/.streamlit/secrets.toml`; saídas do Python mostravam `�` nos acentos.
**Causa-raiz.** O Windows esconde a extensão (o Bloco de Notas acrescentou `.toml`); o console do Git Bash usa
cp1252.
**Conserto.** `ls ~/.streamlit` para ver o nome real; `PYTHONIOENCODING=utf-8` ao rodar scripts no Git Bash.
**Regra.** Antes de concluir "o LLM devolveu acento quebrado", repetir com `PYTHONIOENCODING=utf-8`.

## 2026-07-13 · "Não há PowerPoint nesta máquina" era suposição, nunca verificada

**Problema.** Vários docs diziam que a validação no PowerPoint real era impossível aqui.
**Causa-raiz.** Afirmação negativa repetida sem ser testada.
**Conserto.** O Office 2013 está em `C:\Program Files (x86)\Microsoft Office\Office15\POWERPNT.EXE`, com
`pywin32`; `python -m pptx_opc.render_powerpoint` renderiza via COM (até 05/10: `tools/render_pptx_powerpoint.py`).
**Regra.** Afirmação de ausência ("não existe", "não dá") vira fato só depois de um comando que a teste.
