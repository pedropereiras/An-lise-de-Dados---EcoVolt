# Repositório do projeto do grupo 8 de Banco de Dados e IA - 1° Período.
## Alunos: Lucas Oliveira, Pedro Pereira, Mateus Tarcísio, Daniel Lucas, Breno Neves, Romeu Alves
## Professores: Lucas Farias (Projetos) e Flávio Neves (Fundamentos da Programação)
----------------------------------------------------------------------------------
### escrito por mim (Lucas)
## Pessoal, leiam:

### Primeiro, você deve baixar o git bash
### Para acessar isso dentro do git bash (programa que nós vamos utilizar daqui para frente) tem que fazer isso:

### 1. acesse o link: https://git-scm.com/install/windows
### Se não conseguir acessar o link direto, copia e cola no navegador e instale.

### 2. Depois de baixado, entre no git bash
### Após entrar, você estará na pasta ' C:\Users\seu-nome-de-usuario ', também conhecida como Diretório Pessoal ou até mesmo Home pra quem usa sistemas baseados em Unix e Linux. (indicada pelo ' ~ ' laranja). Para saber as coisas que estão dentro da pasta home (comando MUITO importante), é só digitar o comando: 

## ls  
### Que vai listar todas as pastas e arquivos presentes.
### O comando:

## cd nome-da-pasta
### vai fazer com que você entre na pasta digitada.

### antes de fazer alguma alteração ou entrar em alguma pasta, no seu Diretório Pessoal, faça um clone do repositório.
### Para clonar o repositório, digite o seguinte comando no terminal do Git Bash:

## git clone https://github.com/lucaas783/bd-1p-grupo8-projeto.git

### Com isso, o repositório já vai estar clonado, e você estará na branch (ramificação) main.

### NÃO TRABALHE NA BRANCH MAIN OU DEVELOP!!!!!
### Cada um vai ter uma branch (ramificação) para trabalhar na parte do seu código, com o seu respectivo nome.
### após clonar o repositorio, dê o comando:

## git pull

### para atualizar o seu repositorio local com o remoto do github
### depois, faça o comando

## git fetch

### para baixar todos os arquivos e branches (ramificações) do github remoto para a sua máquina.
### depois, faça o comando

## git branch -a

### para mostrar todas as branches (ramificações) existentes. Você deve entrar na ramificação com o seu nome.
### depois, faça o comando

## git checkout nome-da-ramificação OU git switch nome-da-ramificacao

### para entrar na sua ramificação. NOTA: digite o seu primeiro nome minusculo para entrar na sua ramificação.

### COMO FAZER ALTERAÇÕES E MANDAR PARA O REPOSITÓRIO REMOTO - GITHUB - A PARTIR DO GIT BASH

### Para fazer / mandar um arquivo da sua ramificação de trabalho (a ramificação com o seu nome), aqui estão alguns
### comandos opcionais que você pode fazer.

## mkdir
### esse comando cria uma pasta. Pode ser útil para se organizar e não ficar confuso

## cp nome-do-arquivo local-atual local-novo
### esse comando serve para copiar o arquivo de um lugar para o outro.
### NÃO faça isso para copiar de uma branch para outra.
### Nota: se você já está no local do arquivo que você deseja copiar, basta apenas colocar o nome e o local novo.

## vi nome-do-arquivo
### serve para você editar o arquivo no proprio terminal do git bash.
### Nota: se o arquivo não existe, ele vai criar um arquivo com o nome que você colocou. Porém, ele não será salvo caso você saia sem salvá-lo.
### aqui vão algumas teclas simples sobre o comando - vi -
### Tecla INSERT -> serve para você editar o arquivo
### para salvar o arquivo, você deve clicar na Tecla ESC
### quando você clica na Tecla ESC, você vai estar no modo normal (normal mode)
### no Modo Normal, você pode fazer alguns comandos:

### :x  vai salvar o arquivo
### :x! vai salvar o arquivo de forma forçada
### :q  vai sair do arquivo sem salvar
### :q! vai sair do arquivo sem salvar de forma forçada
### Quando um desses comandos forem realizados, você vai sair automaticamente do modo de edição do arquivo.

## Se der ruim, o que fazer?
### O mais provável de acontecer, é que, pode-se acontecer alguns erros, como:
### 1. dar git commit, git push sem dar git pull antes (e por consequencia a sua copia do repositório estiver desatualizada com a do github
### 2. dar git commit, git push só que esqueceu de preparar ele (no caso, dar git add nome-do-arquivo)

### O que fazer depois de editar um arquivo?

### Faça um git status, veja os arquivos que precisam ser "empacotados" para fazer o Commit.
### depois, faça um git add nome-do-arquivo (ou git add . se você estiver seguro com o que estiver fazendo)
### depois, faça um git commit -m "mensagem explicando o que você fez"
### depois, faça um git push. O arquivo será salvo na sua ramificação no github
