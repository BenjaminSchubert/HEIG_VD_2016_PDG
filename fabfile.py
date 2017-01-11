#!/usr/bin/env python2
# -*- coding: utf-8 -*-


"""
Deploy script for the Rady application

To be sure that the application never breaks, this script should always be used
when deploying it on a remove server.

This script does not support automated configuration of uwsgi and nginx.
"""
import subprocess

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

ANDROID_HOME = "/opt/android-sdk"
LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))
LOCAL_APP = os.path.join(LOCAL_PATH, "app")
LOCAL_BACKEND = os.path.join(LOCAL_PATH, "backend")
LOCAL_FRONTEND = os.path.join(LOCAL_PATH, "frontend")
LOCAL_VENV = os.path.join(LOCAL_PATH, "venv")

SIGNING_KEY = "{}/.keys/rady-release-key.keystore".format(LOCAL_APP)


BASE_APK_NAME = "android-release-unsigned.apk"
BUILT_APK_NAME = "rady.apk"
APK_BUILD_PATH = os.path.join(LOCAL_APP, "platforms/android/build/outputs/apk/")

PATH_TO_BASE_APK = os.path.join(APK_BUILD_PATH, BASE_APK_NAME)
PATH_TO_BUILT_APK = os.path.join(APK_BUILD_PATH, BUILT_APK_NAME)

npm = None


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


def copy(local, remote):
    """Copy local files to the remote destination, using an intermediate directory."""
    sudo("mkdir -p " + remote)
    sudo("rm -rf " + os.path.join(remote, "*"))
    run("mkdir -p " + TEMPORARY_PATH)
    run("rm -rf " + os.path.join(TEMPORARY_PATH, "*"))

    put("{}/*".format(local), TEMPORARY_PATH, mode=644)
    sudo("cp -r {}/* {}".format(TEMPORARY_PATH, remote))
    sudo("rm -r {}".format(TEMPORARY_PATH))


def get_android_home():
    """Get the android home directory."""
    android_home = os.environ.get("ANDROID_HOME", None)

    if android_home is None:
        android_home = ANDROID_HOME

    if not os.path.exists(android_home):
        abort("ANDROID_HOME set as {} does not exist, can't continue".format(android_home))

    return android_home


def get_npm():
    """Get npm executable."""
    global npm
    if npm is None:
        try:
            subprocess.check_call(["which", "yarn"])
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call(["which", "npm"])
            except subprocess.CalledProcessError:
                abort("Could not find npm, do you have it installed and in PATH ?")
            else:
                npm = "npm"
        else:
            npm = "yarn"

    return npm


@task
def lint_app():
    """Run configured linters on the application."""
    with lcd(LOCAL_APP), section("linting app"):
        return local("npm run -s lint")


@task
def lint_backend():
    """Run configured linters on the backend."""
    with lcd(LOCAL_BACKEND), section("linting backend"):
        return local("prospector")


@task
def lint_frontend():
    """Run configured linters on the frontend."""
    with lcd(LOCAL_FRONTEND), section("linting frontend"):
        return local("npm run -s lint")


@task
def lint():
    """Run all linters on the whole project."""
    with warn_only(), section("linting project", green):
        tests = lint_app(), lint_frontend(), lint_backend(),

    if any(not test.succeeded for test in tests):
        abort("Linting failed")


@task
def test_backend():
    """Run tests on the backend."""
    with lcd(LOCAL_BACKEND), section("testing backend"):
        with section("making migrations", cyan):
            local("FCM_SERVER_TOKEN='' python3 manage.py makemigrations")

        with section("running tests", cyan):
            return local("FCM_SERVER_TOKEN='' python3 manage.py test")


@task
def test():
    """Run all tests on the whole project."""
    with warn_only(), section("testing project", green):
        tests = test_backend(),

    if any(not test.succeeded for test in tests):
        abort("Tests failed")


@task
def check():
    """Check that the application is in a working state."""
    lint()
    test()


@task
def prepare_backend():
    """Prepare the backend to deploy."""
    with lcd(LOCAL_BACKEND), section("Preparing backend"):
        local("""find . -type f -iname "*.pyc" -delete""")
        local("""find . -type d -empty -delete""")
        local("rm -rf {}/htmlcov".format(LOCAL_BACKEND))
        local("rm -f {}/.coverage".format(LOCAL_BACKEND))


@task
def prepare_frontend():
    """Prepare and build the frontend."""
    with lcd(LOCAL_FRONTEND), shell_env(NODE_ENV="production"), section("Preparing frontend"):
        local("npm run -s clean:dist")
        local("npm run -s build")


@task
def prepare_app():
    """Prepare and build the application."""
    with lcd(LOCAL_APP), shell_env(ANDROID_HOME=get_android_home()), section("Preparing application"):
        local("{} run clean".format(get_npm()))
        local("{} run build:android".format(get_npm()))

        local("jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore {} {} alias_name".format(
            SIGNING_KEY, PATH_TO_BASE_APK
        ))

        max_version = sorted(os.listdir(os.path.join(get_android_home(), "build-tools")))[-1]
        zipalign = os.path.join(ANDROID_HOME, "build-tools", max_version, "zipalign")
        local("rm -f {}".format(PATH_TO_BUILT_APK))
        local("{} -v 4 {} {}".format(zipalign, PATH_TO_BASE_APK, PATH_TO_BUILT_APK))


@task
def prepare_deployment():
    """Prepare files locally to deploy."""
    with section("Preparing for deployment", green):
        prepare_backend()
        prepare_frontend()
        prepare_app()


@task
def deploy_frontend():
    """Deploy the frontend."""
    with section("Deploying frontend"):
        copy("{}/dist".format(LOCAL_FRONTEND), REMOTE_FRONTEND)


@task
def deploy_backend():
    """Deploy the backend."""
    with section("Deploying backend"):
        copy(LOCAL_BACKEND, REMOTE_BACKEND)
        sudo("rm -f {}/rady.db".format(REMOTE_BACKEND))

        with prefix("source {}/bin/activate".format(REMOTE_VENV)), section("setup of environment"):
            with hide('output'):
                sudo("pip install -r {}/requirements.pip".format(REMOTE_BACKEND))

            with cd(REMOTE_BACKEND):
                sudo("cp {} ./rady/settings/".format(os.path.join(REMOTE_PATH, "prod.py")))
                sudo("python3 manage.py migrate --settings rady.settings.prod")
                sudo("python3 manage.py collectstatic --noinput --settings rady.settings.prod")

        # reload uwsgi
        sudo("touch {}".format(UWSGI_WATCHER))


@task
def deploy_app():
    with section("Deploying app"):
        run("mkdir -p " + TEMPORARY_PATH)
        put(PATH_TO_BUILT_APK, "{}/".format(TEMPORARY_PATH))
        sudo("mkdir -p {}/downloads".format(REMOTE_FRONTEND))
        sudo("cp {}/{} {}/downloads/rady.apk".format(TEMPORARY_PATH, BUILT_APK_NAME, REMOTE_FRONTEND))
        sudo("rm -r {}".format(TEMPORARY_PATH))


@task
def insecure_deploy():
    """
    Deploys the application without running any tests or checking anything
    """
    with section("deploy"):
        prepare_deployment()
        deploy_backend()
        deploy_frontend()
        deploy_app()


@task
def deploy():
    """Deploy the complete application."""
    try:
        check()
    except SystemExit:
        if not env.get("force"):
            raise
        print(red("Check status failed, continuing anyways"))

    insecure_deploy()


@task
def setup_dev():
    """Setup local dev environment for work."""
    with section("Setting up dev environment"):
        with lcd(LOCAL_APP):
            local("{} install".format(get_npm()))

        with lcd(LOCAL_FRONTEND):
            local("{} install".format(get_npm()))

        if not os.path.exists(LOCAL_VENV):
            local("virtualenv -p python3.5 {}".format(LOCAL_VENV))

        with prefix("source {}/bin/activate".format(LOCAL_VENV)), lcd(LOCAL_BACKEND):
            local("pip3 install -r ./requirements.pip")


@task
def create_keys():
    """Create signing keys for the android application."""
    local("mkdir -p {}".format(os.path.dirname(SIGNING_KEY)))
    local("keytool -genkey -v -keystore {} -alias alias_name -keyalg RSA -keysize 2048 -validity 10000".format(
        SIGNING_KEY
    ))
