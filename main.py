from enum import Enum

from flask import Flask, request, render_template
from sqlmodel import create_engine, SQLModel, Field, Session, select


class Status(Enum):
    TO_DO = "ToDo"
    DOING = "Doing"
    DONE = "Done"


class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    status: Status


database_file = "db.sqlite3"
engine = create_engine(f"sqlite:///{database_file}")

SQLModel.metadata.create_all(engine)

app = Flask(__name__)


class BoardColumn:
    name: str
    tasks: list[Task]

    def __init__(self, name: str, tasks: list[Task] | None = None):
        self.name = name
        self.tasks = tasks or []


class Board:
    def __init__(self):
        self.columns: list[BoardColumn] = [
            BoardColumn("ToDo"),
            BoardColumn("Doing"),
            BoardColumn("Done"),
        ]

    def add_task(self, task: Task):
        for column in self.columns:
            if column.name == task.status.value:
                column.tasks.append(task)


@app.get("/")
def index():
    with Session(engine) as session:
        tasks = session.exec(select(Task)).all()

    board = Board()
    for task in tasks:
        board.add_task(task)

    return render_template("index.html", board=board)


@app.post("/tasks")
def add_task():
    title = request.form.get("title")

    with Session(engine) as session:
        task = Task(title=title, status=Status.TO_DO)
        session.add(task)
        session.commit()
        session.refresh(task)
        previous_task = session.exec(
            select(Task).where(Task.id < task.id, Task.status == task.status).order_by(Task.id.desc())).first()

    if previous_task is not None:
        previous_task = previous_task.id

    return render_template("partials/move_task_response.html", to_column="ToDo", task=task,
                           previous_task=previous_task)


@app.post('/task-status')
def update_task_status():
    task_id = request.form.get("task_id")
    column_id = request.form.get("column_id")

    with Session(engine) as session:
        task = session.exec(select(Task).where(Task.id == task_id)).one()
        old_column_name = task.status.value
        task.status = Status(column_id)
        session.add(task)
        session.commit()
        previous_task = session.exec(
            select(Task).where(Task.id < task.id, Task.status == task.status).order_by(Task.id.desc())).first()

    if previous_task is not None:
        previous_task = previous_task.id

    return render_template("partials/move_task_response.html",
                           from_column=old_column_name, to_column=column_id,
                           task=task, previous_task=previous_task)
