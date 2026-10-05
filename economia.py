"""Etapas do trabalho manual que o app poupa, para o tempo_economizado (nuati-framework).

Mesmos tempos da conta antiga do app.py (até 05/10/2026, em horas por componente): cada custo fixo
vira uma etapa de 1 vez e cada termo linear, uma etapa por tipo de elemento. A tradução é a do teste
test_modelo_scopediagram_da_o_mesmo_numero_do_original do tempo_economizado; tests/test_economia.py
confere que o número não mudou.
"""

from __future__ import annotations

from schema import GlobalElements, ScopeDiagram
from tempo_economizado import Etapa

_H = 60  # a conta antiga era em horas; as etapas são em minutos


def etapas_manuais(scope: ScopeDiagram) -> list[Etapa]:
    g = scope.global_elements or GlobalElements()
    entradas, saidas = len(g.inputs), len(g.outputs)
    reguladores, recursos = len(g.regulators), len(g.resources)
    subprocessos = len(scope.subprocesses)
    atividades = sum(len(s.activities) for s in scope.subprocesses)
    return [
        Etapa("Ler e triar o texto-base", 1, 0.6 * _H, "vez"),
        Etapa("Extrair cada entrada, saída, regulador e recurso", entradas + saidas + reguladores + recursos,
              0.06 * _H, "elemento"),
        Etapa("Organizar os componentes do processo", 1, 0.8 * _H, "vez"),
        Etapa("Estruturar cada subprocesso", subprocessos, 0.35 * _H, "subprocesso"),
        Etapa("Estruturar cada atividade", atividades, 0.08 * _H, "atividade"),
        Etapa("Montar o desenho do diagrama", 1, 0.9 * _H, "vez"),
        Etapa("Desenhar cada subprocesso no diagrama", subprocessos, 0.3 * _H, "subprocesso"),
        Etapa("Desenhar cada entrada e saída no diagrama", entradas + saidas, 0.05 * _H,
              "entrada/saída", "entradas/saídas"),
        Etapa("Criar o PowerPoint", 1, 0.7 * _H, "vez"),
        Etapa("Formatar cada subprocesso no PowerPoint", subprocessos, 0.2 * _H, "subprocesso"),
        Etapa("Revisão final", 1, 0.4 * _H, "vez"),
        Etapa("Revisar cada regulador e recurso", reguladores + recursos, 0.03 * _H,
              "regulador/recurso", "reguladores/recursos"),
    ]
