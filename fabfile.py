#!/usr/bin/env python2
# -*- coding: utf-8 -*-


"""
Deploy script for the Rady application

To be sure that the application never breaks, this script should always be used
when deploying it on a remove server.

This script does not support automated configuration of uwsgi and nginx.
"""


import os

# noinspection PyUnresolvedReferences
from fabric.api import cd, hide, lcd, local, prefix, put, run, sudo, task, warn_only
# noinspection PyUnresolvedReferences
from fabric.colors import blue, green, red, cyan
# noinspection PyUnresolvedReferences
from fabric.state import output, env
# noinspection PyUnresolvedReferences
from fabric.context_managers import shell_env
# noinspection PyUnresolvedReferences
from fabric.utils import abort


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


env.hosts = ["benschubert.me"]
env.colorize_errors = True

output.running = False


REMOTE_PATH = "/srv/rady/"
REMOTE_FRONTEND = os.path.join(REMOTE_PATH, "frontend")
REMOTE_BACKEND = os.path.join(REMOTE_PATH, "backend")
REMOTE_VENV = os.path.join(REMOTE_PATH, "venv")
UWSGI_WATCHER = os.path.join(REMOTE_PATH, "watch")

TEMPORARY_PATH = "/tmp/rady"
TEMPORARY_BACKEND_PATH = os.path.join(TEMPORARY_PATH, "backend")
TEMPORARY_FRONTEND_PATH = os.path.join(TEMPORARY_PATH, "frontend")

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))
LOCAL_APP = os.path.join(LOCAL_PATH, "app")
LOCAL_BACKEND = os.path.join(LOCAL_PATH, "backend")
LOCAL_FRONTEND = os.path.join(LOCAL_PATH, "frontend")
LOCAL_VENV = os.path.join(LOCAL_PATH, os.path.expanduser("~/.virtualenvs/rady"))


class Section:
    def __init__(self, _section, color=blue):
        self.section = _section
        self.color = color

    def __enter__(self):
        print(self.color(self.section))
        print(self.color("-" * 50))

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(self.color("-") * 50)

section = Section


@task
def lint_app():
    """
    Runs configured linters on the application
    """
    with lcd(LOCAL_APP), section("linting app"):
        return local("npm run -s lint")


@task
def lint_backend():
    """
    Runs configured linters on the backend
    """
    with lcd(LOCAL_BACKEND), section("linting backend"):
        return local("prospector")


@task
def lint_frontend():
    """
    Runs configured linters on the frontend
    """
    with lcd(LOCAL_FRONTEND), section("linting frontend"):
        return local("npm run -s lint")


@task
def lint():
    """
    Runs all linters on the whole project
    """
    with warn_only(), section("linting project", green):
        tests = lint_app(), lint_frontend(), lint_backend(),

    if any(not test.succeeded for test in tests):
        abort("Linting failed")


@task
def test_backend():
    """
    Run tests on the backend
    """
    with lcd(LOCAL_BACKEND), section("testing backend"):
        with section("making migrations", cyan):
            local("FCM_SERVER_TOKEN='' python3 manage.py makemigrations")

        with section("running tests", cyan):
            return local("FCM_SERVER_TOKEN='' python3 manage.py test")


@task
def test():
    """
    Runs all tests on the whole project
    """
    with warn_only(), section("testing project", green):
        tests = test_backend(),

    if any(not test.succeeded for test in tests):
        abort("Tests failed")


@task
def check():
    """
    Checks that the application is in a working state
    """
    lint()
    test()


@task
def prepare_deploy():
    """
    Prepare files locally to deploy
    """
    with lcd(LOCAL_FRONTEND), shell_env(NODE_ENV="production"):
        local("npm run -s clean:dist")
        local("npm run -s build")

    with lcd(LOCAL_BACKEND), section("local cleanup"):
        local("""find . -type f -iname "*.pyc" -delete""")
        local("""find . -type d -empty -delete""")
        local("rm -rf ./backend/htmlcov")
        local("rm -f ./backend/.coverage")


@task
def copy_files():
    """
    Copy files to the remote server
    """
    with section("copying to server"):
        for path in [REMOTE_BACKEND, REMOTE_FRONTEND]:
            sudo("mkdir -p " + path)
            sudo("rm -rf " + os.path.join(path, "*"))

        for path in [TEMPORARY_BACKEND_PATH, TEMPORARY_FRONTEND_PATH]:
            run("mkdir -p " + path)
            run("rm -rf " + os.path.join(path, "*"))

        put("{}/*".format(LOCAL_BACKEND), TEMPORARY_BACKEND_PATH)
        run("rm -f {}/rady.db".format(TEMPORARY_BACKEND_PATH))
        sudo("cp -r {}/* {}".format(TEMPORARY_BACKEND_PATH, REMOTE_BACKEND))

        put("{}/dist/*".format(LOCAL_FRONTEND), TEMPORARY_FRONTEND_PATH, mode="0644")
        sudo("cp -r {}/* {}".format(TEMPORARY_FRONTEND_PATH, REMOTE_FRONTEND))


@task
def setup_env():
    """
    Setups the remote environment
    """
    with prefix("source {}/bin/activate".format(REMOTE_VENV)), section("setup of environment"):
        with hide('output'):
            sudo("pip install -r {}/requirements.pip".format(REMOTE_BACKEND))

        with cd(REMOTE_BACKEND):
            sudo("cp {} ./rady/settings/".format(os.path.join(REMOTE_PATH, "prod.py")))
            sudo("python3 manage.py migrate --settings rady.settings.prod")

    # reload uwsgi
    sudo("touch {}".format(UWSGI_WATCHER))


@task
def insecure_deploy():
    """
    Deploys the application without running any tests or checking anything
    """
    with section("deploy"):
        prepare_deploy()
        copy_files()
        setup_env()


@task
def deploy():
    """
    Deploys the complete application
    """
    try:
        check()
    except SystemExit:
        if not env.get("force"):
            raise
        print(red("Check status failed, continuing anyways"))

    insecure_deploy()
