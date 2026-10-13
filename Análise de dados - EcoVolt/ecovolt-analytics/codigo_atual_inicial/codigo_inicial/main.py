import cadastro_concluido as cadastro
from menu_logado import menu_principal, limpar_tela
import os, platform

def limpar_tela():
    sistema_operacional = platform.system()

    if sistema_operacional == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def main():

    limpar_tela()

    print("\nBem-vindo ao EcoVolt Analytics!\nO sistema de avaliação de saúde da bateria do seu veículo elétrico!")

    print("\nFaça login para acessar o sistema\nOu crie uma conta par começar a usar.")

    while True:

        escolha = input("Digite \"1\" para login ou \"2\" para cadastro ou \"0\" para sair: ").strip()

        if escolha == "1":

            # loop while para tentar login até o valor retornado ser true, ou se o usuário escolher fazer cadastro.

            while True:

                usuario_logado = cadastro.login_usuario()
                if usuario_logado:
                    menu_principal()  # Só chama se usuario_logado for true
                    break

                else:

                    print("Tente novamente ou digite '2' para criar uma conta.")
                    escolha_login = input("Digite \"1\" para tentar login novamente ou \"2\" para cadastro: ").strip()

                    if escolha_login == "2":
                        cadastro.cadastrar_usuario() # chama a função aqui dentro mesmo (para melhorar a experiência do usuario)

                        menu_principal()  # Chama o menu principal após o cadastro
                        break


        elif escolha == "2":
            cadastro.cadastrar_usuario()
            menu_principal()  # Chama o menu principal após o cadastro

        elif escolha == "0":
            print("\nObrigado por usar o EcoVolt Analytics! Até a próxima!")
            exit()
