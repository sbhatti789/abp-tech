# app.py

from flask import Flask, request, render_template, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from src.db import get_connection
from src.query_sql import query_system
from src.ingest_documents import ingest_document_file

app = Flask(__name__)
app.secret_key = "supersecretkey123"   

# ------------------------------
# Upload settings
# ------------------------------
UPLOAD_FOLDER = "data/documents"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"txt"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------------------
# HOME
# ------------------------------
@app.route("/")
def home():
    return redirect("/login")


# ------------------------------
# SIGNUP
# ------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        role = request.form["role"]

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
                """,
                (username, generate_password_hash(password), role),
            )
            conn.commit()
            return render_template("signup.html", message="Account created! You can now log in.")
        except Exception:
            conn.rollback()
            return render_template("signup.html", message="Username already exists.")
        finally:
            cur.close()
            conn.close()

    return render_template("signup.html")


# ------------------------------
# LOGIN
# ------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, password_hash, role FROM users WHERE username = %s",
            (username,),
        )
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            session["role"] = user[2]
            return redirect("/dashboard")

        return render_template("login.html", message="Invalid credentials.")

    return render_template("login.html")


# ------------------------------
# LOGOUT
# ------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ------------------------------
# DASHBOARD (ROLE-BASED)
# ------------------------------
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    role = session["role"]

    if role == "admin":
        return render_template("admin_dashboard.html", username=session["username"])
    elif role == "curator":
        return render_template("curator_dashboard.html", username=session["username"])
    else:
        return render_template("user_dashboard.html", username=session["username"])


# ------------------------------
# ADMIN: VIEW USERS
# ------------------------------
@app.route("/users")
def users():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, username, role, created_at
        FROM users
        ORDER BY id ASC;
        """
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("users.html", users=rows)


# ------------------------------
# ADMIN: EDIT USER ROLE
# ------------------------------
@app.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return redirect("/users")

    if request.method == "POST":
        new_role = request.form["role"]
        cur.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/users")

    cur.close()
    conn.close()
    return render_template("edit_user.html", user=user)


# ------------------------------
# ADMIN: DELETE USER + ASSOCIATED DATA
# ------------------------------
@app.route("/users/delete/<int:user_id>")
def delete_user(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM documents WHERE uploader_user_id = %s", (user_id,))
    doc_ids = [row[0] for row in cur.fetchall()]

    if doc_ids:
        doc_ids_tuple = tuple(doc_ids)
        cur.execute("DELETE FROM chunks WHERE document_id IN %s", (doc_ids_tuple,))
        cur.execute("DELETE FROM documents WHERE id IN %s", (doc_ids_tuple,))

    cur.execute("DELETE FROM query_logs WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/logout")


# ------------------------------
# SEARCH + LOGGING
# ------------------------------
@app.route("/search", methods=["GET", "POST"])
def search():
    if "user_id" not in session:
        return redirect("/login")

    results = []
    query = None

    if request.method == "POST":
        query = request.form["query"]

        results = query_system(query)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO query_logs (user_id, query_text) VALUES (%s, %s)",
            (session["user_id"], query),
        )
        conn.commit()
        cur.close()
        conn.close()

    return render_template("search.html", results=results, query=query)


# ------------------------------
# ADMIN: QUERY LOGS 
# ------------------------------
@app.route("/query_logs")
def query_logs():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT q.id,
               COALESCE(u.username, 'Anonymous') AS username,
               q.query_text,
               q.timestamp        -- FIXED THIS LINE
        FROM query_logs q
        LEFT JOIN users u ON q.user_id = u.id
        ORDER BY q.id ASC;
        """
    )
    logs = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("query_logs.html", logs=logs)


# ------------------------------
# CURATOR/ADMIN: UPLOAD DOCUMENT
# ------------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    # Allow curator and admin
    if "user_id" not in session or session.get("role") not in ["curator", "admin"]:
        return redirect("/dashboard")

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            return render_template("upload.html", message="No file selected.")

        if not allowed_file(file.filename):
            return render_template("upload.html", message="Only .txt files allowed.")

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        try:
            ingest_document_file(save_path, uploader_user_id=session["user_id"])
            return render_template("upload.html", message="Document uploaded and indexed.")
        except Exception as e:
            return render_template("upload.html", message=f"Error: {e}")

    return render_template("upload.html")


# ------------------------------
# VIEW FULL DOCUMENT
# ------------------------------
@app.route("/document/<filename>")
def view_document(filename):
    if "user_id" not in session:
        return redirect("/login")

    highlighted_chunk = request.args.get("chunk")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT chunk_text
        FROM chunks
        JOIN documents ON chunks.document_id = documents.id
        WHERE documents.filename = %s
        ORDER BY chunks.id ASC;
        """,
        (filename,)
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    full_text = "\n\n".join(chunk[0] for chunk in rows)

    if highlighted_chunk:
        safe_chunk = highlighted_chunk.replace("<", "&lt;").replace(">", "&gt;")
        full_text = full_text.replace(
            highlighted_chunk,
            f"<mark style='background: yellow'>{safe_chunk}</mark>"
        )

    return render_template("document.html", filename=filename, full_text=full_text)


# ------------------------------
# ADMIN: MANAGE DOCUMENTS
# ------------------------------
@app.route("/documents")
def documents():
    if "user_id" not in session:
        return redirect("/login")

    # Allow admin AND curator
    if session.get("role") not in ["admin", "curator"]:
        return redirect("/dashboard")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT d.id,
               d.filename,
               d.uploaded_at,
               COALESCE(u.username, 'Unknown') AS uploaded_by
        FROM documents d
        LEFT JOIN users u ON d.uploader_user_id = u.id
        ORDER BY d.id ASC;
        """
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("documents.html", documents=rows)


# ------------------------------
# ADMIN: DELETE DOCUMENT
# ------------------------------
@app.route("/documents/delete/<int:doc_id>")
def delete_document(doc_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM chunks WHERE document_id = %s", (doc_id,))
    cur.execute("DELETE FROM documents WHERE id = %s", (doc_id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/documents")


# ------------------------------
# RUN APP
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
