import os
import sqlite3
from random import randint

from flask import Flask, render_template, request, redirect, session, send_from_directory

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'documents'
DATABASE = 'documents.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    if 'username' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents")
        documents = cursor.fetchall()
        print(documents)
        conn.close()
        return render_template('index.html', documents=documents)
    else:
        return redirect('/login')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        file = request.files['file']  # Получаем файл из запроса
        filename = file.filename  # Получаем имя файла
        if not os.path.exists(f'documents/{session["username"]}'):
            os.mkdir(f'documents/{session["username"]}')
        filepath = os.path.join(f'documents/{session["username"]}', filename)  # Путь к сохраняемому файлу
        file.save(filepath)  # Сохраняем файл на сервере

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE title = ? AND creator = ?", (title, session['username']))
        existing_document = cursor.fetchone()
        if existing_document:
            error = 'Вы уже загрузили документ с такими же данными'
            return render_template('upload.html', error=error)
        cursor.execute("INSERT INTO documents (title, file_path, creator) VALUES (?, ?, ?)",
                       (title, filepath, session['username']))
        conn.commit()
        conn.close()

        return redirect('/')
    return render_template('upload.html')


@app.route('/download/<int:document_id>')
def download(document_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM documents WHERE id = ?", (document_id,))
    filepath = cursor.fetchone()[0]
    conn.close()
    directory, filename = os.path.split(filepath)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/delete/<int:document_id>', methods=['POST'])
def delete(document_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM documents WHERE id = ?", (document_id,))
    os.remove(cursor.fetchone()[0])
    cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            error = 'Пользователь с таким именем уже существует'
            return render_template('register.html', error=error)
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            session['username'] = username
            return redirect('/')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect('/')
        else:
            error = 'Неверное имя пользователя или пароль'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)

