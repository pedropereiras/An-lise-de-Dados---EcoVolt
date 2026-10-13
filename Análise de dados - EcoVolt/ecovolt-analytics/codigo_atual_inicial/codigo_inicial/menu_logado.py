from calculando_soh import calcular_soh
import cadastro_concluido as cadastro
import os, platform, time

def limpar_tela():
    sistema_operacional = platform.system()

    if sistema_operacional == "Windows":
        os.system("cls")
    else:
        os.system("clear") # adaptação pro linux pq aparentemente eles usam clear?

def menu_principal():

            while True:
                
                time.sleep(1)
                limpar_tela()
                print(f"\nBem-vindo! (ADMIN)")
                print("\n=== MENU  PRINCIPAL ===\n== EcoVolt Analytics ==\n")
                print("1. Calcular Saúde da Bateria (SoH)")
                print("2. Gerenciar Contas Registradas")
                print("0. Sair")

                escolha = input("Escolha uma opção: ").strip()

                if escolha == "1":
                    calcular_soh()
                elif escolha == "2":
                    cadastro.menu_conta()  # Chama o menu de cadastro para gerenciar a conta
                elif escolha == "0":
                    print("\nObrigado por usar o EcoVolt Analytics! Até a próxima!\n")
                    exit()
                else:
                    print("\nOpção inválida. Por favor, tente novamente.\n")