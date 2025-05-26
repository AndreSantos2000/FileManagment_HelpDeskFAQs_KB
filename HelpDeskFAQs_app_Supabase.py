import os
from flask import Flask, request, render_template, redirect, jsonify, send_file
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy
from supabase import create_client, Client
from werkzeug.utils import secure_filename
import fitz #PyMuPDF
#from dotenv import load_dotenv
import csv
from llm_utils import AI_interaction  # import your helper
from openai import OpenAI
#load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Supabase init
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

#OpenAi init
#client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
client = OpenAI(base_url="http://10.14.208.198:1234", api_key="lm-studio")

class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    type_id = db.Column(db.Integer)
    type_desc = db.Column(db.String(255))
    master_type_id = db.Column(db.Integer)
    master_type_desc = db.Column(db.String(255))
    mime_type = db.Column(db.String(255))
    filepath = db.Column(db.String(300))

class Type(db.Model):
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    #created_at = db.Column(db.timestamptz(255), nullable=False)
    Master_type_id = db.Column(db.String(255), nullable=False)


# Parse CSV into a list of dicts at app start
TYPE_DATA = []
with open("CSVs/type_rows.csv", newline="") as f:
    reader = csv.DictReader(f)
    TYPE_DATA = [row for row in reader]

#@app.route("/viewPage")
@app.route("/")
def view_page():
    files = File.query.all()
    content_list = []
    for file in files:
        type_record = Type.query.get_or_404(file.type_id) if file.type_id else ""
        folder = type_record.description.replace("::", "/") if type_record else ""
        folder = folder.strip("?")
        storage_path = f"{folder}/{file.filename}" if folder else file.filename
        #type_row = next((row for row in TYPE_DATA if row["id"] == file.type_id), None)
        #folder_path = type_row["description"].replace("::", "/") if type_row else ""
        #storage_path = f"{folder_path}/{file.filename}" if folder_path else file.filename
        #print("storage path: ", storage_path)
        if file.filename:
        #    if not file.filename.lower().endswith(".pdf"):
        #        continue
            try:
                # Download file from Supabase bucket
                #response = supabase.storage.from_("faqfiles").download(file.filepath)
                response = supabase.storage.from_("faqfiles").download(storage_path)
                pdf_bytes = response  # This is bytes

                # Use PyMuPDF to extract text
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                text = "\n".join([page.get_text() for page in doc])
                doc.close()

                content_list.append({
                    "id": file.id,
                    "filename": file.filename,
                    "text": text
                })
            except Exception as e:
                content_list.append({
                    "filename": file.filename,
                    "text": f"Error loading file: {str(e)}"
                })

    return render_template("HelpDeskFAQs_viewer.html", files=content_list)

@app.route("/managePage")
def index():
    files = File.query.all()
    return render_template("HelpDeskFAQs_manager.html", files=files, types=TYPE_DATA)

@app.route("/chat")
def chat():
    return render_template("HelpDeskFAQs_chat.html")

#@app.route("/viewPage")
#def view_page():
#    files = File.query.all()
#    return render_template("HelpDeskFAQs_viewer.html", files=files)

@app.route("/")
def view_aplication_page():
    files = File.query.all()
    content_list = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
        
        try:
            # Download file from Supabase bucket
            response = supabase.storage.from_("faqfiles/Aplicacoes").download(file.filepath)
            pdf_bytes = response  # This is bytes

            # Use PyMuPDF to extract text
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = "\n".join([page.get_text() for page in doc])
            doc.close()

            content_list.append({
                "id": file.id,
                "filename": file.filename,
                "text": text
            })
        except Exception as e:
            content_list.append({
                "filename": file.filename,
                "text": f"Error loading file: {str(e)}"
            })

    return render_template("HelpDeskFAQs_viewer.html", files=content_list)


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files.get("file")
    type_id = request.form.get("type_id")

    if not uploaded_file:
        return "Missing file", 400

    filename = secure_filename(uploaded_file.filename)
    file_bytes = uploaded_file.read()

    # Default: no folder
    folder = ""

    # If type_id is given, map it to folder path
    if type_id:
        type_row = next((row for row in TYPE_DATA if str(row["id"]) == str(type_id)), None)
        if not type_row:
            return "Invalid type_id", 400
        type_desc = type_row["description"]
        folder = type_desc.replace("::", "/").strip("/")  # e.g., E-mail/Mailbox
        folder = folder.strip("?")

    # Build final storage path
    storage_path = f"{folder}/{filename}" if folder else filename
    # Upload to Supabase Storage
    supabase.storage.from_("faqfiles").upload(
        storage_path,
        file_bytes,
        {"content-type": uploaded_file.mimetype}
    )

    # Save metadata to database
    new_file = File(
        type_id=type_row["id"],
        type_desc=type_row["description"],
        filename=filename,
        filepath=filename
    )
    db.session.add(new_file)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully."}), 200


@app.route("/files", methods=["GET"])
def list_files():
    files = File.query.all()
    #return jsonify([{"id": f.id, "filename": f.filename, "type_desc": f.type_desc, "master_type_desc": f.master_type_desc} for f in files])
    result = []
    for f in files:
        type_entry = Type.query.get(f.type_id)
        master_entry = Type.query.get(type_entry.Master_type_id) if type_entry.Master_type_id else ""
        result.append({
            "id": f.id,
            "filename": f.filename,
            "type_id": f.type_id,
            "type_desc": type_entry.description if type_entry else "",
            "master_type_desc": master_entry.description if master_entry else ""
        })
    return jsonify(result)


@app.route("/download/<int:file_id>", methods=["GET"])
def download(file_id):
    file_record = File.query.get_or_404(file_id)
    type_record = Type.query.get_or_404(file_record.type_id) if file_record.type_id else ""
    folder = type_record.description.replace("::", "/") if type_record.id else ""
    folder = folder.strip("?")
    storage_path = f"{folder}/{file_record.filename}" if folder else file_record.filename
    # Ensure the storage path is correct (e.g., uploads/filename.txt)
    #storage_path = file_record.filepath

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
    file_record = File.query.get_or_404(file_id)
    type_record = Type.query.get_or_404(file_record.type_id) if file_record.type_id else ""
    folder = type_record.description.replace("::", "/") if type_record.description else ""
    folder = folder.strip("?")
    ######
    storage_path = f"{folder}/{file_record.filename}" if folder else file_record.filename
    if storage_path:
        supabase.storage.from_(SUPABASE_BUCKET).remove([storage_path])
        db.session.delete(file_record)
        db.session.commit()
    return jsonify({"message": f"File {file_id} deleted successfully."}), 200


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        user_question = data.get("question", "")

        response = client.chat.completions.create(
            model="granite-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_question}
            ]
        )

        return jsonify({"answer": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
