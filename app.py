from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

# 🔐 SECRET KEY (IMPORTANT for login session)
app.secret_key = "organ_donation_secret"

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect("donors.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            blood TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["user"] = username
            return redirect("/")

        return "Invalid credentials"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------- HOME ----------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        blood = request.form["blood"]

        conn = sqlite3.connect("donors.db")
        c = conn.cursor()
        c.execute("INSERT INTO donors (name, age, blood) VALUES (?, ?, ?)",
                  (name, age, blood))
        conn.commit()
        conn.close()

        return redirect("/donors")

    return render_template("register.html")

# ---------- DONORS ----------
@app.route("/donors")
def donors():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("donors.db")
    c = conn.cursor()
    c.execute("SELECT * FROM donors")
    donors_list = c.fetchall()
    conn.close()

    return render_template("donors.html", donors=donors_list)

# ---------- DELETE ----------
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("donors.db")
    c = conn.cursor()
    c.execute("DELETE FROM donors WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/donors")

# ---------- SEARCH ----------
@app.route("/search", methods=["GET", "POST"])
def search():
    if "user" not in session:
        return redirect("/login")

    results = []

    if request.method == "POST":
        blood = request.form["blood"]

        conn = sqlite3.connect("donors.db")
        c = conn.cursor()
        c.execute("SELECT * FROM donors WHERE blood=?", (blood,))
        results = c.fetchall()
        conn.close()

    return render_template("search.html", donors=results)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)