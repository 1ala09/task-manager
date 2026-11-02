import sqlite3
from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlite3 import IntegrityError
from functools import wraps

app = Flask(__name__)
app.secret_key = "dev-secret-key"


def init_db():
    conn = sqlite3.connect("tasks.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()

tasks = []


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
@login_required
def home():
    filter_by = request.args.get("filter", "all")
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    if filter_by == "pending":
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE user_id=? AND completed=0", (session["user_id"],)
        ).fetchall()
    elif filter_by == "completed":
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE user_id=? AND completed=1", (session["user_id"],)
        ).fetchall()
    else:
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE user_id =?", (session["user_id"],)
        ).fetchall()
    total_tasks = len(tasks)
    completed_tasks = sum(task["completed"] for task in tasks)
    pending_tasks = total_tasks - completed_tasks
    user = conn.execute(
        "SELECT username FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    conn.close()
    return render_template(
        "index.html",
        tasks=tasks,
        username=user["username"],
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
    )


@app.route("/add-task", methods=["GET", "POST"])
@login_required
def add_task():
    if request.method == "POST":
        task = request.form.get("task", "").strip()
        priority = request.form.get("priority", "Medium")
        if len(task) > 100:
            flash("Task title must not exceed 100 characters.", "error")
            return redirect(request.referrer)
        if not task:
            flash("Task title cannot be empty.", "error")
            return redirect("/add-task")
        conn = sqlite3.connect("tasks.db")
        conn.execute(
            "INSERT INTO tasks (title, user_id, priority) VALUES (?, ?, ?)",
            (task, session["user_id"], priority),
        )
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("add_task.html")


@app.route("/complete-task/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    task = conn.execute(
        "SELECT completed FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"]),
    ).fetchone()
    if task is not None:
        new_status = 0 if task[0] else 1
        conn.execute(
            "UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?",
            (new_status, task_id, session["user_id"]),
        )
        conn.commit()
    else:
        flash("Task not found.", "error")
    conn.close()
    return redirect("/")


@app.route("/delete-task/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    conn.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    )
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/edit-task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id=?", (task_id, session["user_id"])
    ).fetchone()
    if task is None:
        conn.close()
        flash("Task not found.")
        return redirect("/")
    if request.method == "POST":
        title = request.form.get("task", "").strip()
        priority = request.form.get("priority", "Medium")
        if not title:
            flash("Task title cannot be empty.", "error")
            conn.close()
            return redirect(request.referrer)
        if len(title) > 100:
            flash("Task title must not exceed 100 characters.", "error")
            conn.close()
            return redirect(request.referrer)

        conn.execute(
            "UPDATE tasks SET title =?, priority = ?  WHERE id = ? AND user_id = ?",
            (title, priority, task_id, session["user_id"]),
        )
        conn.commit()
        conn.close()
        flash("Task updated successfully!", "success")
        return redirect("/")
    conn.close()
    return render_template("edit_task.html", task=task)


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect("/")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect("/register")
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect("/register")
        password_hash = generate_password_hash(password)
        try:

            conn = sqlite3.connect("tasks.db")
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?,?)",
                (username, password_hash),
            )
            conn.commit()
        except IntegrityError:
            flash("That username is already taken", "error")
            return redirect("/register")
        finally:
            conn.close()
        flash("Registration successful! Please log in.", "success")
        return redirect("/login")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = sqlite3.connect("tasks.db")
        conn.row_factory = sqlite3.Row
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
            return redirect("/login")
        session["user_id"] = user["id"]
        flash("Login successful!", "success")
        return redirect("/")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
