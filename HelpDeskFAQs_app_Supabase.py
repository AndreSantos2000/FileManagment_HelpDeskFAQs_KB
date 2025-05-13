import os
from flask import Flask, request, render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Supabase init
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    content_type = db.Column(db.String(255))


@app.route("/")
def index():
    files = File.query.all()
    return render_template("HelpDeskFAQs_manager.html", files=files)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    if file:
        filepath = f"{file.filename}"
        # Upload to Supabase
        supabase.storage.from_(SUPABASE_BUCKET).upload(filepath, file.stream)
        # Save metadata
        new_file = File(filename=file.filename, content_type=file.content_type)
        db.session.add(new_file)
        db.session.commit()
    return redirect("/")


@app.route("/download/<int:file_id>")
def download(file_id):
    file = File.query.get(file_id)
    if not file:
        return "File not found", 404
    # Generate signed URL (valid 1 hour)
    res = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(file.filename, 3600)
    return redirect(res['signedURL'])


@app.route("/view/<int:file_id>")
def view(file_id):
    file = File.query.get(file_id)
    if not file or not file.filename.endswith(".txt"):
        return "Not a viewable .txt file", 400
    # Download the file content
    res = supabase.storage.from_(SUPABASE_BUCKET).download(file.filename)
    content = res.decode("utf-8")
    return jsonify({"content": content})


@app.route("/delete/<int:file_id>", methods=["POST"])
def delete(file_id):
    file = File.query.get(file_id)
    if file:
        supabase.storage.from_(SUPABASE_BUCKET).remove([file.filename])
        db.session.delete(file)
        db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
