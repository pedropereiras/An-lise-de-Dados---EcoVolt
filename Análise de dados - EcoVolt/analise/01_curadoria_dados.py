"""
AV1 - Grupo 6 (EcoVolt) | Etapa: Dados e qualidade
Curadoria dos dados brutos -> datasets processados.

Regra de ouro: NENHUM arquivo em dados/raw e alterado. A limpeza gera
copias em dados/processados e registra tudo no relatorio de qualidade.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\pedro\OneDrive\Desktop\av1-grupo-6-ecovolt")
RAW = ROOT / "dados" / "raw"
PROC = ROOT / "dados" / "processados"
PROC.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


report = {"originais_sha256": {}, "datasets": {}}

# 1) Hash dos originais (rastreabilidade: fonte -> tratamento -> dado)
for p in sorted(RAW.iterdir()):
    if p.is_file():
        report["originais_sha256"][p.name] = sha256(p)

# ---------------------------------------------------------------------------
# 2) CALCE CS2 SOH  (o conteudo real esta no arquivo de nome trocado)
# ---------------------------------------------------------------------------
calce_raw = pd.read_csv(RAW / "ORIGINAL_nomeErrado_recarregados-emplacamentos.csv")
calce_raw.to_csv(PROC / "calce_cs2_soh.csv", index=False)

n0 = len(calce_raw)
dup_exatos = int(calce_raw.duplicated().sum())
dup_chave = int(calce_raw.duplicated(subset=["battery_id", "cycle_number"]).sum())
soh_acima_100 = int((calce_raw["SOH"] > 100).sum())
nulos = int(calce_raw.isna().sum().sum())

calce = calce_raw.copy()
calce = calce.drop_duplicates()
calce = calce.drop_duplicates(subset=["battery_id", "cycle_number"], keep="first")
calce["SOH_corrigido"] = calce["SOH"].clip(upper=100.0)
calce["soh_acima_100_flag"] = calce["SOH"] > 100
calce = calce.sort_values(["battery_id", "cycle_number"]).reset_index(drop=True)
calce.to_csv(PROC / "calce_cs2_soh_limpo.csv", index=False)

report["datasets"]["calce_cs2_soh"] = {
    "linhas_bruto": n0,
    "linhas_limpo": int(len(calce)),
    "duplicatas_exatas_removidas": dup_exatos,
    "duplicatas_chave_battery_ciclo_removidas": dup_chave,
    "valores_SOH_maior_100": soh_acima_100,
    "celulas_nulas": nulos,
    "baterias": sorted(calce["battery_id"].unique().tolist()),
    "C_rates": sorted(calce["C_rate"].unique().tolist()),
    "SOH_min": float(calce["SOH_corrigido"].min()),
    "SOH_max": float(calce["SOH_corrigido"].max()),
}

# ---------------------------------------------------------------------------
# 3) Curva de carga 5,596 Ah (xlsx original e csv derivado)
# ---------------------------------------------------------------------------
curva_xlsx = pd.read_excel(RAW / "ORIGINAL_5.596Ah_charge.xlsx")
curva_xlsx.columns = [str(c).strip() for c in curva_xlsx.columns]
curva_xlsx.to_csv(PROC / "curva_carga_5p596ah_xlsx.csv", index=False)

curva_csv = pd.read_csv(RAW / "ORIGINAL_5_596Ah_charge.csv")
curva_csv.columns = [str(c).strip() for c in curva_csv.columns]

report["datasets"]["curva_carga"] = {
    "xlsx_colunas": list(curva_xlsx.columns),
    "xlsx_linhas": int(len(curva_xlsx)),
    "csv_colunas": list(curva_csv.columns),
    "csv_linhas": int(len(curva_csv)),
    "csv_nulos": int(curva_csv.isna().sum().sum()),
    "SOC_min": float(curva_csv["SOC"].min()),
    "SOC_max": float(curva_csv["SOC"].max()),
    "V_min": float(curva_csv["Voltage(V)"].min()),
    "V_max": float(curva_csv["Voltage(V)"].max()),
    "I_min": float(curva_csv["Current(A)"].min()),
    "I_max": float(curva_csv["Current(A)"].max()),
}

# capacidade integrada (A*h) como evidencia do fator de capacidade
t = pd.to_datetime(curva_csv["Date_Time"])
dt_h = t.diff().dt.total_seconds().fillna(0) / 3600.0
ah = float((curva_csv["Current(A)"].abs() * dt_h).sum())
report["datasets"]["curva_carga"]["capacidade_integrada_Ah"] = round(ah, 4)

(ROOT / "analise" / "relatorio_qualidade.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
)

print(json.dumps(report, indent=2, ensure_ascii=False))
