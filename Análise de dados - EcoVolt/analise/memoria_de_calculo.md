# Memoria de Calculo - AV1 Grupo 6 (EcoVolt)

Decisao: **"Nas condicoes informadas, o cenario atende as cargas criticas durante o tempo requerido?"**

## 1. Formulas (guia do professor)

```
Pcritica      = soma( potencia_i * quantidade_simultanea_i )
Edemanda      = Pcritica * duracao
Eutilizavel   = Enominal * fator_capacidade * fracao_uso * eficiencia
autonomia     = Eutilizavel / Pcritica            (indefinida se Pcritica = 0)
Enao_atendida = max(0, Edemanda - Eutilizavel)
inviavel por potencia  se  Pmax < Pcritica
```

Implementacao: `analise/modelo_energia.py`.

## 2. Parametros do banco (origem declarada)

| Parametro | Valor | Origem |
|---|---|---|
| `fator_capacidade` | 0,80 | SOH de 2a vida (CALCE CS2) |
| `fracao_uso` (DoD) | 0,90 | premissa declarada |
| `eficiencia` | 0,90 | premissa declarada |

- Banco **A** (conservador): `Enominal` = 5,0 kWh, `Pmax` = 1,0 kW -> **Eutilizavel = 3,24 kWh**
- Banco **B** (expandido):  `Enominal` = 10,0 kWh, `Pmax` = 3,0 kW -> **Eutilizavel = 6,48 kWh**

Exemplo do calculo de B: `10,0 x 0,80 x 0,90 x 0,90 = 6,48 kWh`.

## 3. Resultados por cenario

| Cenario | Duracao | Pcritica | Edemanda | A autonomia | A status | B autonomia | B status |
|---|---|---|---|---|---|---|---|
| Sala de vacinas | 8 h | 0,50 kW | 4,00 kWh | 6,48 h | NAO ATENDE (faltam 0,76 kWh) | 12,96 h | ATENDE |
| Radio-base (telecom) | 4 h | 1,20 kW | 4,80 kWh | 2,70 h | INVIAVEL POR POTENCIA (Pmax 1,0 < 1,2) | 5,40 h | ATENDE |
| Residencia essencial | 6 h | 0,91 kW | 5,46 kWh | 3,56 h | NAO ATENDE (faltam 2,22 kWh) | 7,12 h | ATENDE |
| Caso vazio | 4 h | 0,00 kW | 0,00 kWh | indefinida | SEM CARGA CRITICA (guarda) | indefinida | SEM CARGA CRITICA (guarda) |

## 4. Leitura da decisao
- **Banco A** e insuficiente nos 3 cenarios reais; no de telecom falta inclusive **potencia**.
- **Banco B** atende todos os cenarios.
- O cenario de **telecom** e o caso que **distingue restricao de energia x potencia**: para A,
  a autonomia (2,70 h) seria complementar, mas `Pmax < Pcritica` inviabiliza por **potencia**.

## 5. Conferencia independente
`analise/04_validacao.py` reproduz o exemplo do professor (3 kW, 3 h, 6 kWh, 4 kW ->
9 kWh, 2 h, 3 kWh; com Pmax=2 kW tambem insuficiencia de potencia) e recalcula o cenario
"posto de vacinas / banco B" por caminho alternativo. Resultado: **TODAS AS CONFERENCIAS OK**.
