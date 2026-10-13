# Dicionario de Dados - AV1 Grupo 6 (EcoVolt)

## 1. Originais recebidos (preservados em `dados/raw/` - nunca alterados)

| Arquivo em `dados/raw/` | SHA-256 | Tamanho | O que REALMENTE contem |
|---|---|---|---|
| `ORIGINAL_nomeErrado_recarregados-emplacamentos.csv` | `de823114bf77616f110f38659e60431f5b0eb6375f3c4ec64f8d4b4d18125646` | 515.118 B | **Dataset SOH CALCE CS2** (CSV real) |
| `ORIGINAL_5_596Ah_charge.csv` | `cfbe14877c26c33dd2ea1cf20f1fc1ed31de2778eb37c2c8761987a714c286f9` | 294.905 B | **Curva de carga** 5,596 Ah (CSV) |
| `ORIGINAL_5.596Ah_charge.xlsx` | `072261ea7a95afc6ed41466a553b0b3ebfb547b676b2ed7b2391b6af5a852455` | 209.574 B | Curva de carga (XLSX, 4.180 linhas) |
| `ORIGINAL_nomeErrado_CALCE_CS2_ML_SOH_Dataset.csv` | `072261ea7a95afc6ed41466a553b0b3ebfb547b676b2ed7b2391b6af5a852455` | 209.574 B | **XLSX** (identico ao `5.596Ah_charge.xlsx`) |

> **Achado de qualidade #1 (rastreabilidade):** dois arquivos chegaram com o **nome trocado** e
> em **formato errado**:
> - `CALCE_CS2_ML_SOH_Dataset.csv` **nao** e CSV nem CALCE: e um **XLSX** (assinatura `PK`) e,
>   pelo hash, **identico** ao `5.596Ah_charge.xlsx`.
> - `recarregados-emplacamentos...csv` **nao** sao emplacamentos (ABVE): e o **dataset SOH CALCE**.
> - **Consequencia:** a base ABVE de emplacamentos **nao esta entre os arquivos**; ela nao e
>   usada na decisao de continuidade energetica e foi deixada fora do escopo desta AV1.

## 2. Datasets processados (`dados/processados/`)

| Arquivo | Origem | Descricao |
|---|---|---|
| `calce_cs2_soh.csv` | copia fiel do original mal nomeado | Dataset SOH CALCE CS2, nome ja correto |
| `calce_cs2_soh_limpo.csv` | `calce_cs2_soh.csv` + limpeza | Versao tratada (ver secao 4) |
| `curva_carga_5p596ah_xlsx.csv` | `ORIGINAL_5.596Ah_charge.xlsx` | Curva de carga exportada para CSV |

## 3. Dicionario de campos

### 3.1 `calce_cs2_soh.csv`
| Coluna | Tipo | Unidade | Descricao |
|---|---|---|---|
| `battery_id` | texto | - | Identificador da celula (CS2-33 ... CS2-38) |
| `cycle_number` | inteiro | ciclos | Numero do ciclo de carga/descarga |
| `C_rate` | float | C | Taxa de carga (0,5 ou 1,0) |
| `average_voltage_V` | float | V | Tensao media do ciclo |
| `average_current_A` | float | A | Corrente media do ciclo |
| `internal_resistance_ohm` | float | ohm | Resistencia interna estimada |
| `SOH` | float | % | State of Health (referencia) |

### 3.2 `curva_carga_5p596ah.csv`
| Coluna | Tipo | Unidade | Descricao |
|---|---|---|---|
| `Date_Time` | data-hora | - | Timestamp (1 Hz) |
| `Voltage(V)` | float | V | Tensao medida |
| `Current(A)` | float | A | Corrente de carga |
| `SOC` | float | 0-1 | Estado de carga |

## 4. Decisoes de limpeza (documentadas, sem tocar nos originais)

**CALCE (`calce_cs2_soh_limpo.csv`)** - 5.662 linhas:
1. Duplicatas exatas: **0**.
2. Duplicatas por chave (`battery_id`,`cycle_number`): **0**.
3. `SOH > 100`: **6 ocorrencias** - mantidas no campo `SOH` e **limitadas a 100** em
   `SOH_corrigido`; sinalizadas em `soh_acima_100_flag`. Regra: fisicamente SOH nao passa de 100%;
   nao removemos a linha para nao perder o ciclo.
4. Celulas nulas: **0**.
5. Ordenacao por `battery_id`, `cycle_number`.

**Curva de carga** - 4.180 linhas, **0 nulos**; SOC de 0,068 a 1,0; V de 2,93 a 3,65; I de 0 a 6 A.
- Capacidade integrada (∫I·dt): **5,5872 Ah**, coerente com a nominal de **5,596 Ah**
  (erro ~0,16%) -> sustenta o uso da curva como **verificacao de capacidade** (o SOH nao
  substitui ensaio de capacidade util).

## 5. Como os dados entram na decisao
- CALCE (SOH de 2a vida) -> `fator_capacidade` do banco (premissa **0,80**).
- Curva de carga -> **verificacao** de que a capacidade real ~ nominal.
- Os demais parametros (cargas criticas, duracao, Enominal, Pmax) sao **cenarios sinteticos
  declarados** (ver `analise/cenarios.json` e evidencias E1/E2).
