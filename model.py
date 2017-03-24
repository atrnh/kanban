"""Data models for a simple kanban app."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Board(db.Model):
    """A kanban board."""

    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30), nullable=False, unique=True)
    desc = db.Column(db.Text)

    def __repr__(self):
        """Console representation of a board."""
        return '<Board id=%s title=%s>' % (self.id, self.title)

    def __init__(self, title, desc):
        """Create a board."""
        self.title = title
        self.desc = desc


class Job(db.Model):
    """A job that can be broken down into many tasks."""

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30), nullable=False)
    desc = db.Column(db.Text)
    complete = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        """Console representation of a job."""
        return '<Job id=%s title=%s complete=%s>' % (self.id,
                                                     self.title,
                                                     self.complete,
                                                     )


class Task(db.Model):
    """A task in a job."""

    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(40), nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    priority_code = db.Column(db.String(4),
                              db.ForeignKey('priorities.code'),
                              default='none',
                              )
    board_id = db.Column(db.Integer,
                         db.ForeignKey('boards.id'),
                         )
    job_id = db.Column(db.Integer,
                       db.ForeignKey('jobs.id'),
                       )

    priority = db.relationship('Priority',
                               backref='tasks',
                               )
    board = db.relationship('Board',
                            backref='tasks',
                            )
    job = db.relationship('Job',
                          backref='tasks',
                          )

    def __repr__(self):
        """Console representation of a task."""
        return """<Task id=%s title=%s priority=%s complete=%s
                  from job=%s>""" % (self.id,
                                     self.title,
                                     self.priority.title,
                                     self.complete,
                                     self.job.title,
                                     )


class Priority(db.Model):
    """A priority."""

    __tablename__ = 'priorities'

    code = db.Column(db.String(4), primary_key=True)
    title = db.Column(db.String(10), nullable=False, unique=True)

    def __repr__(self):
        """Console representation of a priority."""
        return '<Priority code=%s title=%s' % (self.code, self.title)

    def __init__(self, code, title):
        """Create a priority."""
        self.code = code
        self.title = title


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
