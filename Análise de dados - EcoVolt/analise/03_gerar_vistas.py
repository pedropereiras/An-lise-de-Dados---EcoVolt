"""
Vistas do dashboard - AV1 Grupo 6 (EcoVolt).

Gera as 3 vistas raciocinadas exigidas e um dashboard estatico de 2 estados.
Cada figura declara a decisao, as unidades e o limiar de decisao (racionalizacao visual).
"""
import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import modelo_energia as me

ROOT = Path(r"C:\Users\pedro\OneDrive\Desktop\av1-grupo-6-ecovolt")
VISTAS = ROOT / "dashboard" / "vistas"
VISTAS.mkdir(parents=True, exist_ok=True)

CFG = me.carregar()
FATORES = CFG["fatores_bateria"]
BANCOS = {b["id"]: b for b in CFG["bancos"]}
CENARIOS = {c["id"]: c for c in CFG["cenarios"]}
RESULTADOS = me.avaliar_tudo()

COR = {"A": "#E1A100", "B": "#0B6E4F", "ruim": "#C0392B", "neutro": "#8A8F98", "limiar": "#333333"}
FONTE = "Fonte: cenarios sinteticos declarados (analise/cenarios.json) | Grupo 6 - EcoVolt"


def layout(fig, titulo, subtitulo, altura=560):
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b><br><sup>{subtitulo}</sup>", x=0.01, xanchor="left", font=dict(size=18)),
        template="plotly_white",
        height=altura,
        margin=dict(l=70, r=30, t=95, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        annotations=[
            dict(text=FONTE, xref="paper", yref="paper", x=0, y=-0.16, showarrow=False,
                 font=dict(size=10, color="#666"))
        ],
    )
    return fig


# ---------------------------------------------------------------------------
# V1 - Composicao da carga critica por cenario (small multiples)
# ---------------------------------------------------------------------------
def vista1() -> go.Figure:
    reais = [c for c in CFG["cenarios"] if c["cargas"]]
    fig = make_subplots(rows=1, cols=len(reais),
                        subplot_titles=[c["nome"] for c in reais],
                        horizontal_spacing=0.08)
    for i, c in enumerate(reais, start=1):
        cargas = list(reversed(c["cargas"]))
        labels = [x["equipamento"] for x in cargas]
        vals = [x["potencia_kW"] * x["qtd"] for x in cargas]
        pcrit = sum(vals)
        fig.add_trace(
            go.Bar(x=vals, y=labels, orientation="h",
                   marker_color=COR["B"], text=[f"{v:.2f} kW" for v in vals], textposition="outside",
                   hovertemplate="%{y}<br>Contribuicao: %{x:.2f} kW<extra></extra>", showlegend=False),
            row=1, col=i)
        xref = "x domain" if i == 1 else f"x{i} domain"
        fig.add_annotation(text=f"<b>Pcritica = {pcrit:.2f} kW</b><br>demanda em {c['duracao_h']:.0f} h = {pcrit*c['duracao_h']:.2f} kWh",
                           x=0.5, y=1.18, xref=xref, yref="y domain", showarrow=False,
                           font=dict(size=11, color=COR["B"]))
    fig.update_xaxes(title_text="Potencia simultanea (kW)", rangemode="tozero")
    layout(fig, "V1. Qual carga critica pesa na decisao?",
           "Contribuicao de cada equipamento para a Pcritica. Ordena o que priorizar/religar em cascata.",
           altura=620)
    fig.update_layout(title=dict(text="<b>V1. Qual carga critica pesa na decisao?</b><br><sup>Contribuicao de cada equipamento para a Pcritica (kW).</sup>", x=0.01))
    return fig


# ---------------------------------------------------------------------------
# V2 - Autonomia ofertada vs duracao requerida (compara 2 alternativas)
# ---------------------------------------------------------------------------
def vista2() -> go.Figure:
    reais = [c for c in CFG["cenarios"] if c["cargas"]]
    x = [c["nome"].split(" (")[0] for c in reais]
    fig = go.Figure()
    for bid in ["A", "B"]:
        auts = []
        for c in reais:
            r = next(r for r in RESULTADOS if r["cenario"] == c["id"] and r["banco"] == bid)
            auts.append(r["autonomia_h"])
        fig.add_trace(go.Bar(
            name=f"Banco {bid} - {BANCOS[bid]['nome']}", x=x, y=auts,
            marker_color=COR[bid], text=[f"{a:.1f} h" for a in auts], textposition="outside",
            hovertemplate="%{x}<br>Autonomia: %{y:.2f} h<extra></extra>"))
    req = [c["duracao_h"] for c in reais]
    fig.add_trace(go.Scatter(
        name="Duracao requerida", x=x, y=req, mode="markers+lines",
        marker=dict(symbol="line-ew", size=22, color=COR["limiar"], line=dict(width=3)),
        line=dict(dash="dot", color=COR["limiar"], width=2),
        hovertemplate="%{x}<br>Requerido: %{y:.2f} h<extra></extra>"))
    fig.update_yaxes(title_text="Autonomia (h) / Duracao requerida (h)", rangemode="tozero")
    layout(fig, "V2. O banco aguenta o tempo requerido?",
           "Compara 2 alternativas de banco. Barra abaixo da linha pontilhada = nao atende.")
    return fig


# ---------------------------------------------------------------------------
# V3 - Sensibilidade: e se o fator de capacidade (SOH) mudar?
# ---------------------------------------------------------------------------
def sensibilidade(cenario_id: str, fatores_np=None) -> dict:
    fatores_np = np.linspace(0.6, 1.0, 21) if fatores_np is None else np.asarray(fatores_np)
    c = CENARIOS[cenario_id]
    out = {"fator": fatores_np.tolist(), "A": [], "B": []}
    for f in fatores_np:
        for bid in ["A", "B"]:
            eutil = me.energia_utilizavel(
                BANCOS[bid]["Enominal_kWh"], float(f), FATORES["fracao_uso"]["valor"], FATORES["eficiencia"]["valor"])
            out[bid].append(me.autonomia_h(eutil, me.carga_pcritica(c["cargas"])))
    return out


def vista3() -> go.Figure:
    cid = "telecom_erb"
    c = CENARIOS[cid]
    s = sensibilidade(cid)
    fig = go.Figure()
    for bid in ["A", "B"]:
        fig.add_trace(go.Scatter(
            x=s["fator"], y=s[bid], mode="lines+markers", name=f"Banco {bid} - {BANCOS[bid]['nome']}",
            line=dict(color=COR[bid], width=3),
            hovertemplate="fator_capacidade=%{x:.2f}<br>Autonomia=%{y:.2f} h<extra></extra>"))
    fig.add_hline(y=c["duracao_h"], line=dict(dash="dot", color=COR["limiar"], width=2),
                  annotation_text=f"Duracao requerida = {c['duracao_h']:.0f} h",
                  annotation_position="top left")
    fig.add_vline(x=FATORES["fator_capacidade"]["valor"], line=dict(dash="dash", color=COR["neutro"]),
                  annotation_text="SOH adotado = 0,80", annotation_position="top right")
    fig.update_xaxes(title_text="Fator de capacidade remanescente (SOH) [adimensional]")
    fig.update_yaxes(title_text="Autonomia resultante (h)", rangemode="tozero")
    layout(fig, "V3. Quao sensivel e a decisao ao SOH?",
           f"Cenario: {c['nome']}. Mostra o SOH minimo em que a autonomia alcanca o tempo requerido.")
    return fig


# ---------------------------------------------------------------------------
# Exportacao estatica + dados para o dashboard
# ---------------------------------------------------------------------------
def main():
    v1, v2, v3 = vista1(), vista2(), vista3()
    for nome, fig in [("v1_carga_critica", v1), ("v2_autonomia", v2), ("v3_sensibilidade", v3)]:
        fig.write_html(VISTAS / f"{nome}.html", include_plotlyjs="cdn")
        fig.write_image(VISTAS / f"{nome}.png", width=1100, height=620, scale=2)

    dados = {
        "fatores": FATORES,
        "bancos": CFG["bancos"],
        "cenarios": CFG["cenarios"],
        "resultados": RESULTADOS,
        "sensibilidade": {c["id"]: sensibilidade(c["id"]) for c in CFG["cenarios"] if c["cargas"]},
    }
    (ROOT / "analise" / "resultados.json").write_text(
        json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Vistas geradas em", VISTAS)
    print("Resultados em analise/resultados.json")


if __name__ == "__main__":
    main()
