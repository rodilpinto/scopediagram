"""Extração IGOE real pela cadeia de LLM, pelo mesmo caminho do app (llm.extract_scope), e geração do PPTX.

Uso, da raiz do repo (gasta 1 chamada de LLM):
    py -3.13 tools/qa_extracao_real.py <saida.pptx>
Lê as chaves de ~/.streamlit/secrets.toml (no PC do trabalho: %USERPROFILE%/.streamlit/secrets.toml) DENTRO do
processo e nunca as imprime. Imprime quem respondeu,
o tempo, o nome do processo e o número de subprocessos. Em 05/10/2026, no PC do trabalho: local (google/gemma-4),
72 s, 3 subprocessos. Para forçar um provedor, ponha LLM_SOMENTE no ambiente antes (ex.: LLM_SOMENTE=gemini).
"""
import os
import sys
import time
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

TEXTO = """Processo: Liquidar nota fiscal de contrato. Objetivo: pagar o fornecedor pelo serviço prestado,
conforme o contrato. Começa quando o fornecedor entrega a nota fiscal e termina com a ordem bancária emitida.
O fiscal do contrato recebe a nota fiscal, confere o serviço prestado e atesta a nota. Depois a área financeira
confere certidões de regularidade fiscal, calcula as retenções de tributos e registra a liquidação no SIAFI.
Por fim, o ordenador de despesa autoriza o pagamento e a ordem bancária é emitida.
Regras: Lei 14.133/2021, Lei 4.320/1964 e IN RFB 1.234/2012. Recursos: SIAFI, sistema de contratos, equipe financeira.
Entradas: nota fiscal, contrato, relatório de fiscalização. Saídas: nota atestada, liquidação registrada, ordem bancária."""

if __name__ == "__main__":
    with open(os.path.expanduser("~/.streamlit/secrets.toml"), "rb") as fh:
        for chave, valor in tomllib.load(fh).items():
            if isinstance(valor, str) and valor:
                os.environ.setdefault(chave, valor)
    from llm import extract_scope
    from ppt import generate_ppt_bytes

    inicio = time.time()
    scope, origem = extract_scope(TEXTO)
    print(f"origem: {origem} | {time.time() - inicio:.1f}s | processo: {scope.process.name!r} | "
          f"subprocessos: {len(scope.subprocesses)}")
    saida = Path(sys.argv[1])
    saida.write_bytes(generate_ppt_bytes(scope))
    print("pptx:", saida.name, saida.stat().st_size, "bytes")
