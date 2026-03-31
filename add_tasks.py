from main import Task, engine, Status
from sqlmodel import Session, delete
import argparse

def get_status(idx: int):
    match idx % 3:
        case 0: return Status.TO_DO
        case 1: return Status.DOING
        case _: return Status.DONE

def run(count: int):
    with Session(engine) as session:
        session.exec(delete(Task))
        session.commit()

        for x in range(count):
            task = Task(title=f"Task #{x + 1}", status=get_status(x))
            session.add(task)
        session.commit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, nargs="?", default=500)
    args = parser.parse_args()
    run(args.count)
