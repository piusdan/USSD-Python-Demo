# -*-coding:utf-8-*-
"""Main application script"""

import os
import click
from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate


app = create_app(os.getenv('APP_CONFIG') or 'default')
migrate = Migrate(app, db)

# set up code coverage
COV = None
if os.environ.get('APP_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

@app.cli.command()
def initdb():
    """Initialize the database."""
    click.echo('Init the db')
    from flask_migrate import upgrade
    # migrate database to latest revision
    upgrade()

@app.cli.command()
def deploy():
    """ Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models import Role
    # migrate database to latest revision
    upgrade()
    # create user roles
    click.echo("Inserting roles\n-----")
    Role.insert_roles()
    click.echo("Done!")
    click.echo("Inserting roles for users\n------")
    User.insert_user_roles()
    click.echo("Done!")
    click.echo("Ran deployment tasks")


@app.cli.command()
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'temp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://{covdir}index.html'.format(covdir=covdir))
        COV.erase()