

from flask import Flask, render_template, redirect, request, flash
import mysql.connector
from mysql.connector import Error

# Criação do Flask
app = Flask(__name__)

# Chave de Protação
app.config['SECRET_KEY'] = 'EXTENCAO'

# Configuração do banco de dados MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'tabela_escola',
}

# Login: Tela Inicial
@app.route('/')
def login_professor():
    return render_template("AcessoProfessor.html")

# Processamento do login do professor
@app.route('/login_professor', methods=['POST'])
def processar_login_professor():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PROFESSOR WHERE usuario = %s AND senha = %s", (usuario, senha))
        professor = cursor.fetchone()

        if professor:
            return render_template('professor_tela1.html', professor=professor)
        else:
            flash('Usuário ou senha inválido, por favor tente novamente.')
            return redirect('/')
    except Error as e:
        flash(f"Erro ao conectar ao banco de dados: {e}")
        return redirect('/')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Formulário de modificação de perfil do professor
@app.route('/modificar_perfil', methods=['GET', 'POST'])
def modificar_perfil():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        notificacoes_linha = request.form.get('notificacoes_linha', False)
        notificacoes_email = request.form.get('notificacoes_email', False)
        notificacoes_push = request.form.get('notificacoes_push', False)
        matricula = request.form.get('matricula')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Atualiza as informações do perfil do professor no banco de dados
            cursor.execute(f"""
            UPDATE PROFESSOR
            SET nome = %s, email = %s, telefone = %s, notificacoes_linha = %s, notificacoes_email = %s, notificacoes_push = %s
            WHERE matricula = %s
            """, (nome, email, telefone, notificacoes_linha, notificacoes_email, notificacoes_push, matricula))
            
            conn.commit()

            flash('Perfil atualizado com sucesso!')
            return redirect('/modificar_perfil')
        except Error as e:
            flash(f"Erro ao atualizar o perfil: {e}")
            return redirect('/modificar_perfil')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        # Renderização o formulário de modificação de perfil
        return render_template("modificar_perfil.html")

# Exibir as turmas e matérias designadas ao professor
@app.route('/turmas_materias', methods=['GET'])
def turmas_materias():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Consulta as turmas e matérias designadas ao professor
        cursor.execute("""
        SELECT t.nome_turma, m.nome_materia, t.horario, t.plano_aula
        FROM TURMAS t
        JOIN MATERIAS m ON t.materia_id = m.id
        WHERE t.professor_id = %s
        """, (professor_id,)) 

        turmas_materias = cursor.fetchall()
        return render_template('turmas_materias.html', turmas_materias=turmas_materias)

    except Error as e:
        flash(f"Erro ao conectar ao banco de dados: {e}")
        return redirect('/')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Adicionar atividades (exercícios, testes, notas)
@app.route('/atividades', methods=['GET', 'POST'])
def atividades():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        descricao = request.form.get('descricao')
        data_entrega = request.form.get('data_entrega')
        turma_id = request.form.get('turma_id')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Inserindo nova atividade no banco de dados
            cursor.execute(f"""
            INSERT INTO ATIVIDADES (tipo, descricao, data_entrega, turma_id)
            VALUES (%s, %s, %s, %s)
            """, (tipo, descricao, data_entrega, turma_id))

            conn.commit()

            flash('Atividade adicionada com sucesso!')
            return redirect('/atividades')
        except Error as e:
            flash(f"Erro ao adicionar atividade: {e}")
            return redirect('/atividades')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        return render_template("atividades.html")

# Checar o desempenho da turma
@app.route('/desempenho_turma', methods=['GET'])
def desempenho_turma():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Consulta as notas e desempenho dos alunos
        cursor.execute("""
        SELECT a.nome, at.nota, m.nome_materia
        FROM ALUNOS a
        JOIN ATIVIDADES at ON a.id = at.aluno_id
        JOIN MATERIAS m ON at.materia_id = m.id
        WHERE at.turma_id = %s
        """, (turma_id,)) 

        desempenho = cursor.fetchall()
        return render_template('desempenho_turma.html', desempenho=desempenho)

    except Error as e:
        flash(f"Erro ao conectar ao banco de dados: {e}")
        return redirect('/')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Visualizar o calendário (com entrega de atividades)
@app.route('/calendario', methods=['GET'])
def calendario():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Consulta o calendário de atividades
        cursor.execute("""
        SELECT descricao, data_entrega
        FROM ATIVIDADES
        WHERE professor_id = %s
        """, (professor_id,)) 

        atividades = cursor.fetchall()
        return render_template('calendario.html', atividades=atividades)

    except Error as e:
        flash(f"Erro ao conectar ao banco de dados: {e}")
        return redirect('/')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)


