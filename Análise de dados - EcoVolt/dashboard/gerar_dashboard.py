"""Gera dashboard estatico (HTML unico) - AV1 Grupo 6 (EcoVolt)."""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\pedro\OneDrive\Desktop\av1-grupo-6-ecovolt")
DADOS = json.loads((ROOT / "analise" / "resultados.json").read_text(encoding="utf-8"))

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>EcoVolt - Continuidade energetica (AV1 Grupo 6)</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  :root{--verde:#0B6E4F;--ambar:#E1A100;--ruim:#C0392B;--cinza:#8A8F98;--fundo:#F6F8F7;--card:#fff;--txt:#1E2A24;}
  *{box-sizing:border-box}
  body{margin:0;font-family:"Segoe UI",Roboto,Arial,sans-serif;background:var(--fundo);color:var(--txt)}
  header{background:linear-gradient(120deg,#0B6E4F,#0a5a41);color:#fff;padding:22px 28px}
  header h1{margin:0;font-size:22px}
  header p{margin:6px 0 0;opacity:.9;font-size:14px}
  .wrap{max-width:1180px;margin:0 auto;padding:18px 20px 40px}
  .chips{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}
  .chip{border:1px solid #cfd8d3;background:#fff;border-radius:999px;padding:8px 14px;cursor:pointer;font-size:13px}
  .chip.active{background:var(--verde);color:#fff;border-color:var(--verde)}
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:14px}
  .kpi{background:var(--card);border:1px solid #e3e8e5;border-radius:12px;padding:12px 14px}
  .kpi .l{font-size:11px;color:var(--cinza);text-transform:uppercase;letter-spacing:.4px}
  .kpi .v{font-size:20px;font-weight:700;margin-top:4px}
  .badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;color:#fff}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .card{background:var(--card);border:1px solid #e3e8e5;border-radius:12px;padding:8px 10px}
  .card.full{grid-column:1 / -1}
  .card h3{margin:8px 10px 0;font-size:15px}
  .card h3 small{display:block;font-weight:400;color:var(--cinza);font-size:12px;margin-top:2px}
  footer{max-width:1180px;margin:0 auto;padding:0 20px 30px;color:#666;font-size:12px}
  @media(max-width:860px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<header>
  <h1>EcoVolt - Banco de 2a vida atende as cargas criticas?</h1>
  <p>Decisao: <i>nas condicoes informadas, o cenario atende as cargas criticas durante o tempo requerido?</i> &middot; AV1 Grupo 6</p>
</header>
<div class="wrap">
  <div class="chips" id="chips"></div>
  <div class="kpis" id="kpis"></div>
  <div class="grid">
    <div class="card full"><h3>V1. Composicao da carga critica<small>Onde esta o consumo que decide o caso</small></h3><div id="v1"></div></div>
    <div class="card"><h3>V2. Autonomia ofertada vs requerida<small>Compara 2 alternativas de banco</small></h3><div id="v2"></div></div>
    <div class="card"><h3>V3. Sensibilidade ao SOH<small>Quao robusta e a decisao</small></h3><div id="v3"></div></div>
  </div>
</div>
<footer id="rodape"></footer>
<script>
const DATA = __DATA__;
const COR = {A:"#E1A100",B:"#0B6E4F",ruim:"#C0392B",cinza:"#8A8F98"};
const LAYOUT = {template:"plotly_white",margin:{l:60,r:16,t:10,b:44},height:330,legend:{orientation:"h",y:1.15,x:0}};
const RODAPE = "Fonte: cenarios sinteticos declarados (analise/cenarios.json) | Banco: dados/processados/calce_cs2_soh.csv (SOH de 2a vida) | Grupo 6 - EcoVolt";
document.getElementById("rodape").textContent = RODAPE;

const cen = DATA.cenarios, bancos = {};
DATA.bancos.forEach(b=>bancos[b.id]=b);
function res(cid,bid){return DATA.resultados.find(r=>r.cenario===cid&&r.banco===bid);}
function statusCor(s){return s==="atende"?"#0B6E4F":(s==="nao_atende"?"#C0392B":(s==="inviavel_potencia"?"#8A6D00":"#8A8F98"));}
function statusTxt(s){return {atende:"ATENDE",nao_atende:"NAO ATENDE",inviavel_potencia:"INVIAVEL POR POTENCIA",sem_carga:"SEM CARGA CRITICA"}[s];}

function renderChips(sel){
  const el=document.getElementById("chips"); el.innerHTML="";
  cen.forEach(c=>{
    const d=document.createElement("div"); d.className="chip"+(c.id===sel?" active":""); d.textContent=c.nome;
    d.onclick=()=>select(c.id); el.appendChild(d);
  });
}
function kpi(label,val,extra){return `<div class="kpi"><div class="l">${label}</div><div class="v">${val}</div>${extra||""}</div>`;}

function render(sel){
  renderChips(sel);
  const c=cen.find(x=>x.id===sel);
  const rA=res(sel,"A"), rB=res(sel,"B");
  const st=(rB.status==="atende")?"atende":rB.status;
  const k=document.getElementById("kpis"); k.innerHTML="";
  k.innerHTML += kpi("P critica", rA.Pcritica_kW.toFixed(2)+" kW");
  k.innerHTML += kpi("Duracao requerida", c.duracao_h.toFixed(0)+" h");
  k.innerHTML += kpi("E demanda", rA.Edemanda_kWh.toFixed(2)+" kWh");
  k.innerHTML += kpi("E utilizavel (A / B)", rA.Eutilizavel_kWh.toFixed(2)+" / "+rB.Eutilizavel_kWh.toFixed(2)+" kWh");
  k.innerHTML += kpi("Autonomia (A / B)", (rA.autonomia_h==null?"n/d":rA.autonomia_h.toFixed(1)+" h")+" / "+(rB.autonomia_h==null?"n/d":rB.autonomia_h.toFixed(1)+" h"));
  k.innerHTML += kpi("E nao atendida (A / B)", rA.Enao_atendida_kWh.toFixed(2)+" / "+rB.Enao_atendida_kWh.toFixed(2)+" kWh");
  k.innerHTML += kpi("Decisao (Banco B)", `<span class="badge" style="background:${statusCor(st)}">${statusTxt(st)}</span>`, `<div style="font-size:11px;color:#666;margin-top:6px">${rB.motivo}</div>`);

  const cargas=(c.cargas||[]).slice().reverse();
  Plotly.react("v1",[{type:"bar",orientation:"h",x:cargas.map(e=>e.potencia_kW*e.qtd),y:cargas.map(e=>e.equipamento),
    marker:{color:"#0B6E4F"},text:cargas.map(e=>(e.potencia_kW*e.qtd).toFixed(2)+" kW"),textposition:"outside"}],
    Object.assign({},LAYOUT,{xaxis:{title:"Potencia simultanea (kW)",rangemode:"tozero"},yaxis:{automargin:true}}),{displayModeBar:false});

  Plotly.react("v2",[
    {type:"bar",name:"Banco A ("+bancos.A.Enominal_kWh+" kWh)",x:["Autonomia A"],y:[rA.autonomia_h||0],marker:{color:COR.A},text:[rA.autonomia_h==null?"n/d":rA.autonomia_h.toFixed(1)+" h"],textposition:"outside"},
    {type:"bar",name:"Banco B ("+bancos.B.Enominal_kWh+" kWh)",x:["Autonomia B"],y:[rB.autonomia_h||0],marker:{color:COR.B},text:[rB.autonomia_h==null?"n/d":rB.autonomia_h.toFixed(1)+" h"],textposition:"outside"}
  ],Object.assign({},LAYOUT,{shapes:[{type:"line",xref:"paper",x0:0,x1:1,y0:c.duracao_h,y1:c.duracao_h,line:{dash:"dot",color:"#333",width:2}}],
    annotations:[{xref:"paper",x:1,y:c.duracao_h,text:"requerido "+c.duracao_h.toFixed(0)+" h",showarrow:false,yanchor:"bottom"}],
    yaxis:{title:"Autonomia (h)",rangemode:"tozero"},xaxis:{title:""}}),{displayModeBar:false});

  const s=DATA.sensibilidade[sel];
  if(!s){Plotly.react("v3",[],[],{annotations:[{text:"Sem carga critica: autonomia indefinida (P critica = 0).",showarrow:false,font:{size:13}}],xaxis:{visible:false},yaxis:{visible:false},height:330});return;}
  Plotly.react("v3",[
    {type:"scatter",mode:"lines+markers",name:"Banco A",x:s.fator,y:s.A,line:{color:COR.A,width:3}},
    {type:"scatter",mode:"lines+markers",name:"Banco B",x:s.fator,y:s.B,line:{color:COR.B,width:3}}
  ],Object.assign({},LAYOUT,{shapes:[{type:"line",xref:"paper",x0:0,x1:1,y0:c.duracao_h,y1:c.duracao_h,line:{dash:"dot",color:"#333",width:2}}],
    xaxis:{title:"Fator de capacidade remanescente (SOH)"},yaxis:{title:"Autonomia (h)",rangemode:"tozero"}}),{displayModeBar:false});
}
function select(id){render(id);}
render("telecom_erb");
</script>
</body>
</html>
"""

html = HTML.replace("__DATA__", json.dumps(DADOS, ensure_ascii=False))
out = ROOT / "dashboard" / "dashboard.html"
out.write_text(html, encoding="utf-8")
print("Dashboard gerado:", out, len(html), "bytes")
