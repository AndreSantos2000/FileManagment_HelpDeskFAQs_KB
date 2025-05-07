from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import sqlite3
import io

app = Flask(__name__)
CORS(app)
DB_FILE = 'my_files.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data BLOB
            )
        ''')

@app.route('/')
def home():
    return render_template('HelpDeskFAQs_DataManage.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    data = file.read()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO files (name, data) VALUES (?, ?)", (file.filename, data))
    return 'File uploaded', 200

@app.route('/files', methods=['GET'])
def list_files():
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute("SELECT id, name FROM files").fetchall()
    return rows

@app.route('/file/<int:file_id>', methods=['GET'])
def get_file(file_id):
    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute("SELECT name, data FROM files WHERE id = ?", (file_id,)).fetchone()
    if row:
        name, data = row
        return send_file(io.BytesIO(data), download_name=name, as_attachment=True)
    return 'File not found', 404

@app.route('/text/<int:file_id>', methods=['GET'])
def get_text_content(file_id):
    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute("SELECT name, data FROM files WHERE id = ?", (file_id,)).fetchone()
    if row:
        try:
            text = row[1].decode("utf-8")
            return text, 200
        except UnicodeDecodeError:
            return "Not a text file", 400
    return "File not found", 404

@app.route('/delete/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
        if cur.rowcount > 0:
            return "Deleted", 200
        else:
            return "Not found", 404

if __name__ == '__main__':
    init_db()
    app.run(host='10.201.132.150', port=5000)