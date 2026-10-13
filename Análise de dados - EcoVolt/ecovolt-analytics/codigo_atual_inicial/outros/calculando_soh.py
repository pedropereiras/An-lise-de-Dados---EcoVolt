# Lógica do SOH:
# 1. A_orig (autonomia_original) em km (quilômetros)
# 2. A_atual (autonomia_atual) em km (quilômetros)
# 3. idade (idade_veiculo) em anos
# 4. F_uso (fator_uso) fator de frequência de uso
# 5. F_carga (fator_carga) fator de frequência de carga
# 6. F_tipo (fator_tipo) fator de tipo de carregamento

# Fontes: https://ifpr.edu.br/curitiba/wp-content/uploads/sites/11/2025/04/Douglas-e-Thiago-TCC-2024.pdf
# https://www.nature.com/articles/s41598-025-93775-y
# Front de Pedro tbm foi uma fonte
# Eu tbm copiei as respostas iguais a do front de pedro inclusive os mesmos emojis pra ficar igual ao front que ele mandou, vou mandar no github isso agora (acredito que está pronto).

def calcular_soh():
    print("===== CALCULADORA DA SAÚDE DA BATERIA (SoH) =====\n")

    while True: 
        try:
            autonomia_original = float(input("1. Qual a autonomia original do veículo (em km)? "))
            autonomia_atual = float(input("2. Qual a autonomia percebida hoje (em km)? "))
            idade = float(input("3. Qual a idade do veículo (em anos)? "))
        except ValueError:
            print("\n❌ Erro: Por favor, insira apenas números para autonomia e idade.")
            continue
        break

    # Fatores de impacto (aquelas perguntas que tinha dentro do JS de pedro)
    opcoes_uso = {
        "1": {"texto": "🌿 Pouco uso", "peso": 1.0},
        "2": {"texto": "🚗 Uso moderado", "peso": 1.1},
        "3": {"texto": "⚡ Uso intenso", "peso": 1.3}
    }

    opcoes_carga = {
        "1": {"texto": "🌙 Ocasional", "peso": 1.0},
        "2": {"texto": "🔋 Regular", "peso": 1.1},
        "3": {"texto": "⚡ Frequente", "peso": 1.25}
    }

    opcoes_tipo = {
        "1": {"texto": "🏠 Lento (residencial)", "peso": 1.0},
        "2": {"texto": "⚡ Rápido (DC)", "peso": 1.2}
    }

    # 3. Coleta de dados qualitativos com validação
    # Detalhe: a função get() com um valor padrão garante que mesmo que o usuário escreva algo errado, o programa não pare de rodar e como fallback usar um valor padrão hardcodado

    print("\n4. Com que frequência você usa o veículo?")
    for k, v in opcoes_uso.items():
        print(f"  [{k}] {v['texto']}")
    resp_uso = input("Escolha uma opção (1/2/3): ")
    fator_uso = opcoes_uso.get(resp_uso, opcoes_uso["2"])["peso"] # Padrão: Moderado

    print("\n5. Com que frequência você carrega?")
    for k, v in opcoes_carga.items():
        print(f"  [{k}] {v['texto']}")
    resp_carga = input("Escolha uma opção (1/2/3): ")
    fator_carga = opcoes_carga.get(resp_carga, opcoes_carga["2"])["peso"] # Padrão: Regular

    print("\n6. Tipo de carregamento mais usado?")
    for k, v in opcoes_tipo.items():
        print(f"  [{k}] {v['texto']}")
    resp_tipo = input("Escolha uma opção (1/2): ")
    fator_tipo = opcoes_tipo.get(resp_tipo, opcoes_tipo["1"])["peso"] # Padrão: Lento

    # CALCULOS

    # Passo 1: Eficiência da Autonomia (no caso o calculo do SoH padrão sem os fatores alternos como o fator de uso, carga e tipo de carregamento)
    eficiencia_autonomia = (autonomia_atual / autonomia_original) * 100

    # Passo 2: Aplicação dos fatores de degradação química por idade e uso
    fator_estresse = fator_uso * fator_carga * fator_tipo
    degradacao_estimada = idade * 2.5 * fator_estresse # 2.5 significa uma taxa constante anual, em porcentagem de degradação da bateria de litio. No caso, eu pesquisei e deu entre 2% e 3%, por isso 2.5
    
    # Passo 3: Resultado Final do SoH
    soh_final = eficiencia_autonomia - degradacao_estimada

    # fallbacks caso o resultado passe de limites lógicos (obv n vai passar mas é bom ter)
    if soh_final > 100:
        soh_final = 100.0
    if soh_final > eficiencia_autonomia:
        soh_final = eficiencia_autonomia

    # printando os resultados 
    print("\n" + "="*40)
    print("         RELATÓRIO DE SAÚDE DA BATERIA      ")
    print("="*40)
    print(f" Eficiência de Autonomia Direta: {eficiencia_autonomia:.2f}%")
    print(f" Penalidade por Perfil de Uso:  -{degradacao_estimada:.2f}%")
    print("-"*40)
    print(f" ESTADO DE SAÚDE ESTIMADO (SoH): {soh_final:.2f}%")
    print("="*40)

    # Diagnóstico final
    if soh_final >= 80:
        print("🔋 Status: Excelente! A bateria está muito saudável.")
    elif soh_final >= 70:
        print("🟡 Status: Segunda vida. Inutilizável para o carro, recomendável para ser encaminhada para segunda vida.")
    else:
        print("⚠️ Alerta: A degradação está bastante elevada. Considere uma avaliação profissional para possível substituição.")



if __name__ == "__main__":
    calcular_soh()