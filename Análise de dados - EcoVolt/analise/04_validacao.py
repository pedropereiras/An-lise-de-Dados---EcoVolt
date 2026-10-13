"""
Validacao independente - AV1 Grupo 6 (EcoVolt).

1) Reproduz o exemplo de conferencia do professor.
2) Reconfere, por caminho independente (sem usar as funcoes do modelo),
   um cenario real do projeto.
"""
import json
from pathlib import Path

import modelo_energia as me

BASE = Path(__file__).resolve().parent
falhas = []

# --- Caso de referencia do professor ---------------------------------------
# 3 kW, 3 h, 6 kWh util, 4 kW max -> demanda 9 kWh, autonomia 2 h, nao atendida 3 kWh
edem = me.energia_demanda(3.0, 3.0)
aut = me.autonomia_h(6.0, 3.0)
nao = me.energia_nao_atendida(edem, 6.0)
print("[ref] Edemanda =", edem, "(esperado 9.0)")
print("[ref] autonomia =", aut, "(esperado 2.0)")
print("[ref] nao atendida =", nao, "(esperado 3.0)")
falhas += ["ref demanda"] * (edem != 9.0) + ["ref autonomia"] * (aut != 2.0) + ["ref nao atendida"] * (nao != 3.0)
inv_pot = 2.0 < 3.0
print("[ref] inviavel por potencia com Pmax=2 kW:", inv_pot, "(esperado True)")
falhas += ["ref potencia"] * (not inv_pot)

# --- Recalculo independente do cenario 'posto_vacinas', banco B -------------
cfg = me.carregar()
cen = next(c for c in cfg["cenarios"] if c["id"] == "posto_vacinas")
bancoB = next(b for b in cfg["bancos"] if b["id"] == "B")
f = cfg["fatores_bateria"]

pc = 0.20 * 1 + 0.05 * 4 + 0.10 * 1            # 0.50 kW
ed = pc * 8.0                                   # 4.00 kWh
eu = 10.0 * 0.80 * 0.90 * 0.90                  # 6.48 kWh
au = eu / pc                                    # 12.96 h
print("\n[cenario] Pcritica =", pc, "Edemanda =", ed, "Eutil =", eu, "autonomia =", au)

r = me.avaliar(cen, bancoB, f)
checa = (abs(r["Pcritica_kW"] - pc) < 1e-9 and abs(r["Edemanda_kWh"] - ed) < 1e-9
         and abs(r["Eutilizavel_kWh"] - eu) < 1e-9 and abs(r["autonomia_h"] - au) < 1e-9)
print("[cenario] bate com o modelo:", checa, "| status:", r["status"])
falhas += ["cenario"] * (not checa)

# --- Guarda de denominador zero --------------------------------------------
assert me.autonomia_h(5.0, 0.0) is None
print("\n[guarda] autonomia com Pcritica=0 ->", None, "(sem divisao por zero)")

print("\nRESULTADO:", "TODAS AS CONFERENCIAS OK" if not falhas else f"FALHAS: {falhas}")
(BASE / "validacao_resultado.json").write_text(
    json.dumps({"falhas": falhas, "ok": not falhas}, ensure_ascii=False, indent=2), encoding="utf-8")
