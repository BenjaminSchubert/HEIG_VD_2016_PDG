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
from fabric.api import cd, hide, lcd, local, prefix, put, run, sudo
# noinspection PyUnresolvedReferences
from fabric.colors import blue, green, red
# noinspection PyUnresolvedReferences
from fabric.state import output, env
# noinspection PyUnresolvedReferences
from fabric.context_managers import shell_env


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


def start_section(section, color=blue):
    print(color(section))
    print(color("-" * 50))


def stop_section(color=blue):
    print(color("-") * 50)


def lint_app():
    """
    Runs configured linters on the application
    """
    with lcd(LOCAL_APP):
        start_section("linting app")
        local("npm run -s lint")
        stop_section()


def lint_backend():
    """
    Runs configured linters on the backend
    """
    with lcd(LOCAL_BACKEND):
        start_section("linting backend")
        local("prospector")
        stop_section()


def lint_frontend():
    """
    Runs configured linters on the frontend
    """
    with lcd(LOCAL_FRONTEND):
        start_section("linting frontend")
        local("npm run -s lint")
        stop_section()


def lint():
    """
    Runs all linters on the whole project
    """
    start_section("linting project", green)
    lint_app()
    lint_frontend()
    lint_backend()
    stop_section(green)


def test_backend():
    """
    Run tests on the backend
    """
    with lcd(LOCAL_BACKEND):
        start_section("making migrations")
        local("FCM_SERVER_TOKEN='' python3 manage.py makemigrations")
        start_section("testing backend")
        local("FCM_SERVER_TOKEN='' python3 manage.py test")
        stop_section()


def test():
    """
    Runs all tests on the whole project
    """
    start_section("testing project", green)
    test_backend()
    stop_section(green)


def check_status():
    """
    Checks that the application is in a working state
    """
    lint()
    test()


def prepare_deploy():
    """
    Prepare files locally to deploy
    """
    with lcd(LOCAL_FRONTEND):
        with shell_env(NODE_ENV="production"):
            local("npm run -s clean:dist")
            local("npm run -s build")

    with lcd(LOCAL_BACKEND):
        start_section("local cleanup")
        local("""find . -type f -iname "*.pyc" -delete""")
        local("""find . -type d -empty -delete""")
        local("rm -rf ./backend/htmlcov")
        local("rm -f ./backend/.coverage")
        stop_section()


def copy_files():
    """
    Copy files to the remote server
    """
    start_section("copying to server")

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
    stop_section()


def setup_env():
    """
    Setups the remote environment
    """
    start_section("setup of environment")
    with prefix("source {}/bin/activate".format(REMOTE_VENV)):
        with hide('output'):
            sudo("pip install -r {}/requirements.pip".format(REMOTE_BACKEND))

        with cd(REMOTE_BACKEND):
            sudo("cp {} ./rady/settings/".format(os.path.join(REMOTE_PATH, "prod.py")))
            sudo("python3 manage.py migrate --settings rady.settings.prod")

    # reload uwsgi
    sudo("touch {}".format(UWSGI_WATCHER))
    stop_section()


def insecure_deploy():
    """
    Deploys the application without running any tests or checking anything
    """
    start_section("deploy", green)
    prepare_deploy()
    copy_files()
    setup_env()
    stop_section(green)


def deploy():
    """
    Deploys the complete application
    """
    try:
        check_status()
    except SystemExit:
        if not env.get("force"):
            raise
        print(red("Check status failed, continuing anyways"))

    insecure_deploy()
