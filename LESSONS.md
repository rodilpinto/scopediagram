# LESSONS: scopediagram

<!-- Append-only. Mais novas no topo. Formato: Problema / Causa-raiz / Conserto / Regra (+ Cobertura quando o
     conserto é estrutural). Lições específicas do PPTX ficam em docs/SESSION-ONBOARD-pptx.md §3 e docs/log.md. -->

## 2026-09-28 · Credencial do git.camara.gov.br expira: push do `origin` falha com "Authentication failed"

**Problema.** Pushes para `origin` (git.camara.gov.br) falharam 3 vezes em 28-29/09, com o GitHub funcionando.
**Causa-raiz.** Credencial HTTPS do Git Credential Manager expira; não é erro de rede nem de permissão.
**Conserto.** `! git fetch origin` (ou o próprio push) no prompt do Claude Code abre o login; depois disso passa.
**Regra.** Push que envolve `origin`: se falhar por auth, empurre o GitHub, registre no `BLOCKED-ON-RODRIGO.md` e
peça o login; nunca contornar trocando credencial ou URL.

## 2026-09-28 · Chave Gemini nova recebe 404 em `gemini-2.5-flash`

**Problema.** A chave do projeto nuati.secin (criada em set/2026) recebe 404 "no longer available to new users" em
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
`pywin32`; `tools/render_pptx_powerpoint.py` renderiza via COM.
**Regra.** Afirmação de ausência ("não existe", "não dá") vira fato só depois de um comando que a teste.
