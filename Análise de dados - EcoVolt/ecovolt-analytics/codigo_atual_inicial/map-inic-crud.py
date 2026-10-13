import sqlite3
import hashlib
import re
import datetime
from colorama import Fore, Style, init
from os import system

init(autoreset=True)  # reseta a cor automaticamente após cada print

CAMINHO_BANCO = "usuarios.db"

# SISTEMA DE MENSAGEM PENDENTE

# Problema original: mensagens de erro/sucesso eram apagadas
# imediatamente pelo próximo system("cls").
#
# A função cabecalho() sempre a exibe (se existir) entre o header
# e o menu, e depois a limpa para não repetir.

_mensagem_pendente: str = ""

def definir_mensagem(msg: str):
    """Armazena uma mensagem para exibir no próximo cabecalho()."""
    global _mensagem_pendente
    _mensagem_pendente = msg

def cabecalho(titulo: str = ""):
    """
    Limpa o terminal, imprime o header da aplicação,
    exibe a mensagem pendente (se houver) e o título da tela.
    """
    global _mensagem_pendente

    system("cls")
    print(Fore.GREEN + "==========================")
    print(Fore.GREEN + "  🍃 EcoVolt Analytics")
    print(Fore.GREEN + "==========================")

    # Exibe a mensagem pendente entre o header e o conteúdo da tela
    if _mensagem_pendente:
        print(f"\n{_mensagem_pendente}")
        _mensagem_pendente = ""   # limpa após exibir

    if titulo:
        print(Fore.YELLOW + f"\n{titulo}")


# CONEXÃO CENTRALIZADA

def get_conexao():
    """Retorna uma conexão com o banco de dados."""
    return sqlite3.connect(CAMINHO_BANCO)


# BANCO DE DADOS

def criar_banco():
    """Cria a tabela de usuários se ainda não existir."""
    with get_conexao() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                nome  TEXT    NOT NULL,
                email TEXT    NOT NULL UNIQUE,
                senha TEXT    NOT NULL
            )
        """)

# SEGURANÇA

def hash_senha(senha: str) -> str:
    """Retorna o hash SHA-256 da senha."""
    return hashlib.sha256(senha.encode()).hexdigest()

def validar_email(email: str) -> bool:
    """Valida o formato básico de um e-mail."""
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return re.match(padrao, email) is not None


# CREATE — Cadastro

def cadastrar_usuario():
    cabecalho("=== CADASTRO ===")

    nome  = input("Nome: ").strip()
    email = input("Email: ").strip()
    senha = input("Senha: ").strip()

    if not nome or not email or not senha:
        definir_mensagem(Fore.RED + "❌ Preencha todos os campos!")
        #cadastrar_usuario()
        return

    if not validar_email(email):
        definir_mensagem(Fore.RED + "❌ Formato de e-mail inválido!")
        #cadastrar_usuario()
        return

    try:
        with get_conexao() as conexao:
            conexao.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, hash_senha(senha))
            )
        definir_mensagem(Fore.GREEN + f"✅ Cadastro realizado! Bem-vindo, {nome}!")
        menu_logado(nome, _buscar_id_por_email(email))

    except sqlite3.IntegrityError:
        definir_mensagem(Fore.RED + "❌ E-mail já cadastrado!")
        #cadastrar_usuario()


# READ — Login e Busca

def login_usuario():
    cabecalho("=== LOGIN ===")

    email = input("Email: ").strip()
    senha = input("Senha: ").strip()

    with get_conexao() as conexao:
        cursor = conexao.execute(
            "SELECT id, nome FROM usuarios WHERE email = ? AND senha = ?",
            (email, hash_senha(senha))
        )
        usuario = cursor.fetchone()

    if usuario:
        usuario_id, nome = usuario
        definir_mensagem(Fore.GREEN + f"✅ Bem-vindo, {nome}!")
        menu_logado(nome, usuario_id)
    else:
        definir_mensagem(Fore.RED + "❌ E-mail ou senha incorretos!")
        #login_usuario()

def _buscar_id_por_email(email: str):
    """Auxiliar interno: retorna o id do usuário pelo e-mail."""
    with get_conexao() as conexao:
        cursor = conexao.execute(
            "SELECT id FROM usuarios WHERE email = ?", (email,)
        )
        resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def listar_usuarios():
    """Exibe todos os usuários cadastrados (sem mostrar a senha)."""
    cabecalho("=== USUÁRIOS CADASTRADOS ===")

    with get_conexao() as conexao:
        cursor = conexao.execute("SELECT id, nome, email FROM usuarios")
        usuarios = cursor.fetchall()

    if not usuarios:
        print("Nenhum usuário cadastrado.")
    else:
        for u in usuarios:
            print(f"  ID: {u[0]} | Nome: {u[1]} | Email: {u[2]}")

    input(Fore.YELLOW + "\n[Enter para voltar]")

# UPDATE — Atualização

def atualizar_usuario(usuario_id: int):
    cabecalho("=== ATUALIZAR CADASTRO ===")
    print("(Pressione Enter para manter o valor atual)\n")

    novo_nome  = input("Novo nome: ").strip()
    novo_email = input("Novo e-mail: ").strip()
    nova_senha = input("Nova senha: ").strip()

    if novo_email and not validar_email(novo_email):
        definir_mensagem(Fore.RED + "❌ Formato de e-mail inválido!")
        #atualizar_usuario(usuario_id)
        return 

    campos_alterados = False

    try:
        with get_conexao() as conexao:
            if novo_nome:
                conexao.execute(
                    "UPDATE usuarios SET nome = ? WHERE id = ?",
                    (novo_nome, usuario_id)
                )
                campos_alterados = True
            if novo_email:
                conexao.execute(
                    "UPDATE usuarios SET email = ? WHERE id = ?",
                    (novo_email, usuario_id)
                )
                campos_alterados = True
            if nova_senha:
                conexao.execute(
                    "UPDATE usuarios SET senha = ? WHERE id = ?",
                    (hash_senha(nova_senha), usuario_id)
                )
                campos_alterados = True

        if campos_alterados:
            definir_mensagem(Fore.GREEN + "✅ Dados atualizados com sucesso!")
        else:
            definir_mensagem(Fore.YELLOW + "ℹ️  Nenhum campo alterado.")

    except sqlite3.IntegrityError:
        definir_mensagem(Fore.RED + "❌ Este e-mail já está em uso por outro usuário!")
        #atualizar_usuario(usuario_id)

# DELETE — Exclusão

def deletar_usuario(usuario_id: int):
    cabecalho("=== DELETAR CONTA ===")
    confirmacao = input("⚠️  Esta ação é irreversível! Digite 'CONFIRMAR' para prosseguir: ").strip()

    if confirmacao != "CONFIRMAR":
        definir_mensagem(Fore.YELLOW + "❌ Operação cancelada.")
        return False

    with get_conexao() as conexao:
        conexao.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))

    definir_mensagem(Fore.GREEN + "✅ Conta deletada com sucesso!")
    return True


# SIMULADOR SOH


CICLOS_ESPERADOS = {
    "tesla":     1500,
    "byd":       3000,
    # "catl":      3000,
    # "lg":        1000,
    # "samsung":   1000,
    # "panasonic": 1000,
    "outros":    1000,
}

def _ciclos_esperados(fabricante: str) -> int:
    return CICLOS_ESPERADOS.get(fabricante.lower(), CICLOS_ESPERADOS["outros"])

def _alerta_ciclos(ciclos: float, fabricante: str) -> str:
    vida_util  = _ciclos_esperados(fabricante)
    percentual = (ciclos / vida_util) * 100

    if percentual < 50:
        return Fore.GREEN + f"🟢 Ciclos OK ({ciclos:.0f}/{vida_util} — {percentual:.1f}% da vida útil)"
    elif percentual < 80:
        return Fore.YELLOW + f"🟡 Atenção: {ciclos:.0f}/{vida_util} ciclos ({percentual:.1f}% da vida útil)"
    else:
        return Fore.RED + f"🔴 Crítico: {ciclos:.0f}/{vida_util} ciclos ({percentual:.1f}% da vida útil)"

def simulador(nome_usuario: str):
    cabecalho(f"=== SIMULADOR SOH — Olá, {nome_usuario}! ===")

    try:
        fabricante   = input("Fabricante da bateria: ").strip()
        modelo       = input("Modelo do carro: ").strip()
        ano_str      = input("Ano do carro (fabricação): ").strip()
        cap_original = float(input("Capacidade original da bateria (kWh): "))
        cap_atual    = float(input("Capacidade atual da bateria (kWh): "))
        ciclos       = float(input("Ciclos de carga: "))

        if not fabricante or not modelo or not ano_str:
            definir_mensagem(Fore.RED + "❌ Preencha todos os campos de texto!")
            simulador(nome_usuario)
            return

        ano = int(ano_str)
        ano_atual = datetime.date.today().year

        if ano < 2000 or ano > ano_atual:
            definir_mensagem(Fore.RED + f"❌ Ano inválido! Informe um valor entre 2000 e {ano_atual}.")
            simulador(nome_usuario)
            return

        if cap_original <= 0:
            definir_mensagem(Fore.RED + "❌ A capacidade original deve ser maior que zero!")
            simulador(nome_usuario)
            return

        if cap_atual < 0 or cap_atual > cap_original:
            definir_mensagem(Fore.RED + "❌ A capacidade atual não pode ser negativa nem maior que a original!")
            simulador(nome_usuario)
            return

        if ciclos < 0:
            definir_mensagem(Fore.RED + "❌ O número de ciclos não pode ser negativo!")
            simulador(nome_usuario)
            return

        soh = (cap_atual / cap_original) * 100
        soh = max(0.0, min(100.0, soh))

        capacidade_perdida = cap_original - cap_atual
        anos_uso = ano_atual - ano

        if soh >= 90:
            cor_soh      = Fore.GREEN
            status       = "Excelente 🟢"
            recomendacao = "Bateria em ótimo estado. Continue com as práticas atuais de carregamento."
        elif soh >= 80:
            cor_soh      = Fore.YELLOW
            status       = "Segunda Vida 🟡"
            recomendacao = "Desgaste moderado. Evite cargas acima de 80% e abaixo de 20%.\n Recomendável para esta bateria ser encaminhada para segunda vida."
        elif soh >= 60:
            cor_soh      = Fore.RED
            status       = "Desgastada 🔴"
            recomendacao = "Bateria degradada. Autonomia reduzida. Deve ser encaminhada para reciclagem"
        else:
            cor_soh      = Fore.WHITE
            status       = "Fim de Vida ⚫"
            recomendacao = "Bateria no limite. Recomenda-se substituição para uso seguro."

        alerta = _alerta_ciclos(ciclos, fabricante)

        cabecalho("=== RESULTADO DA ANÁLISE ===")
        print(f"  Fabricante        : {fabricante}")
        print(f"  Modelo            : {modelo}")
        print(f"  Ano / Uso         : {ano} ({anos_uso} ano(s))")
        print(f"  Cap. original     : {cap_original:.1f} kWh")
        print(f"  Cap. atual        : {cap_atual:.1f} kWh")
        print(f"  Capacidade perdida: {capacidade_perdida:.2f} kWh")
        print(Fore.YELLOW + "\n" + "-" * 40)
        print(cor_soh + f"  SOH    : {soh:.2f}%")
        print(cor_soh + f"  Status : {status}")
        print(f"  Ciclos : {alerta}")
        print(Fore.YELLOW + "-" * 40)
        print(f"\n  💡 {recomendacao}\n")

    except ValueError:
        definir_mensagem(Fore.RED + "❌ Erro: verifique se os valores numéricos foram digitados corretamente!")
        simulador(nome_usuario)
        return

    input(Fore.YELLOW + "[Enter para voltar ao menu]")


# MENU PÓS-LOGIN

# def _deletar_e_sair(usuario_id: int):
#     """Deleta a conta e sinaliza saída do menu_logado."""
#     deletar_usuario(usuario_id)

def menu_logado(nome: str, usuario_id: int):
    """Menu exibido após autenticação bem-sucedida."""

    opcoes = {
        "1": ("Simulador SOH",       lambda: simulador(nome)),
        "2": ("Atualizar cadastro",  lambda: atualizar_usuario(usuario_id)),
        "3": ("Deletar minha conta", lambda: deletar_usuario(usuario_id)),
        "4": ("Listar usuários",     listar_usuarios),
        "5": ("Sair da conta",       None),
    }

# MENU PÓS-LOGIN

def menu_logado(nome: str, usuario_id: int):
    """Menu exibido após autenticação bem-sucedida."""

    opcoes = {
        "1": ("Simulador SOH",       lambda: simulador(nome)),
        "2": ("Atualizar cadastro",  lambda: atualizar_usuario(usuario_id)),
        "3": ("Deletar minha conta", lambda: deletar_usuario(usuario_id)),
        "4": ("Listar usuários",     listar_usuarios),
        "5": ("Sair da conta",       None),
    }

    while True:
        cabecalho(f"===== MENU ({nome}) =====")

        for chave, (descricao, _) in opcoes.items():
            print(f"  ({chave}) {descricao}")

        escolha = input("\nEscolha: ").strip()

        if escolha not in opcoes:
            definir_mensagem(Fore.RED + "❌ Opção inválida!")
            continue

        _, acao = opcoes[escolha]

        if acao is None:
            definir_mensagem(Fore.GREEN + "👋 Sessão encerrada.")
            break

        # Executa a função escolhida e guarda o resultado (se houver)
        resultado = acao()

        # Se o usuário escolheu deletar (3) e a função retornou True (confirmou)
        if escolha == "3" and resultado is True:
            break


# MENU PRINCIPAL

def menu():
    while True:
        cabecalho("===== MENU PRINCIPAL =====")
        print("  (1) Login")
        print("  (2) Cadastro")
        print("  (3) Sair")

        escolha = input("\nEscolha: ").strip()

        if escolha == "1":
            login_usuario()
        elif escolha == "2":
            cadastrar_usuario()
        elif escolha == "3":
            cabecalho()
            print(Fore.GREEN + "  Até logo! 👋\n")
            break
        else:
            definir_mensagem(Fore.RED + "❌ Opção inválida!")

# MAIN

def main():
    criar_banco()
    menu()

if __name__ == "__main__":
    main()