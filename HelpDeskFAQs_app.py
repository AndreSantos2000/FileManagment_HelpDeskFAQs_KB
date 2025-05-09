import os
from flask import Flask, request, jsonify, send_file, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure database (PostgreSQL in production, fallback to SQLite locally)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///my_files.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# File model
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(300), nullable=False)

# Ensure upload directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#@app._got_first_request
#def create_tables():
#    db.create_all()

@app.route("/")
def index():
    #return render_template("index.html")
    return render_template("HelpDeskFAQs_DataManage.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    new_file = File(filename=filename, filepath=filepath)
    db.session.add(new_file)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully."})

@app.route("/files", methods=["GET"])
def list_files():
    files = File.query.all()
    return jsonify([{"id": f.id, "name": f.filename} for f in files])

@app.route("/download/<int:file_id>", methods=["GET"])
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
    return jsonify({"message": "File deleted."})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)