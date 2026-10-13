import sqlite3
import os, platform, time

def limpar_tela():
    sistema_operacional = platform.system()

    if sistema_operacional == "Windows":
        os.system("cls")
    else:
        os.system("clear")

# config o banco de dados
def inicializar_banco():
    conexao = sqlite3.connect("Dados.db")
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Dados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sobrenome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    conexao.commit()
    conexao.close()


def cadastrar_usuario():
    while True:
        time.sleep(1.5)

        limpar_tela()
        try: #Bloco onde podem ocorrer erros.
            nome_completo = input("Digite seu nome completo: ").strip() #remove os espaços
            if not nome_completo:
                raise ValueError("O nome não pode ficar vazio.")
            if not nome_completo.replace(" ", "").isalpha(): #existe apenas letras
                raise ValueError("O nome deve conter apenas letras.")
            partes_nome = nome_completo.split() #divide o texto
            if len(partes_nome) < 2:
                raise ValueError("Digite nome e sobrenome.")
            nome = partes_nome[0]
            sobrenome = " ".join(partes_nome[1:])

            email = input("Digite seu e-mail: ").strip().lower()
            if email.count("@") != 1:
                raise ValueError("Digite um e-mail válido.")
            usuario_email, dominio = email.split("@")
            if not usuario_email or "." not in dominio:
                raise ValueError("Digite um e-mail válido.")

            # Conectar ao banco para verificar se o e-mail já existe
            conexao = sqlite3.connect("Dados.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT email FROM Dados WHERE email = ?", (email,)) # esse tipo de consulta é melhor do que concatenar strings usando o f-string pq previne SQL injection.
            
            if cursor.fetchone():
                conexao.close()
                raise ValueError("E-mail já cadastrado.")

            senha = input("Digite sua senha: ").strip()
            confirmar_senha = input("Confirme sua senha: ").strip()
            if len(senha) < 6:
                conexao.close()
                raise ValueError("A senha deve ter pelo menos 6 caracteres.")
            if senha != confirmar_senha:
                conexao.close()
                raise ValueError("As senhas não coincidem.")

            # Inserir no banco de dados
            cursor.execute("""
                INSERT INTO Dados (nome, sobrenome, email, senha) 
                VALUES (?, ?, ?, ?)
            """, (nome, sobrenome, email, senha))
            
            conexao.commit()
            conexao.close()

            print("\nCadastro realizado com sucesso!\n")
            break

        except ValueError as erro: #Captura erros do tipo: ValueError
            print(f"Erro: {erro}")


def login_usuario():
    limpar_tela()
    email = input("Digite seu e-mail: ").strip().lower()
    senha = input("Digite sua senha: ").strip()

    conexao = sqlite3.connect("Dados.db")
    cursor = conexao.cursor()
    
    # Busca o usuário com o e-mail e senha correspondentes
    cursor.execute("SELECT nome, sobrenome, email FROM Dados WHERE email = ? AND senha = ?", (email, senha))
    usuario = cursor.fetchone()
    conexao.close()

    if usuario:
        limpar_tela()
        print("\nLogin realizado com sucesso!")
        print(f"Bem-vindo, {usuario[0]}!")

        time.sleep(2)

        return {"nome": usuario[0], "sobrenome": usuario[1], "email": usuario[2]}
    else:
        print("E-mail ou senha incorretos.")
        return None


def listar_usuarios():

    limpar_tela()

    conexao = sqlite3.connect("Dados.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, sobrenome, email FROM Dados")
    usuarios = cursor.fetchall()
    conexao.close()

    if not usuarios:
        print("Nenhum usuário cadastrado.")
    else:
        print("\n=== USUÁRIOS CADASTRADOS ===")
        for usuario in usuarios:
            print("-" * 30)
            print(f"Nome: {usuario[0]} {usuario[1]}")
            print(f"E-mail: {usuario[2]}")

    input("Aperte a tecla ENTER para sair.")


def buscar_usuario():

    limpar_tela()

    email = input("Digite o e-mail para busca: ").strip().lower()

    conexao = sqlite3.connect("Dados.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, sobrenome, email FROM Dados WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    conexao.close()

    if usuario:
        print("\nUsuário encontrado!")
        print(f"Nome: {usuario[0]} {usuario[1]}")
        print(f"E-mail: {usuario[2]}")
    else:
        print("Usuário não encontrado.")

    input("Aperte a tecla ENTER para sair.")


def atualizar_usuario():
    limpar_tela()
    email = input("Digite o e-mail do usuário: ").strip().lower()

    conexao = sqlite3.connect("Dados.db")
    cursor = conexao.cursor()
    
    # Verifica se o usuário existe antes de tentar atualizar
    cursor.execute("SELECT nome, sobrenome, senha FROM Dados WHERE email = ?", (email,))
    usuario = cursor.fetchone()

    if usuario:

        # Se o usuário der "Enter" sem digitar nada, mantém o valor antigo

        novo_nome = input(f"Novo nome [{usuario[0]}]: ").strip()
        if novo_nome and not novo_nome.isalpha():

            print("Nome inválido. Alteração descartada.")
            novo_nome = usuario[0]

        elif not novo_nome:
            novo_nome = usuario[0]

        novo_sobrenome = input(f"Novo sobrenome [{usuario[1]}]: ").strip()
        if novo_sobrenome and not novo_sobrenome.replace(" ", "").isalpha():

            print("Sobrenome inválido. Alteração descartada.")
            novo_sobrenome = usuario[1]

        elif not novo_sobrenome:
            novo_sobrenome = usuario[1]

        nova_senha = input("Nova senha [ENTER para manter a atual]: ").strip()
        if not nova_senha:
            nova_senha = usuario[2]

        # Atualiza no banco
        cursor.execute("""
            UPDATE Dados 
            SET nome = ?, sobrenome = ?, senha = ?
            WHERE email = ?
        """, (novo_nome, novo_sobrenome, nova_senha, email))
        
        conexao.commit()
        print("Usuário atualizado com sucesso!")
        input("pressione ENTER para sair. ")

    else:
        print("Usuário não encontrado.")
        input("pressione ENTER para sair. ")
        
    conexao.close()

def excluir_usuario():
    limpar_tela()
    email = input("Digite o e-mail do usuário: ").strip().lower()

    conexao = sqlite3.connect("Dados.db")
    cursor = conexao.cursor()
    
    # Verifica se o usuário existe
    cursor.execute("SELECT email FROM Dados WHERE email = ?", (email,))
    if cursor.fetchone():

        cursor.execute("DELETE FROM Dados WHERE email = ?", (email,))
        conexao.commit()
        print("Usuário removido com sucesso!")
        input("pressione ENTER para sair. ")

    else:
        print("Usuário não encontrado.")
        
    conexao.close()


# --- FLUXO PRINCIPAL (MENU) ---
def menu_conta():
    # Garante que o banco e a tabela existam antes de rodar o menu
    inicializar_banco()

    while True:
        limpar_tela()
        print("\n===== MENU ADMINISTRADOR =====")
        print("1 - Listar")
        print("2 - Buscar")
        print("3 - Atualizar")
        print("4 - Excluir")
        print("5 - Voltar ao Menu Principal")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            listar_usuarios()
        elif opcao == "2":
            buscar_usuario()
        elif opcao == "3":
            atualizar_usuario()
        elif opcao == "4":
            excluir_usuario()
        elif opcao == "5":
            print("Voltando ao menu principal...")
            break
        elif opcao == "0":
            print("Programa encerrado.")
            exit()
        else:
            print("Opção inválida.")

inicializar_banco() # chamar o arquivo pra ele ser executado imediatamente (FALLBACK)