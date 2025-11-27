from flask import Flask, request, render_template, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from src.db import get_connection
from src.query_sql import query_system
from src.ingest_documents import ingest_document_file

app = Flask(__name__)
app.secret_key = "supersecretkey123"   # Change later if needed

# Upload settings
UPLOAD_FOLDER = "data/documents"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"txt"}


def allowed_file(filename):
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
        username = request.form["username"]
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
                (username, generate_password_hash(password), role)
            )
            conn.commit()
            message = "✅ Account created! You can now log in."
            return render_template("signup.html", message=message)
        except:
            conn.rollback()
            message = "❌ Username already exists. Try another."
            return render_template("signup.html", message=message)
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
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, password_hash, role FROM users WHERE username=%s",
            (username,)
        )
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            session["role"] = user[2]
            return redirect("/dashboard")

        return render_template("login.html", message="❌ Invalid credentials.")

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
    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") == "admin":
        return render_template("admin_dashboard.html", username=session["username"])
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
    cur.execute("SELECT id, username, role, created_at FROM users ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("users.html", users=rows)


# ------------------------------
# SEARCH PAGE (VECTOR + LOGGING ✅)
# ------------------------------
@app.route("/search", methods=["GET", "POST"])
def search():
    if "user_id" not in session:
        return redirect("/login")

    results = []
    query = None

    if request.method == "POST":
        query = request.form["query"]

        # ✅ Run vector search
        results = query_system(query)

        # ✅ Log query
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO query_logs (user_id, query_text) VALUES (%s, %s)",
            (session["user_id"], query)
        )
        conn.commit()
        cur.close()
        conn.close()

    return render_template("search.html", results=results, query=query)


# ------------------------------
# CURATOR/ADMIN: UPLOAD DOCUMENT
# ------------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session or session.get("role") not in ["curator", "admin"]:
        return redirect("/dashboard")

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            return render_template("upload.html", message="❌ No file selected.")

        if not allowed_file(file.filename):
            return render_template("upload.html", message="❌ Only .txt files allowed.")

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        try:
            ingest_document_file(save_path, uploader_user_id=session["user_id"])
            return render_template("upload.html", message="✅ Document uploaded and indexed!")
        except Exception as e:
            return render_template("upload.html", message=f"❌ Error: {e}")

    return render_template("upload.html")


# ------------------------------
# VIEW FULL DOCUMENT
# ------------------------------
@app.route("/document/<filename>")
def view_document(filename):
    if "user_id" not in session:
        return redirect("/login")

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

    return render_template("document.html", filename=filename, full_text=full_text)


# ------------------------------
# MANAGE DOCUMENTS (ADMIN ONLY)
# ------------------------------
@app.route("/documents")
def documents():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, filename, uploaded_at
        FROM documents
        ORDER BY id ASC;
        """
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("documents.html", documents=rows)


# ------------------------------
# DELETE DOCUMENT
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
