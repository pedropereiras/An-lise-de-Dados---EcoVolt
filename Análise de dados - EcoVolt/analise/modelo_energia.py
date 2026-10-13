"""
Modelo de continuidade energetica - AV1 Grupo 6 (EcoVolt).

Formulas (guia do professor):
  Pcritica      = soma(potencia * quantidade simultanea)
  Edemanda      = Pcritica * duracao
  Eutilizavel   = Enominal * fator_capacidade * fracao_uso * eficiencia
  autonomia     = Eutilizavel / Pcritica        (indefinida se Pcritica == 0)
  Enao_atendida = max(0, Edemanda - Eutilizavel)
  inviavel por potencia se Pmax < Pcritica
"""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def carga_pcritica(cargas: list[dict]) -> float:
    """Pcritica = soma(potencia * quantidade simultanea)."""
    return float(sum(c["potencia_kW"] * c["qtd"] for c in cargas))


def energia_demanda(pcritica: float, duracao_h: float) -> float:
    """Edemanda = Pcritica * duracao."""
    return pcritica * duracao_h


def energia_utilizavel(
    enominal_kwh: float, fator_capacidade: float, fracao_uso: float, eficiencia: float
) -> float:
    """Eutilizavel = Enominal * fator_capacidade * fracao_uso * eficiencia."""
    return enominal_kwh * fator_capacidade * fracao_uso * eficiencia


def autonomia_h(eutilizavel_kwh: float, pcritica_kw: float) -> float | None:
    """autonomia = Eutilizavel / Pcritica. Guarda para denominador zero."""
    if pcritica_kw == 0:
        return None
    return eutilizavel_kwh / pcritica_kw


def energia_nao_atendida(edemanda_kwh: float, eutilizavel_kwh: float) -> float:
    """Enao_atendida = max(0, Edemanda - Eutilizavel)."""
    return max(0.0, edemanda_kwh - eutilizavel_kwh)


def avaliar(cenario: dict, banco: dict, fatores: dict) -> dict:
    """Avalia um cenario para um banco. Trata casos vazio e inviavel por potencia."""
    pcritica = carga_pcritica(cenario["cargas"])
    edemanda = energia_demanda(pcritica, cenario["duracao_h"])
    eutil = energia_utilizavel(
        banco["Enominal_kWh"],
        fatores["fator_capacidade"]["valor"],
        fatores["fracao_uso"]["valor"],
        fatores["eficiencia"]["valor"],
    )
    aut = autonomia_h(eutil, pcritica)
    nao_atendida = energia_nao_atendida(edemanda, eutil)
    inviavel_pot = banco["Pmax_kW"] < pcritica

    if pcritica == 0:
        status, motivo = "sem_carga", "Pcritica = 0: nao ha carga critica. Divisao de autonomia evitada."
    elif inviavel_pot:
        status, motivo = "inviavel_potencia", "Pmax do banco < Pcritica: insuficiencia de potencia."
    elif aut is not None and aut >= cenario["duracao_h"]:
        status, motivo = "atende", "Autonomia >= duracao requerida e potencia suficiente."
    else:
        status, motivo = "nao_atende", "Autonomia < duracao requerida: faltam kWh."

    return {
        "cenario": cenario["id"],
        "cenario_nome": cenario["nome"],
        "banco": banco["id"],
        "banco_nome": banco["nome"],
        "duracao_h": cenario["duracao_h"],
        "cargas": cenario["cargas"],
        "Pcritica_kW": round(pcritica, 4),
        "Pmax_kW": banco["Pmax_kW"],
        "Edemanda_kWh": round(edemanda, 4),
        "Eutilizavel_kWh": round(eutil, 4),
        "autonomia_h": None if aut is None else round(aut, 4),
        "Enao_atendida_kWh": round(nao_atendida, 4),
        "status": status,
        "motivo": motivo,
    }


def carregar() -> dict:
    return json.loads((BASE / "cenarios.json").read_text(encoding="utf-8"))


def avaliar_tudo() -> list[dict]:
    cfg = carregar()
    resultados = []
    for banco in cfg["bancos"]:
        for cenario in cfg["cenarios"]:
            resultados.append(avaliar(cenario, banco, cfg["fatores_bateria"]))
    return resultados


if __name__ == "__main__":
    for r in avaliar_tudo():
        print(
            f"{r['cenario_nome']:<38} | banco {r['banco']} | P={r['Pcritica_kW']:.2f}kW "
            f"Ed={r['Edemanda_kWh']:.2f} Eu={r['Eutilizavel_kWh']:.2f} "
            f"aut={r['autonomia_h']} naoAt={r['Enao_atendida_kWh']:.2f} -> {r['status']}"
        )
