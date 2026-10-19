library(shiny)
library(plotly)

# ----------------------------------------------------------------------------
# 1. DADOS (espelham analise/cenarios.json do repositório)
#    AVISO: parâmetros ilustrativos declarados pelo grupo, não medições reais.
# ----------------------------------------------------------------------------
PADRAO <- list(soh = 80, dod = 90, efi = 90)   # em %

bancos <- data.frame(
  id = c("A", "B"),
  nome = c("Banco 2ª vida conservador", "Banco 2ª vida expandido"),
  E = c(5, 10),   # energia nominal (kWh)
  P = c(1, 3),    # potência máxima (kW)
  stringsAsFactors = FALSE
)

mk <- function(eq, pot, qtd) {
  data.frame(equipamento = eq, potencia = pot, qtd = qtd, stringsAsFactors = FALSE)
}

cenarios <- list(
  posto_vacinas = list(
    nome = "Sala de vacinas (posto de saúde)", curto = "Sala de<br>vacinas", duracao = 8,
    cargas = mk(c("Refrigerador de vacinas", "Iluminação de emergência", "Terminal + impressora"),
                c(0.20, 0.05, 0.10), c(1, 4, 1))),
  telecom_erb = list(
    nome = "Estação rádio-base (telecom)", curto = "Rádio-base", duracao = 4,
    cargas = mk(c("Transmissor/rádio", "Ar-condicionado de emergência"),
                c(0.40, 0.80), c(1, 1))),
  residencia_essencial = list(
    nome = "Residência - circuito essencial", curto = "Residência<br>essencial", duracao = 6,
    cargas = mk(c("Geladeira", "Bomba d'água", "Iluminação", "Roteador/internet"),
                c(0.15, 0.50, 0.08, 0.02), c(1, 1, 3, 1))),
  sem_carga_critica = list(
    nome = "Caso vazio - sem cargas críticas", curto = "Sem cargas", duracao = 4,
    cargas = mk(character(0), numeric(0), numeric(0)))
)

# ----------------------------------------------------------------------------
# 2. MODELO
# ----------------------------------------------------------------------------
potencia_critica <- function(cen) sum(cen$cargas$potencia * cen$cargas$qtd)

avaliar <- function(cen, banco, soh, dod, efi) {
  pc  <- potencia_critica(cen)
  ed  <- pc * cen$duracao
  eu  <- banco$E * soh * dod * efi
  aut <- if (pc == 0) NA_real_ else eu / pc
  nao <- max(0, ed - eu)
  pot_ok   <- banco$P >= pc
  tempo_ok <- !is.na(aut) && aut >= cen$duracao
  status <- if (pc == 0) "sem_carga"
            else if (!pot_ok) "inviavel_potencia"
            else if (tempo_ok) "atende"
            else "nao_atende"
  list(pc = pc, ed = ed, eu = eu, aut = aut, nao = nao,
       pot_ok = pot_ok, tempo_ok = tempo_ok, status = status,
       pmax = banco$P, dur = cen$duracao)
}

# ----------------------------------------------------------------------------
# 3. APOIO VISUAL  (paleta Okabe-Ito; contraste sobre branco auditado)
#    azul 5,19:1 · vermelhão 3,87:1 (gráficos) / escuro 6,06:1 (texto) · cinza 3,25:1
# ----------------------------------------------------------------------------
AZUL      <- "#0072B2"   # atende
VERM      <- "#D55E00"   # não atende / limitação
VERM_TXT  <- "#A84300"   # versão escura para texto pequeno
CINZA     <- "#8A8F98"   # dado de contexto
CINZA_2   <- "#7B8390"   # linha do banco não selecionado
CINZA_TXT <- "#4B5563"
TINTA     <- "#111827"
FONTE     <- "Hanken Grotesk, Segoe UI, Roboto, Arial, sans-serif"

STATUS <- list(
  atende            = list(txt = "ATENDE",                 icone = "✔", cor = AZUL, cor_txt = AZUL),
  nao_atende        = list(txt = "NÃO ATENDE",             icone = "✖", cor = VERM, cor_txt = VERM_TXT),
  inviavel_potencia = list(txt = "INVIÁVEL POR POTÊNCIA",  icone = "⚠", cor = VERM, cor_txt = VERM_TXT),
  sem_carga         = list(txt = "SEM CARGA CRÍTICA",      icone = "–", cor = CINZA, cor_txt = CINZA_TXT)
)

fmt <- function(x, d = 2) formatC(x, format = "f", digits = d, decimal.mark = ",")
quebrar <- function(x, n) vapply(x, function(s) paste(strwrap(s, n), collapse = "<br>"), "")

msg_plot <- function(texto) {
  plot_ly(x = 0, y = 0, type = "scatter", mode = "markers", marker = list(opacity = 0),
          hoverinfo = "none") %>%
    layout(xaxis = list(visible = FALSE), yaxis = list(visible = FALSE),
           font = list(family = FONTE),
           annotations = list(list(text = texto, x = 0.5, y = 0.5, xref = "paper", yref = "paper",
                                   showarrow = FALSE, font = list(size = 13, color = CINZA_TXT)))) %>%
    config(displayModeBar = FALSE)
}

base_layout <- function(p, ...) {
  layout(p, font = list(family = FONTE, size = 12, color = TINTA),
         paper_bgcolor = "white", plot_bgcolor = "white", showlegend = FALSE,
         hoverlabel = list(font = list(family = FONTE, size = 12)), ...) %>%
    config(displayModeBar = FALSE)
}

# Barra "bullet": preenchimento = valor medido; traço preto = referência (mesma escala)
bullet <- function(valor, ref, cor) {
  mx <- max(valor, ref) * 1.08
  div(class = "bt",
      div(class = "bt-fill", style = sprintf("width:%.1f%%;background:%s", 100 * valor / mx, cor)),
      div(class = "bt-mark", style = sprintf("left:%.1f%%", 100 * ref / mx)))
}

# ----------------------------------------------------------------------------
# 4. INTERFACE
# ----------------------------------------------------------------------------
css <- sprintf("
html,body{min-height:100%%;margin:0}
body{background:#F3F5F7;color:%1$s;font-family:%2$s;font-size:14px;overflow-y:auto}
.app{display:flex;flex-direction:column;min-height:100vh}
.topo{background:#0B6F52;color:#fff;padding:15px 24px;display:flex;justify-content:space-between;
      align-items:center;flex-wrap:wrap;gap:10px 24px}
.topo h1{font-size:clamp(18px,1.55vw,23px);font-weight:800;margin:0;line-height:1.25}
.topo p{margin:0;font-size:12.5px;color:#E5F3ED;text-align:right;max-width:540px;line-height:1.4}
.corpo{display:grid;grid-template-columns:250px minmax(0,1fr);gap:14px;padding:14px 18px 8px;align-items:start}
.lateral{width:auto;min-width:0;background:#fff;border:1px solid #E5E7EB;border-radius:12px;
         padding:15px;overflow:visible;align-self:start}
.lateral h4{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:%3$s;margin:14px 0 7px;font-weight:800}
.lateral h4:first-child{margin-top:0}
.lateral .form-group{margin-bottom:10px}
.lateral label.control-label{font-size:12.5px;font-weight:650;margin-bottom:4px;line-height:1.3}
.lateral .radio{margin:8px 0 5px}
.lateral .radio label{font-size:13px;line-height:1.35}
.lateral .radio small{color:%3$s}
.lateral .form-control{border-color:#D1D5DB;border-radius:7px;min-height:38px}
.lateral .btn{width:100%%;margin-top:10px;font-size:12.5px;border-radius:7px}
.irs--shiny .irs-bar{background:#0B6F52;border-color:#0B6F52}
.irs--shiny .irs-handle{border-color:#0B6F52;background:#fff}
.irs--shiny .irs-single,.irs--shiny .irs-from,.irs--shiny .irs-to{background:#0B6F52}
.irs--shiny .irs-min,.irs--shiny .irs-max{background:transparent;color:%3$s}
.principal{min-width:0;display:flex;flex-direction:column;gap:12px}
.linha-kpi{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.linha-check{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.linha-graf{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;align-items:stretch}
.cartao{background:#fff;border:1px solid #E5E7EB;border-radius:12px;padding:13px 15px;
        display:flex;flex-direction:column;min-width:0;box-shadow:0 1px 2px rgba(17,24,39,.035)}
.kpi .rot{font-size:10.5px;text-transform:uppercase;letter-spacing:.055em;color:%3$s;font-weight:800;line-height:1.3}
.kpi .val{font-size:clamp(21px,1.8vw,29px);font-weight:800;line-height:1.18;margin-top:5px;overflow-wrap:anywhere}
.kpi .sub{font-size:11.5px;color:%3$s;line-height:1.4;margin-top:5px}
.hero{border-left:5px solid;padding-left:12px}
.hero .val{font-size:clamp(19px,1.6vw,26px);font-weight:850;line-height:1.2;margin-top:5px;overflow-wrap:anywhere}
.hero .sub{font-size:11.5px}
.ck-topo{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;flex-wrap:wrap}
.ck-tit{font-size:13px;font-weight:750;line-height:1.3}
.ck-ver{font-size:13px;font-weight:850;line-height:1.3;white-space:nowrap}
.bt{position:relative;height:14px;background:#E5E7EB;border-radius:4px;margin:13px 0 10px;overflow:visible}
.bt-fill{position:absolute;left:0;top:0;height:100%%;border-radius:4px}
.bt-mark{position:absolute;top:-5px;height:24px;width:3px;margin-left:-1.5px;background:%1$s;border-radius:1px}
.ck-leg{font-size:11.5px;color:%3$s;display:flex;gap:8px 16px;flex-wrap:wrap;align-items:center;line-height:1.4}
.sw{display:inline-block;width:10px;height:10px;border-radius:2px;vertical-align:-1px;margin-right:5px}
.sw.tr{width:3px;height:13px;border-radius:1px;background:%1$s;vertical-align:-3px}
.cartao h3{font-size:14.5px;font-weight:800;margin:0;line-height:1.35}
.cartao .sub{font-size:11.5px;color:%3$s;margin:6px 0 2px;line-height:1.4;min-height:46px}
.cartao .plot{position:relative;min-width:0;width:100%%;margin-top:2px}
.cartao .plot .html-widget{width:100%% !important;height:340px !important}
.rodape{font-size:10.5px;color:%3$s;padding:4px 22px 12px;line-height:1.5}
@media(max-width:1400px){
  .corpo{grid-template-columns:225px minmax(0,1fr);padding-left:12px;padding-right:12px}
  .linha-kpi{grid-template-columns:repeat(2,minmax(0,1fr))}
  .linha-graf{grid-template-columns:repeat(2,minmax(0,1fr))}
  .linha-graf .cartao:last-child{grid-column:1/-1}
  .cartao .plot .html-widget{height:330px !important}
}
@media(max-width:900px){
  .corpo{grid-template-columns:minmax(0,1fr)}
  .lateral{display:block}
  .linha-graf{grid-template-columns:minmax(0,1fr)}
  .linha-graf .cartao:last-child{grid-column:auto}
  .cartao .plot .html-widget{height:340px !important}
}
@media(max-width:560px){
  .topo{padding:14px 16px}
  .topo p{text-align:left}
  .corpo{padding:10px;gap:10px}
  .linha-kpi,.linha-check{grid-template-columns:minmax(0,1fr)}
  .cartao{padding:12px}
  .cartao .sub{min-height:0}
  .cartao .plot .html-widget{height:320px !important}
  .rodape{padding:4px 12px 12px}
}
", TINTA, FONTE, CINZA_TXT)

ui <- bootstrapPage(
  title = "EcoVolt - Dashboard",
  tags$head(
    tags$link(rel = "stylesheet",
              href = "https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700;800&display=swap"),
    tags$style(HTML(css))),
  div(class = "app",
    div(class = "topo",
        h1("EcoVolt Analytics · Continuidade energética com banco de 2ª vida"),
        p("O cenário atende às cargas críticas durante o tempo requerido de interrupção?")),
    div(class = "corpo",
      # ---- painel de controle ----
      div(class = "lateral",
          h4("Cenário"),
          selectInput("cenario", NULL,
                      choices = setNames(names(cenarios), sapply(cenarios, `[[`, "nome")),
                      selected = "telecom_erb", width = "100%"),
          h4("Banco de 2ª vida"),
          radioButtons("banco", NULL,
                       choiceNames = lapply(seq_len(nrow(bancos)), function(i)
                         HTML(sprintf("<b>Banco %s</b><br><small>%s kWh nominais · %s kW máx.</small>",
                                      bancos$id[i], fmt(bancos$E[i], 0), fmt(bancos$P[i], 0)))),
                       choiceValues = bancos$id, selected = "A"),
          h4("Premissas da bateria"),
          sliderInput("soh", "SOH (saúde da bateria)", 60, 100, PADRAO$soh, step = 1,
                      post = "%", ticks = FALSE),
          sliderInput("dod", "Fração de uso (descarga)", 50, 100, PADRAO$dod, step = 1,
                      post = "%", ticks = FALSE),
          sliderInput("efi", "Eficiência (inversor + bateria)", 70, 100, PADRAO$efi, step = 1,
                      post = "%", ticks = FALSE),
          actionButton("reset", "Restaurar premissas")
      ),
      # ---- área principal ----
      div(class = "principal",
          uiOutput("kpis"),
          uiOutput("checks"),
          div(class = "linha-graf",
              div(class = "cartao",
                  h3("Qual carga pesa na decisão?"), div(class = "sub", uiOutput("sub1")),
                  div(class = "plot", plotlyOutput("v1", height = "340px"))),
              div(class = "cartao",
                  h3("O banco aguenta o tempo requerido?"), div(class = "sub", uiOutput("sub2")),
                  div(class = "plot", plotlyOutput("v2", height = "340px"))),
              div(class = "cartao",
                  h3("Quão sensível é a decisão ao SOH?"), div(class = "sub", uiOutput("sub3")),
                  div(class = "plot", plotlyOutput("v3", height = "340px")))
          )
      )
    ),
    div(class = "rodape",
        HTML(paste0(
          "<b>Como calculamos:</b> potência crítica = soma da potência de cada equipamento × quantidade · ",
          "energia demandada = potência crítica × duração requerida · ",
          "energia utilizável = energia nominal × SOH × fração de uso × eficiência · ",
          "autonomia = energia utilizável ÷ potência crítica. ",
          "Parâmetros ilustrativos declarados pelo Grupo 6 (não há base operacional real de cargas críticas); ",
          "SOH de 2ª vida com referência no dataset CALCE CS2.")))
  )
)

# ----------------------------------------------------------------------------
# 5. SERVIDOR
# ----------------------------------------------------------------------------
server <- function(input, output, session) {

  observeEvent(input$reset, {
    updateSliderInput(session, "soh", value = PADRAO$soh)
    updateSliderInput(session, "dod", value = PADRAO$dod)
    updateSliderInput(session, "efi", value = PADRAO$efi)
  })

  cen   <- reactive(cenarios[[input$cenario]])
  banco <- reactive(bancos[bancos$id == input$banco, ])
  par   <- reactive(list(soh = input$soh / 100, dod = input$dod / 100, efi = input$efi / 100))
  res   <- reactive(avaliar(cen(), banco(), par()$soh, par()$dod, par()$efi))

  # ---- Indicadores principais ----
  output$kpis <- renderUI({
    r <- res(); b <- banco(); st <- STATUS[[r$status]]
    motivo <- switch(r$status,
      atende = "Potência suficiente e autonomia igual ou superior ao tempo requerido.",
      nao_atende = paste0("Energia insuficiente para o período: faltam ",
                          fmt(r$nao), " kWh para cobrir a energia demandada."),
      inviavel_potencia = paste0("Potência máxima do banco (", fmt(r$pmax), " kW) menor que a potência crítica (",
                                 fmt(r$pc), " kW)", if (r$nao > 0) paste0("; déficit de energia de ", fmt(r$nao), " kWh") else "", "."),
      sem_carga = "Este cenário não tem cargas críticas definidas.")
    kpi <- function(rot, val, sub) div(class = "cartao kpi",
                                      div(class = "rot", rot),
                                      div(class = "val", val),
                                      div(class = "sub", sub))
    div(class = "linha-kpi",
        kpi("Potência crítica", paste(fmt(r$pc), "kW"),
            paste0("Energia demandada: ", fmt(r$ed), " kWh em ", fmt(r$dur, 0), " h")),
        kpi("Energia disponível", paste(fmt(r$eu), "kWh"),
            paste0("Energia utilizável do Banco ", b$id, " · ", fmt(b$E, 1), " kWh nominais")),
        kpi("Autonomia", if (is.na(r$aut)) "—" else paste(fmt(r$aut), "h"),
            paste0("Tempo requerido: ", fmt(r$dur, 0), " h")),
        div(class = "cartao kpi hero", style = paste0("border-left-color:", st$cor),
            div(class = "rot", "Situação do cenário"),
            div(class = "val", style = paste0("color:", st$cor_txt), paste(st$icone, st$txt)),
            div(class = "sub", motivo)))
  })

  # ---- Verificações destacadas: tempo requerido e potência ----
  output$checks <- renderUI({
    r <- res()
    if (r$status == "sem_carga") {
      return(div(class = "linha-check", style = "grid-template-columns:1fr",
                 div(class = "cartao", style = "color:#4B5563",
                     "Sem cargas críticas neste cenário: não há tempo requerido nem potência a verificar.")))
    }
    c_tempo <- if (r$tempo_ok) AZUL else VERM
    c_pot   <- if (r$pot_ok) AZUL else VERM
    ver <- function(ok, t_ok, t_no, ic_no = "✖")
      span(class = "ck-ver", style = paste0("color:", if (ok) AZUL else VERM_TXT),
           if (ok) paste("✔", t_ok) else paste(ic_no, t_no))
    div(class = "linha-check",
        div(class = "cartao",
            div(class = "ck-topo", span(class = "ck-tit", "Tempo requerido de interrupção"),
                ver(r$tempo_ok, "Atendido", "Não atendido")),
            bullet(r$aut, r$dur, c_tempo),
            div(class = "ck-leg",
                span(span(class = "sw", style = paste0("background:", c_tempo)),
                     paste0("Autonomia: ", fmt(r$aut), " h")),
                span(span(class = "sw tr"), paste0("Tempo requerido: ", fmt(r$dur), " h")))),
        div(class = "cartao",
            div(class = "ck-topo", span(class = "ck-tit", "Limite de potência do banco"),
                ver(r$pot_ok, "Suficiente", "Limitação de potência", "⚠")),
            bullet(r$pc, r$pmax, c_pot),
            div(class = "ck-leg",
                span(span(class = "sw", style = paste0("background:", c_pot)),
                     paste0("Potência crítica: ", fmt(r$pc), " kW")),
                span(span(class = "sw tr"), paste0("Potência máxima do banco: ", fmt(r$pmax), " kW")))))
  })

  # ---- Subtítulos (pergunta + como ler) ----
  output$sub1 <- renderUI({
    b <- banco()
    HTML(paste0("Barras ordenadas por potência simultânea. A linha tracejada marca a potência máxima do Banco ",
                b$id, ". Valores à direita das barras; escala em kW a partir de zero."))
  })
  output$sub2 <- renderUI(HTML(paste0(
    "Azul + ✔ = atende; laranja + ✖ = autonomia insuficiente; laranja + ⚠ = potência insuficiente. ",
    "Faixa cinza = cenário selecionado; contorno escuro = combinação selecionada (cenário + banco). ",
    "Linha tracejada = tempo requerido; passe o cursor para detalhes.")))
  output$sub3 <- renderUI({
    cn <- cen(); p <- par()
    pc <- potencia_critica(cn)
    if (pc == 0) return(HTML("Sem cargas críticas neste cenário."))
    smin <- function(i) {
      bk <- bancos[i, ]
      if (bk$P < pc) return("limitado por potência")
      s <- cn$duracao * pc / (bk$E * p$dod * p$efi)
      if (s > 1) "inalcançável" else paste0(ceiling(s * 100), "%")
    }
    pot_limitados <- bancos$P < pc
    nota_potencia <- if (any(pot_limitados)) {
      paste0(
        " * Curva tracejada e marcada com asterisco = autonomia teórica para ",
        paste0("Banco ", bancos$id[pot_limitados], collapse = ", "),
        ", cuja potência máxima é inferior à potência crítica; esse banco não é operacionalmente viável neste cenário."
      )
    } else {
      ""
    }
    HTML(paste0("Curva escura e espessa = banco selecionado; cinza = outro banco. ",
                "Linha horizontal = tempo requerido; linha vertical = SOH atual. SOH mínimo: Banco A = <b>", smin(1),
                "</b> · Banco B = <b>", smin(2), "</b>.", nota_potencia))
  })

  # ---- V1: composição da potência crítica x potência máxima do banco ----
  output$v1 <- renderPlotly({
    cn <- cen(); b <- banco(); r <- res()
    if (nrow(cn$cargas) == 0) return(msg_plot("Sem cargas críticas neste cenário"))

    d <- cn$cargas
    d$kw <- d$potencia * d$qtd
    d <- d[order(-d$kw), ]
    nomes <- ifelse(d$qtd > 1, paste0(d$equipamento, " (", d$qtd, "×)"), d$equipamento)
    cats <- c("<b>Potência crítica (total)</b>", quebrar(nomes, 24))
    vals <- c(r$pc, d$kw)
    # Cinza mais escuro para manter contraste suficiente sobre o fundo branco.
    cores <- c(if (r$pot_ok) AZUL else VERM, rep(CINZA_2, nrow(d)))
    rot <- paste0(fmt(vals), " kW")
    rot[1] <- paste0(rot[1], if (r$pot_ok) " ✔" else " ⚠")
    xmax <- max(c(vals, b$P, 0.1)) * 1.28
    anot <- lapply(seq_along(vals), function(k) {
      list(x = vals[k], y = cats[k], xref = "x", yref = "y",
           xanchor = "left", xshift = 5, showarrow = FALSE,
           text = rot[k], bgcolor = "rgba(255,255,255,0.92)", borderpad = 1,
           font = list(size = 10, color = TINTA))
    })
    ancora_pmax <- if (b$P / xmax > 0.60) "right" else "left"
    anot_pmax <- list(
      x = b$P, y = 1.02, xref = "x", yref = "paper",
      xanchor = ancora_pmax, yanchor = "bottom",
      xshift = if (ancora_pmax == "right") -5 else 5,
      showarrow = FALSE,
      text = paste0("Potência máx. Banco ", b$id, ": ", fmt(b$P), " kW"),
      bgcolor = "rgba(255,255,255,0.94)", borderpad = 2,
      font = list(size = 10, color = TINTA)
    )

    plot_ly(x = vals, y = cats, type = "bar", orientation = "h",
            marker = list(color = cores, line = list(color = "white", width = 1)),
            hoverinfo = "text",
            hovertext = c(paste0("<b>Potência crítica total</b><br>", fmt(r$pc), " kW"),
                          paste0(nomes, ": ", fmt(d$kw), " kW"))) %>%
      base_layout(
        margin = list(l = 12, r = 18, t = 38, b = 48),
        bargap = 0.38,
        xaxis = list(range = c(0, xmax), title = list(text = "Potência (kW)", standoff = 8),
                     showticklabels = TRUE, showgrid = TRUE, gridcolor = "#E9EDF1",
                     zeroline = FALSE, ticks = "outside", ticklen = 3,
                     tickfont = list(size = 10, color = CINZA_TXT), fixedrange = TRUE),
        yaxis = list(autorange = "reversed", categoryorder = "array", categoryarray = cats,
                     automargin = TRUE, showgrid = FALSE, ticks = "",
                     tickfont = list(size = 10, color = TINTA), fixedrange = TRUE),
        shapes = list(list(type = "line", x0 = b$P, x1 = b$P, y0 = 0, y1 = 1, yref = "paper",
                           line = list(color = TINTA, dash = "dash", width = 2))),
        annotations = c(anot, list(anot_pmax)))
  })

  # ---- V2: autonomia x tempo requerido (2 bancos, 3 cenários) ----
  output$v2 <- renderPlotly({
    p <- par()
    reais <- cenarios[sapply(cenarios, function(cn) nrow(cn$cargas) > 0)]
    n <- length(reais)
    xs <- aut <- dur <- numeric()
    cor <- hov <- character()
    sinais <- character()
    lw <- numeric()
    shapes <- list()
    rotulos_banco <- character()
    grupo_rotulos <- character()

    for (i in seq_len(n)) {
      id <- names(reais)[i]
      cn <- reais[[i]]
      g0 <- 3 * (i - 1)
      grupo_rotulos <- c(grupo_rotulos, paste0(
        switch(id,
          posto_vacinas = "Sala de vacinas",
          telecom_erb = "Estação rádio-base",
          residencia_essencial = "Residência essencial",
          "Cenário"),
        "<br>", fmt(cn$duracao, 0), " h exigidas"))

      for (j in 1:2) {
        bk <- bancos[j, ]
        r <- avaliar(cn, bk, p$soh, p$dod, p$efi)
        st <- STATUS[[r$status]]
        xs <- c(xs, g0 + j - 1)
        aut <- c(aut, r$aut)
        dur <- c(dur, cn$duracao)
        cor <- c(cor, st$cor)
        sinais <- c(sinais, st$icone)
        rotulos_banco <- c(rotulos_banco, bk$id)
        hov <- c(hov, paste0("<b>Banco ", bk$id, " · ", cn$nome, "</b><br>Autonomia: ", fmt(r$aut),
                             " h<br>Tempo requerido: ", fmt(cn$duracao, 0), " h<br>Potência crítica: ",
                             fmt(r$pc), " kW<br>Situação: ", st$txt))
        lw <- c(lw, if (id == input$cenario && bk$id == input$banco) 2.5 else 0)
      }

      if (id == input$cenario) {
        shapes[[length(shapes) + 1]] <- list(type = "rect", x0 = g0 - 0.55, x1 = g0 + 1.55,
                                             y0 = 0, y1 = 1, yref = "paper", layer = "below",
                                             fillcolor = "#F3F6F8", line = list(width = 0))
      }
      shapes[[length(shapes) + 1]] <- list(type = "line", x0 = g0 - 0.42, x1 = g0 + 1.42,
                                           y0 = cn$duracao, y1 = cn$duracao,
                                           line = list(color = TINTA, dash = "dash", width = 1.5))
    }

    ymax <- max(c(aut, sapply(reais, `[[`, "duracao")), na.rm = TRUE) * 1.22
    # Rótulos de valor acima das barras e identificação A/B dentro delas.
    anot_valores <- lapply(seq_along(xs), function(k) {
      list(x = xs[k], y = aut[k], xref = "x", yref = "y", yanchor = "bottom", yshift = 3,
           showarrow = FALSE, text = paste0(fmt(aut[k], 1), " h ", sinais[k]),
           bgcolor = "rgba(255,255,255,0.92)", borderpad = 1,
           font = list(size = 10, color = TINTA))
    })
    anot_bancos <- lapply(seq_along(xs), function(k) {
      list(x = xs[k], y = max(aut[k] * 0.52, ymax * 0.035), xref = "x", yref = "y",
           showarrow = FALSE, text = rotulos_banco[k],
           bgcolor = "rgba(255,255,255,0.96)", borderpad = 2,
           font = list(size = 10, color = TINTA, family = FONTE))
    })

    plot_ly(x = xs, y = aut, type = "bar",
            marker = list(color = cor, line = list(color = rep(TINTA, length(xs)), width = lw)),
            hoverinfo = "text", hovertext = hov) %>%
      base_layout(
        margin = list(l = 54, r = 12, t = 14, b = 70),
        bargap = 0.2,
        xaxis = list(tickvals = c(0.5, 3.5, 6.5), ticktext = grupo_rotulos,
                     range = c(-0.7, 7.7), showline = TRUE, linecolor = CINZA,
                     ticks = "", showgrid = FALSE,
                     tickfont = list(size = 10, color = CINZA_TXT), fixedrange = TRUE),
        yaxis = list(range = c(0, ymax), title = list(text = "Autonomia (h)", standoff = 8),
                     showticklabels = TRUE, showgrid = TRUE, gridcolor = "#E9EDF1",
                     zeroline = FALSE, ticks = "outside", ticklen = 3,
                     tickfont = list(size = 10, color = CINZA_TXT), automargin = TRUE, fixedrange = TRUE),
        shapes = shapes,
        annotations = c(anot_valores, anot_bancos))
  })

  # ---- V3: sensibilidade da autonomia ao SOH ----
  output$v3 <- renderPlotly({
    cn <- cen(); p <- par()
    pc <- potencia_critica(cn)
    if (pc == 0) return(msg_plot("Sem cargas críticas neste cenário"))

    f <- seq(60, 100, by = 2)
    curva <- function(i) (bancos$E[i] * (f / 100) * p$dod * p$efi) / pc
    sel <- which(bancos$id == input$banco)
    ymax <- max(curva(1), curva(2), cn$duracao) * 1.18
    aut_atual <- sapply(1:2, function(i) avaliar(cn, bancos[i, ], p$soh, p$dod, p$efi)$aut)
    cor_pt <- sapply(1:2, function(i) STATUS[[avaliar(cn, bancos[i, ], p$soh, p$dod, p$efi)$status]]$cor)

    fig <- plot_ly()
    for (i in 1:2) {
      sel_i <- i == sel
      fig <- add_trace(fig, x = f, y = curva(i), type = "scatter", mode = "lines",
                       line = list(color = if (sel_i) TINTA else CINZA_2,
                                   width = if (sel_i) 3.5 else 2.5,
                                   dash = if (bancos$P[i] < pc) "dash" else "solid"),
                       hoverinfo = "text",
                       text = paste0("<b>Banco ", bancos$id[i], "</b><br>SOH: ", f,
                                     "%<br>Autonomia: ", fmt(curva(i)), " h"))
      fig <- add_trace(fig, x = p$soh * 100, y = aut_atual[i], type = "scatter", mode = "markers+text",
                       marker = list(color = cor_pt[i], size = 11, line = list(color = "white", width = 2)),
                       text = paste0(fmt(aut_atual[i], 1), " h ",
                                     STATUS[[avaliar(cn, bancos[i, ], p$soh, p$dod, p$efi)$status]]$icone),
                       textposition = if (i == 2) "top center" else "bottom center",
                       textfont = list(size = 10, color = TINTA), cliponaxis = FALSE,
                       hoverinfo = "text",
                       hovertext = paste0("Banco ", bancos$id[i], " com SOH de ", input$soh, "%: ",
                                          fmt(aut_atual[i]), " h"))
    }

    ends <- lapply(1:2, function(i) list(
      x = 100, y = curva(i)[length(f)], xanchor = "left", xshift = 7,
      showarrow = FALSE, font = list(size = 11, color = if (i == sel) TINTA else CINZA_TXT),
      text = paste0(if (i == sel) "<b>" else "", "Banco ", bancos$id[i],
                    if (bancos$P[i] < pc) "*" else "", if (i == sel) "</b>" else "")))

    fig %>% base_layout(
      margin = list(l = 58, r = 62, t = 28, b = 52),
      xaxis = list(tickvals = seq(60, 100, 10), ticksuffix = "%", range = c(58, 108),
                   title = list(text = "SOH (saúde da bateria)", standoff = 8),
                   showgrid = FALSE, showline = TRUE, linecolor = CINZA, ticks = "outside",
                   tickfont = list(size = 10, color = CINZA_TXT), fixedrange = TRUE),
      yaxis = list(range = c(0, ymax), title = list(text = "Autonomia (h)", standoff = 8),
                   showgrid = TRUE, gridcolor = "#E9EDF1", zeroline = FALSE,
                   ticks = "outside", ticklen = 3, automargin = TRUE,
                   tickfont = list(size = 10, color = CINZA_TXT), fixedrange = TRUE),
      shapes = list(
        list(type = "line", xref = "paper", x0 = 0, x1 = 1, y0 = cn$duracao, y1 = cn$duracao,
             line = list(color = TINTA, dash = "dash", width = 1.5)),
        list(type = "line", x0 = p$soh * 100, x1 = p$soh * 100, yref = "paper", y0 = 0, y1 = 1,
             line = list(color = CINZA, dash = "dot", width = 1.5))),
      annotations = c(ends, list(list(x = p$soh * 100, y = 1, yref = "paper", yanchor = "bottom",
                                      yshift = 7, showarrow = FALSE, bgcolor = "rgba(255,255,255,0.9)",
                                      borderpad = 1, font = list(size = 10, color = CINZA_TXT),
                                      text = paste0("SOH atual: ", input$soh, "%")))))
  })
}

shinyApp(ui, server)
