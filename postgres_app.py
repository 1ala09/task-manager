from flask import Flask, jsonify, render_template, request
from db import get_connection

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("simple.html")


@app.route("/add-task")
def add_task():
    conn = get_connection()

    conn.execute(
        "INSERT INTO tasks (title, user_id) VALUES (%s, %s)", ("Learn Flask routes", 1)
    )
    conn.commit()
    conn.close()
    return "Task added successfully!"


@app.route("/update-task")
def update_task():
    conn = get_connection()

    conn.execute(
        "UPDATE tasks SET title = %s WHERE id = %s",
        ("Practising Flask and PostgreSQL", 1),
    )
    conn.commit()
    conn.close()

    return "Task updated successfully!"


@app.route("/delete-task")
def delete_task():
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = %s", (1,))
    conn.commit()
    conn.close()
    return "Task deleted successfully!"


@app.route("/api/tasks", methods=["GET", "POST"])
def get_tasks():
    if request.method == "POST":
        data = request.get_json()
        return jsonify({"message": "Task recieved successfully!", "task": data})
    tasks = [
        {"id": 1, "title": "Learn Flask", "completed": False},
        {"id": 2, "title": "Learn JavaScript", "completed": True},
    ]
    return jsonify(tasks)


if __name__ == "__main__":
    app.run(debug=True)
