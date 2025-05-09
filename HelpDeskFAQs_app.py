import os
from flask import Flask, request, jsonify, send_file, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Database config: PostgreSQL for production, fallback to SQLite locally
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///my_files.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# File model
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(300), nullable=False)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("HelpDeskFAQs_manager.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    db_entry = File(filename=filename, filepath=filepath)
    db.session.add(db_entry)
    db.session.commit()

    return jsonify({"message": "Upload successful"})

@app.route("/files", methods=["GET"])
def list_files():
    files = File.query.all()
    return jsonify([{"id": f.id, "name": f.filename} for f in files])

@app.route("/download/<int:file_id>")
def download(file_id):
    file = File.query.get_or_404(file_id)
    return send_file(file.filepath, as_attachment=True)

@app.route("/delete/<int:file_id>", methods=["DELETE"])
def delete(file_id):
    file = File.query.get_or_404(file_id)
    try:
        os.remove(file.filepath)
    except FileNotFoundError:
        pass
    db.session.delete(file)
    db.session.commit()
    return jsonify({"message": "File deleted"})

@app.route("/view/<int:file_id>")
def view(file_id):
    file = File.query.get_or_404(file_id)
    if not file.filename.lower().endswith(".txt"):
        return jsonify({"error": "Only .txt files can be viewed"}), 400
    try:
        with open(file.filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"filename": file.filename, "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
