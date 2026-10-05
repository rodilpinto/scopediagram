# BLOCKED-ON-RODRIGO: ações que só o Rodrigo pode fazer (scopediagram)

Ledger acumulativo entre sessões: nunca zerar. Cada item: o que fazer, por que está bloqueado, o que destrava.
Feitos vão para o fim, com data. 🔴 urgente · 🟡 importante · 🟢 quando der.

## Abertos

- 🔴 **D6: URL do app de produção do scopediagram, branch que ele segue e se há app de teste.** A resposta de 05/10
  veio com a do DOU-clipping. Destrava: o passo do Streamlit abaixo, com os endereços certos.
- 🔴 **Passo do Streamlit do passe do framework** (receita §3, passo 5, do `nuati-framework`), depois da D6:
  1. no app de produção, copiar o texto dos Secrets (guardar fora do navegador);
  2. apagar o app de produção e recriá-lo com a **mesma URL** na branch `main` (se não aparecer na lista, digitar);
     colar os Secrets e clicar **Reboot app**;
  3. criar o app de homologação (sugestão: `<url-de-produção>-homologacao`) na branch `homologacao`; colar os mesmos
     Secrets e **Reboot app**;
  4. avisar a sessão para a conferência no ar. Apps de teste antigos só são apagados depois do ok com os dois no ar.
- 🟢 **Chave OpenAI para verificar ao vivo** a repetição com `max_completion_tokens` (modelos de raciocínio via
  "Usar minha própria chave" › Outro). Hoje só há teste com dublê. Destrava: tirar o ⚠ do README do `llm_cadeia`
  (pedido vai para a sessão do framework, D-C24).

## Feitos

- 2026-10-05 · Decidiu o passe do framework (D5): mapeamento de branches, rodapé só com a marca, sem
  `extracao_texto`, dado interno fora dos arquivos versionados. As 2 pendências antigas de Cloud (conferir a branch;
  Secrets + teste no ar) viraram a D6 e o passo do Streamlit acima.
- 2026-09-29 · Credencial do remoto interno renovada: `feat/llm-cadeia` igual no `origin` e no `github` (`f5a08e8`,
  conferido com `git ls-remote`). Se voltar a falhar: `LESSONS.md` 28/09.
- 2026-09-29 · Autorizou o snapshot de memória do checkpoint (`pptx_state_2026-09-29.md`).
- 2026-09-28 · Criou `~/.streamlit/secrets.toml` (fora do repo) com as chaves e o Gemma local.
- 2026-09-28 · Autorizou merge de `feat/llm-cadeia` em `main` (D4) e a integração da branch no buscador.
