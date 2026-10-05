# pptx_opc: mexer em .pptx por dentro e conferir no PowerPoint de verdade (pasta copiável)

**Versão 1.0.0** · **Origem:** `github.com/rodilpinto/nuati-framework` (privado), pasta `pptx_opc/`.
Histórico: [`CHANGELOG.md`](CHANGELOG.md). Regras de cópia e registro de onde há cópias: README da raiz do framework.

Duas peças que vieram do `scopediagram` (gerador de diagramas de escopo em PowerPoint):

| Peça | Para quê |
|---|---|
| `opc.py` · `Package` | abrir o `.pptx` como pacote de partes XML (zip + lxml) e **apagar, clonar e reordenar slides**, levando junto as partes próprias do slide (diagramas SmartArt em `ppt/diagrams/`, notas). O `python-pptx` não alcança o SmartArt; esta camada sim |
| `render_powerpoint.py` · `render()` | exportar cada slide para PNG **com o PowerPoint instalado** (COM, `pywin32`). É a fonte de verdade para QA visual: o render do LibreOffice já divergiu do PowerPoint em casos reais (scopediagram) |

## Usar

```python
from pptx_opc import Package

pkg = Package(open("modelo.pptx", "rb").read())     # ou Package.open("modelo.pptx")
modelo = pkg.slide_names()[1]
novos = [pkg.clone_slide(modelo) for _ in range(3)]  # cada clone ganha cópia própria do SmartArt
pkg.delete_slide(modelo)
pkg.reorder([pkg.slide_names()[0], *novos])
dados = pkg.to_bytes()                               # ou pkg.save("saida.pptx")
```

Detalhes de `clone_slide`: o slide novo vai para o fim; partes de `ppt/diagrams/` ganham número novo; notas não vão
para o clone (evita órfãos); layout e tema continuam compartilhados. `delete_slide` remove o slide, as partes
próprias, as relações e os *content types*.

```bash
python -m pptx_opc.render_powerpoint saida.pptx pasta_png    # imprime o caminho de cada PNG (slide01.png, ...)
```

Só Windows com PowerPoint. Abre o PowerPoint visível (o COM do PowerPoint não roda totalmente oculto), exporta em
1920×1080 e fecha. ⚠ O texto de uso dentro do arquivo ainda diz `tools/render_pptx_powerpoint.py` (caminho no
scopediagram): o arquivo veio sem mudança.

## Adotar num app

1. **Copie a pasta inteira** `pptx_opc/` para a raiz do app, sem editar nada, e registre a cópia no README da raiz
   do framework ("Registro de cópias").
2. **Dependências:** `lxml` (para `opc.py`); `pywin32` só na máquina que faz QA visual (não no `requirements.txt` do
   Streamlit Cloud, que é Linux). Para os testes: `python-pptx`.
3. No scopediagram: `from templatefill.opc import Package` vira `from pptx_opc import Package`;
   `tools/render_pptx_powerpoint.py` vira `python -m pptx_opc.render_powerpoint`.
4. Rode, da pasta que contém `pptx_opc/`: `python -m pytest pptx_opc -q`. O teste do render abre o PowerPoint e só
   roda com `NUATI_TESTE_POWERPOINT=1`. Nele o pytest imprime "Windows fatal exception: code 0x800706be" (chamada RPC
   falhou ao fechar o PowerPoint): não é falha, o teste passa e os PNGs saem (visto em 30/09).

## Regra de sincronia

**Não edite uma cópia.** Melhoria nasce no framework, sobe `__version__`, entra no `CHANGELOG.md` e é recopiada.
