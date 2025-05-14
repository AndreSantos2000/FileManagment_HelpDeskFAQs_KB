import os
from flask import Flask, request, render_template, redirect, jsonify, send_file
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy
from supabase import create_client, Client
from werkzeug.utils import secure_filename
#from dotenv import load_dotenv

#load_dotenv()

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
    type_id = db.Column(db.Integer)
    type_desc = db.Column(db.String(255))
    master_type_id = db.Column(db.Integer)
    master_type_desc = db.Column(db.String(255))
    mime_type = db.Column(db.String(255))
    filepath = db.Column(db.String(300))


@app.route("/")
def index():
    files = File.query.all()
    return render_template("HelpDeskFAQs_manager.html", files=files)

@app.route("/viewPage")
def view_page():
    files = File.query.all()
    return render_template("HelpDeskFAQs_viewer.html", files=files)


@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file provided"}), 400

        filename = secure_filename(file.filename)
        #storage_path = f"uploads/{filename}"

        file_data = file.read()
        if len(file_data) == 0:
            return jsonify({"error": "Uploaded file is empty"}), 400

        # Upload to Supabase Storage
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(
            filename, file_data, {"content-type": file.content_type}
        )
        print("Supabase upload response:", res)

        # Save metadata to database
        new_file = File(
            type_id=0,
            type_desc="aplicações",
            filename=filename,
            filepath=filename
        )
        db.session.add(new_file)
        db.session.commit()

        return jsonify({"message": "File uploaded successfully."}), 200

    except Exception as e:
        print("Upload error:", e)  # <--- this helps!
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route("/files", methods=["GET"])
def list_files():
    files = File.query.all()
    return jsonify([{"id": f.id, "filename": f.filename, "tema": f.type_desc, "tema_parent": f.master_type_desc} for f in files])

@app.route("/download/<int:file_id>", methods=["GET"])
def download(file_id):
    file_record = File.query.get_or_404(file_id)

    # Ensure the storage path is correct (e.g., uploads/filename.txt)
    storage_path = file_record.filepath

    try:
        # Download file content from Supabase Storage
        response = supabase.storage.from_(SUPABASE_BUCKET).download(storage_path)

        # Wrap it in BytesIO so Flask can treat it like a file
        file_stream = BytesIO(response)

        # Send the file to the client as an attachment
        return send_file(file_stream, download_name=file_record.filename, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


@app.route("/view/<int:file_id>", methods=["GET"])
def view(file_id):
    file = File.query.get(file_id)
    if not file or not file.filename.endswith(".txt"):
        return "Not a viewable .txt file", 400
    # Download the file content
    res = supabase.storage.from_(SUPABASE_BUCKET).download(file.filename)
    content = res.decode("utf-8")
    return jsonify({"content": content})


@app.route("/delete/<int:file_id>", methods=["DELETE"])
def delete(file_id):
    file = File.query.get(file_id)
    if file:
        supabase.storage.from_(SUPABASE_BUCKET).remove([file.filename])
        db.session.delete(file)
        db.session.commit()
    return jsonify({"message": f"File {file_id} deleted successfully."}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
