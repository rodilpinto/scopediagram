# Changelog do pptx_opc

Versão atual em `__init__.py` (`__version__`).

## 1.0.0 (30/09/2026): entra no nuati-framework

Trazido **sem mudança** do `github.com/rodilpinto/scopediagram`, branch `feat/llm-cadeia` @ `9d52dc5`:

- `templatefill/opc.py` → `opc.py` (mesmo hash git: `b3032f9`);
- `tools/render_pptx_powerpoint.py` → `render_powerpoint.py` (mesmo hash git: `b0cfdf8`).

Novos: `__init__.py` (versão, exporta `Package`), `README.md`, este changelog e `test_pptx_opc.py` (9 testes sem rede,
com apresentações geradas em memória pelo python-pptx e uma parte de diagrama injetada; mais 1 teste do render que
abre o PowerPoint, opcional). ✅ O teste do render passou ao vivo em 30/09 no PC do trabalho.

Ficaram no scopediagram, por serem do domínio dele (📝 avaliação do Claude): `templatefill/igoe.py` e
`templatefill/builder.py` (preenchimento do modelo IGOE).
