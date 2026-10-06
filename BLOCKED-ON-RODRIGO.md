# BLOCKED-ON-RODRIGO: ações que só o Rodrigo pode fazer (scopediagram)

Ledger acumulativo entre sessões: nunca zerar. Cada item: o que fazer, por que está bloqueado, o que destrava.
Feitos vão para o fim, com data. 🔴 urgente · 🟡 importante · 🟢 quando der.

## Abertos

- 🔴 **Ok para promover `homologacao` → `main`** (passo 9), depois de ver os dois apps no ar (log 06/10). Junto:
  o nome da tag de versão do app e se o rodapé passa a mostrar essa versão.
- 🟡 **URL antiga `diagramadeescopo.streamlit.app` deixou de existir** (06/10): links já divulgados quebram. Avisar
  quem usa, ou criar um app nessa URL (Streamlit não redireciona).
- 🟡 **Existe app de teste antigo do scopediagram?** Se sim, apagar só depois do ok final.
- 🟢 **Chave OpenAI para verificar ao vivo** a repetição com `max_completion_tokens` (modelos de raciocínio via
  "Usar minha própria chave" › Outro). Hoje só há teste com dublê. Destrava: tirar o ⚠ do README do `llm_cadeia`
  (pedido vai para a sessão do framework, D-C24).

## Feitos

- 2026-10-06 · Recriou a produção (`diagrama-escopo`, `main`) e criou a homologação
  (`diagrama-escopo-homologacao`, `homologacao`), com os Secrets e Reboot.
- 2026-10-05 · Decidiu o passe do framework (D5): mapeamento de branches, rodapé só com a marca, sem
  `extracao_texto`, dado interno fora dos arquivos versionados. As 2 pendências antigas de Cloud (conferir a branch;
  Secrets + teste no ar) viraram a D6 e o passo do Streamlit acima.
- 2026-09-29 · Credencial do remoto interno renovada: `feat/llm-cadeia` igual no `origin` e no `github` (`f5a08e8`,
  conferido com `git ls-remote`). Se voltar a falhar: `LESSONS.md` 28/09.
- 2026-09-29 · Autorizou o snapshot de memória do checkpoint (`pptx_state_2026-09-29.md`).
- 2026-09-28 · Criou `~/.streamlit/secrets.toml` (fora do repo) com as chaves e o Gemma local.
- 2026-09-28 · Autorizou merge de `feat/llm-cadeia` em `main` (D4) e a integração da branch no buscador.
