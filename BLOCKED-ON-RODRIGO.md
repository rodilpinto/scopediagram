# BLOCKED-ON-RODRIGO: ações que só o Rodrigo pode fazer (scopediagram)

Ledger acumulativo entre sessões: nunca zerar. Cada item: o que fazer, por que está bloqueado, o que destrava.
Feitos vão para o fim, com data. 🔴 urgente · 🟡 importante · 🟢 quando der.

## Abertos

- 🟡 **Conferir em share.streamlit.io qual branch o app de produção serve, e a URL.** Os docs dizem `main`, mas
  ninguém conferiu no painel (pede o login do Rodrigo). Destrava: o passe da D-C23 (recriar apps sabendo o que existe)
  e o teste de geração no ar.
- 🟡 **Secrets do app no Streamlit Cloud + teste no ar.** Deixar só as chaves gratuitas (nomes em
  `.streamlit/secrets.toml.example`), sem `LLM_BASE_URL`/`LLM_MODEL` (a nuvem não alcança a intranet; se ficarem,
  cada chamada pode perder até 5 s a cada 5 min), clicar **Reboot app** e gerar um diagrama. Por quê: a `main` com o
  `llm_cadeia` (`0b5aee1`) está publicada desde 28/09 e **nenhuma geração no Cloud foi verificada**.
- 🟢 **Chave OpenAI para verificar ao vivo** a repetição com `max_completion_tokens` (modelos de raciocínio via
  "Usar minha própria chave" › Outro). Hoje só há teste com dublê. Destrava: tirar o ⚠ do README do `llm_cadeia`
  (pedido vai para a sessão do framework, D-C24).

## Feitos

- 2026-09-29 · Credencial do git.camara renovada: `feat/llm-cadeia` igual no `origin` e no `github` (`f5a08e8`,
  conferido com `git ls-remote`). Se voltar a falhar: `LESSONS.md` 28/09.
- 2026-09-29 · Autorizou o snapshot de memória do checkpoint (`pptx_state_2026-09-29.md`).
- 2026-09-28 · Criou `~/.streamlit/secrets.toml` (fora do repo) com as chaves e o Gemma local.
- 2026-09-28 · Autorizou merge de `feat/llm-cadeia` em `main` (D4) e a integração da branch no buscador.
