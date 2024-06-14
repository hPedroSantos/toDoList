from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
from dotenv import load_dotenv
import os

path_complete = 'COLOQUE AQUI O CAMINHO COMPLETO PARA A PASTA TEMPLATES!!!!'
app = Flask(__name__, template_folder=path_complete)

load_dotenv()

################################ BD CONFIG ####################################

mysql_host = os.getenv('MYSQL_HOST')
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_db = os.getenv('MYSQL_DB')

db_config = {
    'host': mysql_host,
    'user': mysql_user,
    'password': mysql_password,
    'database': mysql_db
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

################################ ROTAS ####################################

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/view_tasks')
def view_tasks():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, taskName, description, creationDateTime, deadline FROM taskList")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('view_task.html', tasks=tasks)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task_name = request.form['taskName']
        description = request.form['description']
        deadline = request.form['deadline']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO taskList (taskName, description, deadline) VALUES (%s, %s, %s)", (task_name, description, deadline))
        conn.commit()
        cur.close()
        conn.close()
        
        return render_template('task_added_success.html', new_task={'task_name': task_name, 'description': description, 'deadline': deadline})
    
    return render_template('create_task.html')

@app.route('/edit_task', methods=['GET', 'POST'])
def edit_task():
    task_id = request.args.get('task_id')
    if not task_id:
        return "ID da tarefa não fornecido", 400
    
    try:
        task_id = int(task_id)
    except ValueError:
        return "ID da tarefa inválido", 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM taskList WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if not task:
        return "Tarefa não encontrada", 404

    if request.method == 'POST':
        task_name = request.form['taskName']
        description = request.form['description']
        deadline = request.form['deadline']

        cursor.execute(
            "UPDATE taskList SET taskName = %s, description = %s, deadline = %s WHERE id = %s",
            (task_name, description, deadline, task_id)
        )
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('view_tasks'))

    cursor.close()
    conn.close()

    return render_template('update_task.html', task=task)

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM taskList WHERE id = %s', (task_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('view_tasks'))

if __name__ == '__main__':
    app.run(debug=True)
