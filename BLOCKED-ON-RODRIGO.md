# BLOCKED-ON-RODRIGO: ações que só o Rodrigo pode fazer (scopediagram)

Ledger acumulativo entre sessões: nunca zerar. Cada item: o que fazer, por que está bloqueado, o que destrava.
Feitos vão para o fim, com data. 🔴 urgente · 🟡 importante · 🟢 quando der.

## Abertos

- 🔴 **Confirmar a remoção de `feat/llm-cadeia`** (GitHub, interno e local). Está contida na `main`; nada se perde.
  Com o ok: `git push github --delete feat/llm-cadeia`, `git push origin --delete feat/llm-cadeia`,
  `git branch -d feat/llm-cadeia`; conferir com `git ls-remote`.
- 🟡 **Gitea interno: branch padrão `main`** (na tela do `diagrama-escopo`, se ainda não for).
- 🟡 **URL antiga `diagramadeescopo.streamlit.app` deixou de existir** (06/10): links já divulgados quebram. Avisar
  quem usa, ou criar um app nessa URL (Streamlit não redireciona).
- 🟡 **Existe app de teste antigo do scopediagram?** Se sim, o Rodrigo o apaga no share.streamlit.io quando quiser
  (os dois apps novos já estão conferidos no ar).
- 🟡 **O template `Diagramas de Escopo_Realizar Auditoria e subprocessos_2026_GSF.pptx` está público** no GitHub desde
  o 1º commit (`5babcb5`, 29/03). É o arquivo que o gerador preenche (`templatefill/builder.py`). Confirmar se o
  conteúdo dele pode ser público (achado do dogfood de 06/10; nada foi mudado).
- 🟢 **Chave OpenAI para verificar ao vivo** a repetição com `max_completion_tokens` (modelos de raciocínio via
  "Usar minha própria chave" › Outro). Hoje só há teste com dublê. Destrava: tirar o ⚠ do README do `llm_cadeia`
  (pedido vai para o `nuati-framework`).

## Feitos

- 2026-10-06 · Autorizou o snapshot de memória do checkpoint (`scopediagram_state_2026-10-06.md`) e a troca do nome da área
  (`pptx` → `scopediagram`).
- 2026-10-06 · Autorizou a promoção (`v1.1.0`) e pediu a versão do app no rodapé de todos os apps (D7, F-A14).
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
