from flask import Flask, render_template, redirect, request, flash, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'EXTENCAO'

# Configuração do banco de dados MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Substitua pela senha do seu banco de dados
    'database': 'tabela_escola',
}

# Função para obter a conexão com o banco de dados
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        flash(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Tela de login do diretor
@app.route('/')
def login():
    return render_template("AcessoDiretor.html")

# Rota para processar o login do diretor
@app.route('/login_diretor', methods=['POST'])
def login_diretor():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    
    if usuario == 'diretor' and senha == '123':  # Substitua por um sistema seguro em produção
        alunos = alunos_cadastrados()
        return render_template('diretor_tela1.html', alunos=alunos)
    else:
        flash('Usuário ou senha inválidos, por favor tente novamente.')
        return redirect('/')

# Rota para adicionar aluno
@app.route('/adicionar_aluno', methods=['POST'])
def adicionar_aluno():
    return render_template("adicionar_pfs_aln.html")

# Rota para adicionar professor
@app.route('/adicionar_professor', methods=['POST'])
def adicionar_professor():
    alunos = alunos_cadastrados()
    return render_template("cadastro_professor.html", alunos=alunos)

# Rota para deletar ou editar
@app.route('/deletar_editar', methods=['POST'])
def deletar_editar():
    alunos = alunos_cadastrados()
    professores=professor_cadastrados()
    return render_template("deletar_editar.html", alunos=alunos,professores=professores)

# Rota para atribuição de professor
@app.route('/atri_professor', methods=['POST'])
def atri_professor():
    professores=professor_cadastrados()
    return render_template("buscar_professor.html",professores=professores)

# Cadastro de professor
@app.route('/cadastro_prof', methods=['POST'])
def cadastro_profe():
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados"
    
    cursor = conn.cursor()
    try:
        # Coletando os dados do formulário
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        numero = request.form.get('numero')
        email = request.form.get('email')
        idade = request.form.get('idade')
        senha = request.form.get('senha')

        # Inserindo os dados na tabela PROFESSOR
        cursor.execute(
            "INSERT INTO PROFESSOR (nome, cpf, numero, email, idade, senha) "
            "VALUES (%s, %s, %s, %s, %s, %s)", 
            (nome, cpf, numero, email, idade, senha)
        )
        conn.commit()
        return "Professor cadastrado com sucesso"

    except Error as e:
        return f"Erro ao conectar ao banco de dados: {e}"

    finally:
        cursor.close()
        conn.close()

# Função para pegar alunos já cadastrados
def alunos_cadastrados():
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ALUNO")
    alunos = cursor.fetchall()
    cursor.close()
    conn.close()
    return alunos

# Função para pegar professores já cadastrados
def professor_cadastrados():
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PROFESSOR")
    professores = cursor.fetchall()
    cursor.close()
    conn.close()
    return professores

# Cadastro de aluno
@app.route("/cadastro_alun", methods=['POST'])
def cadastrar_aluno():
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados"
    
    cursor = conn.cursor()
    try:
        # Coletando dados do formulário
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        turma = request.form.get('turma')
        numero = request.form.get('numero')
        data_nascimento = request.form.get('data_d_nasc')
        responsavel = request.form.get('responsavel')
        cpf_resp = request.form.get('cpf_respon')
        ano = request.form.get('ano')
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Validação básica de CPF e número de telefone
        if len(cpf) != 11 or not cpf.isdigit():
            return "Erro: O CPF deve conter 11 dígitos."
        if len(numero) < 8 or len(numero) > 14:
            return "Erro: O número de telefone deve conter entre 8 e 14 dígitos."

        # Inserindo os dados na tabela ALUNO
        cursor.execute(
            "INSERT INTO ALUNO (nome, cpf, turma, numero, data_nascimento, responsavel, cpf_respon, senha, email, ano_serie) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (nome, cpf, turma, numero, data_nascimento, responsavel, cpf_resp, senha, email, ano)
        )

        # Inserindo matérias padrões para o aluno
        materias = ["portugues", "matematica", "ingles", "fisica"]
        prova1, prova2, nota_final = 0, 0, 0

        for materia in materias:
            cursor.execute(
                "INSERT INTO MATERIAS (matricula, ano, materia, prova1, prova2, nota_final) "
                "VALUES (LAST_INSERT_ID(), %s, %s, %s, %s, %s)",
                (ano, materia, prova1, prova2, nota_final)
            )

        conn.commit()
        return "Aluno cadastrado com sucesso"

    except Error as e:
        return f"Erro ao conectar ao banco de dados: {e}"

    finally:
        cursor.close()
        conn.close()

# Rota de resposta para busca de aluno
@app.route('/resposta_al', methods=['POST'])
def resposta_al():
    termo = request.form['barraPesquisa']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query_aluno = """
    SELECT * FROM aluno WHERE matricula LIKE %s 
    OR nome LIKE %s OR ano_serie LIKE %s
    """
    cursor.execute(query_aluno, (f"%{termo}%", f"%{termo}%", f"%{termo}%"))
    res_aluno = cursor.fetchall()
    
    professores = professor_cadastrados()
    alunos = alunos_cadastrados()
    
    cursor.close()
    conn.close()
    
    return render_template('diretor_tela1.html', res_aluno=res_aluno, alunos=alunos,professores=professores)

# Rota de resposta para busca de professor
@app.route('/resposta_professor', methods=['POST'])
def resposta_professor():
    termo = request.form['barraPesquisa']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query_professor = """
    SELECT * FROM PROFESSOR WHERE matricula LIKE %s 
    OR nome LIKE %s
    """
    cursor.execute(query_professor, (f"%{termo}%", f"%{termo}%"))
    res_professor = cursor.fetchall()
    
    professores = professor_cadastrados()
    alunos = alunos_cadastrados()
    cursor.close()
    conn.close()
    
    return render_template('deletar_editar.html', res_professor=res_professor, professores=professores,alunos=alunos)

# Rota de atualização de professor
@app.route('/alterar_professor', methods=['POST'])
def alterar_prof():
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados"
    
    cursor = conn.cursor()
    try:
        # Coletando os dados do formulário
        matricula = request.form.get('matricula')
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        numero = request.form.get('numero')
        email = request.form.get('email')
        idade = request.form.get('idade')
        senha = request.form.get('senha')

        # Atualizando os dados na tabela PROFESSOR
        cursor.execute(
            "UPDATE PROFESSOR SET nome=%s, cpf=%s, numero=%s, email=%s, idade=%s, senha=%s "
            "WHERE matricula=%s", 
            (nome, cpf, numero, email, idade, senha, matricula)
        )
        conn.commit()
        return "Professor editado com sucesso"

    except Error as e:
        return f"Erro ao atualizar os dados: {e}"

    finally:
        cursor.close()
        conn.close()
        
# Função para deletar um professor
@app.route('/deletar_professor', methods=['POST'])
def deletar_professor():
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados"
    
    cursor = conn.cursor()
    try:
        matricula = request.form.get('matricula')

        # Exclui o professor com a matrícula correspondente
        cursor.execute("DELETE FROM PROFESSOR WHERE matricula = %s", (matricula,))
        conn.commit()
        return "Professor deletado com sucesso"

    except Error as e:
        return f"Erro ao deletar o professor: {e}"

    finally:
        cursor.close()
        conn.close()        
        
@app.route('/resposta_aluno', methods=['POST'])
def resposta_aluno():
    termo = request.form['barraPesqui']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query_professor = """
    SELECT * FROM ALUNO WHERE matricula LIKE %s 
    OR nome LIKE %s
    """
    cursor.execute(query_professor, (f"%{termo}%", f"%{termo}%"))
    res_aluno = cursor.fetchall()
    
    professores = professor_cadastrados()
    alunos = alunos_cadastrados()
    cursor.close()
    conn.close()
    
    return render_template('deletar_editar.html', res_aluno=res_aluno, professores=professores,alunos=alunos)

# Rota de atualização de aluno
@app.route('/alterar_aluno', methods=['POST'])
def alterar_aluno():
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados"
    
    cursor = conn.cursor()
    try:
        # Coletando os dados do formulário
        matricula = request.form.get('matricula')
        ano = request.form.get('ano_serie')
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        turma = request.form.get('turma')
        email = request.form.get('email')

        # Atualizando os dados na tabela ALUNO
        cursor.execute(
            "UPDATE ALUNO SET nome=%s, cpf=%s, ano_serie=%s, email=%s, turma=%s "
            "WHERE matricula=%s", 
            (nome, cpf, ano, email, turma, matricula)
        )
        conn.commit()
        return "Aluno editado com sucesso"

    except Error as e:
        return f"Erro ao atualizar os dados: {e}"

    finally:
        cursor.close()
        conn.close()
        
# Função para deletar um aluno
@app.route('/deletar_aluno', methods=['POST'])
def deletar_aluno():
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados"
    
    cursor = conn.cursor()
    try:
        matricula = request.form.get('matricula')

        # Exclui o aluno com a matrícula correspondente
        cursor.execute("DELETE FROM ALUNO WHERE matricula = %s", (matricula,))
        conn.commit()
        return "Aluno deletado com sucesso"

    except Error as e:
        return f"Erro ao deletar o aluno: {e}"

    finally:
        cursor.close()
        conn.close()  
        
@app.route('/materia_prof', methods=['POST'])
def materia_prof():
    termo = request.form['barraPesquisa']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query_professor = """
    SELECT * FROM PROFESSOR WHERE matricula LIKE %s 
    OR nome LIKE %s
    """
    cursor.execute(query_professor, (f"%{termo}%", f"%{termo}%"))
    res_professor = cursor.fetchall()
    
    professores = professor_cadastrados()
    cursor.close()
    conn.close()
    
    return render_template('buscar_professor.html', res_professor=res_professor, professores=professores)

# Cadastro de professor a sua materia
@app.route('/atribuir_materia', methods=['POST'])
def atribuir_materia():
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados"
    
    cursor = conn.cursor()
    try:
        # Coletando os dados do formulário
        matricula = request.form.get('matricula')
        ano_serie = request.form.get('ano')
        horario = request.form.get('horario')
        materia = request.form.get('materia')

        # Inserindo os dados na tabela PROFESSOR
        cursor.execute(
            "INSERT INTO MATERIAS_PROFESSOR (matricula, ano_serie, horario, materia) "
            "VALUES (%s, %s, %s, %s)", 
            (matricula, ano_serie, horario, materia)
        )
        conn.commit()
        return "Professor cadastrado a sua materia com sucesso"

    except Error as e:
        return f"Erro ao conectar ao banco de dados: {e}"

    finally:
        cursor.close()
        conn.close()              

if __name__ == "__main__":
    app.run(debug=True)
