import sqlite3

def print_all_rows():
    conn = sqlite3.connect("my_files.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM files")
    rows = cursor.fetchall()

    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}")

    conn.close()


def insert_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    name = file_path.split("/")[-1]

    conn = sqlite3.connect("my_files.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (name, data) VALUES (?, ?)", (name, data))
    conn.commit()
    conn.close()


def delete_file_by_id(file_id):
    conn = sqlite3.connect("my_files.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
    conn.commit()

    if cursor.rowcount > 0:
        print(f"Deleted file with ID {file_id}")
    else:
        print(f"No file found with ID {file_id}")

    conn.close()


def retrieve_file(file_id, output_path):
    conn = sqlite3.connect("my_files.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, data FROM files WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        with open(output_path+ str(file_id) + ".pdf", "wb") as f:
            f.write(row[1])
        print(f"File saved as: {output_path + str(file_id) + ".pdf"}")
    else:
        print("File not found")


def print_file_content(file_id):
    conn = sqlite3.connect("my_files.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, data FROM files WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        file_name, file_data = row
        try:
            # Decode binary as UTF-8 text (works for .txt, .csv, .json, etc.)
            text = file_data.decode("utf-8")
            print(f"--- Content of '{file_name}' ---")
            print(text)
        except UnicodeDecodeError:
            print(f"File '{file_name}' is not a text file or has unsupported encoding.")
    else:
        print("No file found with that ID.")



file_path = "C:/Users/ext.andre.santos/Documents/Trabalho/HelpDeskFAQ_datafiles/FAQs2.pdf"
file_path2 = "C:/Users/ext.andre.santos/Documents/Trabalho/HelpDeskFAQ_datafiles/FAQs2.txt"
output_path = "HelpDesk_outputFiles/FAQs_OutputFile"

#insert_file(file_path2)
print_all_rows()
print_file_content(2)
print_file_content(3)
#retrieve_file(2, output_path)

#delete_file_by_id(2)