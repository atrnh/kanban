"""Data models for a simple kanban app."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm

db = SQLAlchemy()


class BoardJob(db.Model):
    """A board-job pair."""

    __tablename__ = 'boards_jobs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))

    tasks = db.relationship('Task', secondary='boards_jobs_tasks')

    def __init__(self, board_id, job_id):
        """Make a BoardJob."""

        self.board_id = board_id
        self.job_id = job_id

    def __repr__(self):
        """Console represenation of a BoardJob."""

        return ('<BoardJob board_id={board_id} ' +
                'job_id={job_id}>').format(board_id=self.board_id,
                                           job_id=self.job_id,
                                           )

    @classmethod
    def get_boardjob(cls, board_id, job_id):
        """Return BoardJob in database with given board_id and job_id."""

        try:
            return cls.query.filter_by(board_id=board_id, job_id=job_id).one()
        except orm.exc.NoResultFound:
            return None
        except orm.exc.MultipleResultsFound:
            db.session.delete(cls.query.filter_by(board_id=board_id, job_id=job_id).first())
            db.session.commit()
            return cls.query.filter_by(board_id=board_id, job_id=job_id).one()


class BoardJobTask(db.Model):
    """Association between a task and its board-job pair."""

    __tablename__ = 'boards_jobs_tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    board_job_id = db.Column(db.Integer, db.ForeignKey('boards_jobs.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

    def __init__(self, board_job_id, task_id):
        """Make a BoardJobTask."""

        self.board_job_id = board_job_id
        self.task_id = task_id

    def __repr__(self):
        """Console representation of a BoardJobTask."""

        return ('<BoardJobTask board_job_id={board_job_id} ' +
                'task_id={task_id}').format(board_job_id=self.board_job_id,
                                            task_id=self.task_id,
                                            )


class Board(db.Model):
    """A kanban board."""

    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30), unique=True)
    desc = db.Column(db.Text, nullable=True)

    jobs = db.relationship('Job', secondary='boards_jobs')

    def __repr__(self):
        """Console representation of a board."""

        return '<Board id={id} title={title}'.format(id=self.id,
                                                     title=self.title,
                                                     )

    def __init__(self, title, desc=None):
        """Create a board."""
        self.title = title
        self.desc = desc


class Job(db.Model):
    """A job that can be broken down into many tasks."""

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30))
    desc = db.Column(db.Text, nullable=True)
    complete = db.Column(db.Boolean, default=False)

    boards = db.relationship('Board', secondary='boards_jobs')

    def __init__(self, title, desc=None):
        """Make a job."""
        self.title = title
        self.desc = desc

    def __repr__(self):
        """Console representation of a job."""

        return ('<Job id={id} title={title} ' +
                'complete={complete}').format(id=self.id,
                                              title=self.title,
                                              complete=self.complete,
                                              )

    def get_tasks(self, board):
        """Return a list of tasks associated with the job and board."""

        return BoardJob.get_boardjob(board.id, self.id).tasks


class Task(db.Model):
    """A task in a job."""

    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean, default=False)
    priority_code = db.Column(db.String(4),
                              db.ForeignKey('priorities.code'),
                              default='none',
                              )

    priority = db.relationship('Priority')
    board_job = db.relationship('BoardJob', secondary='boards_jobs_tasks')

    def __init__(self, title):
        """Create a task."""

        self.title = title

    def __repr__(self):
        """Console representation of a task."""

        return '<Task id={id} title={title}>'.format(id=self.id,
                                                     title=self.title,
                                                     )


class Priority(db.Model):
    """A priority."""

    __tablename__ = 'priorities'

    code = db.Column(db.String(4), primary_key=True)
    title = db.Column(db.String(10), unique=True)

    tasks = db.relationship('Task')

    def __init__(self, code, title):
        """Create a priority."""
        self.code = code
        self.title = title

    def __repr__(self):
        """Console representation of a priority."""
        return '<Priority code={code} title={title}'.format(code=self.code,
                                                            title=self.title,
                                                            )


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///kanban'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def seed_db():
    """Seed database."""
    db.create_all()
    db.session.add_all([Priority('none', 'None'),
                        Priority('min', 'Minor'),
                        Priority('med', 'Medium'),
                        Priority('urg', 'Urgent'),
                        Board('To Do', 'Things to do'),
                        Board('Doing', "Things I'm working on"),
                        Board('Done', 'Completed tasks')
                        ])
    db.session.commit()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
