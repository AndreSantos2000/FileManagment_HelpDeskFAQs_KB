import os
from flask import Flask, request, jsonify, send_file, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure database (PostgreSQL in production, fallback to SQLite locally)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///my_files.db")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://postgres_myfiles_user:eAvlAnLLSQUwqmiiEZo290PkiUqa1YDN@dpg-d0ebu60dl3ps73bj9omg-a.frankfurt-postgres.render.com/postgres_myfiles")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# File model 
# New "FAQ_file" model
class FAQ_file(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tema_id = db.Column(db.Integer, nullable=False)
    tema_desc = db.Column(db.String(200))
    tema_master_id = db.Column(db.Integer)
    tema_master_desc = db.Column(db.String(200))
    nome = db.Column(db.String(200))
    ficheiro = db.Column(db.String(300))

# Ensure upload directory exists
#UPLOAD_FOLDER = "uploads"
#os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    #return render_template("index.html")
    return render_template("HelpDeskFAQs_manager.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    #filename = secure_filename(file.filename)
    filename = secure_filename(file.nome)
    #filepath = os.path.join(UPLOAD_FOLDER, filename)
    filepath = filename
    file.save(filepath)
    tema_id = 0
    tema_desc = "aplicações"
    #tema_master_id = 
    #tema_master_desc = 

    new_file = FAQ_file(tema_id = tema_id, tema_desc = tema_desc, nome=filename, ficheiro=filepath)
    db.session.add(new_file)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully."})

@app.route("/files", methods=["GET"])
def list_files():
    files = FAQ_file.query.all()
    return jsonify([{"id": f.id, "name": f.filename, "tema": f.tema_desc, "tema_parent": f.tema_master_desc} for f in files])

@app.route("/download/<int:file_id>", methods=["GET"])
def download(file_id):
    file = FAQ_file.query.get_or_404(file_id)
    return send_file(file.filepath, as_attachment=True)

@app.route("/delete/<int:file_id>", methods=["DELETE"])
def delete(file_id):
    file = FAQ_file.query.get_or_404(file_id)
    try:
        os.remove(file.filepath)
    except FileNotFoundError:
        pass
    db.session.delete(file)
    db.session.commit()
    return jsonify({"message": "File deleted."})

@app.route("/view/<int:file_id>", methods=["GET"])
def view_file(file_id):
    file = FAQ_file.query.get_or_404(file_id)
    print(file.filepath)
    if not file.filename.lower().endswith(".txt"):
        return jsonify({"error": "Only .txt files can be viewed"}), 400

    try:
        with open(file.filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"filename": file.filename, "content": content})
    except Exception as e:
        return jsonify({"error": f"Could not read file: {str(e)}"}), 500

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
