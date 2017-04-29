from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, request, flash, redirect,
                   session)
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Board, Task, Job, Priority, BoardJob, BoardJobTask


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = 'ABC'

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage.

    Display all boards, jobs, and tasks in the database.
    """

    boards = Board.query.options(db.joinedload('jobs')).all()

    return render_template('index.html', boards=boards)


@app.route('/board/<board_id>/add_job', methods=['POST'])
def add_job(board_id):
    """Add a job to a board."""

    title = request.form.get('title')
    desc = request.form.get('desc')
    job = Job(title, desc)

    db.session.add(job)
    db.session.commit()

    db.session.add(BoardJob(board_id, job.id))
    db.session.commit()

    return redirect('/')


@app.route('/job/<job_id>/add_task', methods=['POST'])
def add_task(job_id):
    """Add a task to a job."""

    title = request.form.get('title')
    board_id = request.form.get('board_id')
    task = Task(title)

    db.session.add(task)
    db.session.commit()

    board_job = BoardJob.get_boardjob(board_id, job_id)
    db.session.add(BoardJobTask(board_job.id, task.id))
    db.session.commit()

    return redirect('/')


@app.route('/task/<task_id>/move/<board_id>', methods=['POST'])
def move_task(task_id, board_id):
    """Move task to a certain board."""

    task = Task.query.get(task_id)

    # See if there is existing board-job pair
    try:
        board_job = BoardJob.query.filter_by(board_id=task.board_job.board_id, job_id=task.board_job.job_id).one()

        # Make new relationship
        board_job_task = BoardJobTask(board_job.id, task.id)
        db.session.add(board_job_task)
        db.session.commit()
    except:
        board_job = BoardJob(board_id, task.board_job[0].job_id)
        db.session.add(board_job)
        db.session.commit()

        # Make new relationship
        board_job_task = BoardJobTask(board_job.id, task.id)
        db.session.add(board_job)
        db.session.commit()

        print task.board_job

    return redirect('/')


if __name__ == '__main__':
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
