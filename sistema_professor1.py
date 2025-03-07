


from flask import Flask, render_template, redirect, request, flash
import mysql.connector
from mysql.connector import Error

# Criação da Flask
app = Flask(__name__)

# Definindo uma chave para proteger a aplicação
app.config['SECRET_KEY'] = 'EXTENCAO'

# Configuração do banco de dados
db_config = {
    'host': 'localhost',       # Endereço do servidor do banco de dados
    'user': 'root',            # Nome do usuário do banco de dados
    'password': '',            # Senha do usuário
    'database': 'tabela_escola', # Nome do banco de dados utilizado
}

# Tela Inicial
@app.route('/')
def login_professor():
    # Página de login do professor
    return render_template("AcessoProfessor.html")

# Processamento dos dados de login do professor
@app.route('/login_professor', methods=['POST'])
def processar_login_professor():
    # Dados do Formulário de Login
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')

    # Teste
    if usuario == 'professor' and senha == 'abc123':
        return render_template('professor_tela1.html')
    else:
        flash('Usuário ou senha inválido, por favor tente novamente.')
        return redirect('/')

# Exibe o cadastro de professor
@app.route('/adicionar_professor', methods=['GET'])
def adicionar_professor():
    # HTML do formulário de cadastro de professor
    return render_template("cadastro_professor.html")

# Debug
if __name__ == "__main__": 
    app.run(debug=True)
