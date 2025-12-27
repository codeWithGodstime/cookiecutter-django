# ruff: noqa: PLR0133
import json
import random
import shutil
import string
import subprocess
import sys
from pathlib import Path

try:
    # Inspired by
    # https://github.com/django/django/blob/main/django/utils/crypto.py
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

TERMINATOR = "\x1b[0m"
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;33m [INFO]: "
HINT = "\x1b[3;33m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "

DEBUG_VALUE = "debug"


def remove_open_source_files():
    file_names = ["CONTRIBUTORS.txt", "LICENSE"]
    for file_name in file_names:
        Path(file_name).unlink()


def remove_custom_user_manager_files():
    users_path = Path("{{cookiecutter.project_slug}}", "apps", "users")
    (users_path / "managers.py").unlink()
    (users_path / "tests" / "test_managers.py").unlink()


def remove_pycharm_files():
    idea_dir_path = Path(".idea")
    if idea_dir_path.exists():
        shutil.rmtree(idea_dir_path)

    docs_dir_path = Path("docs", "pycharm")
    if docs_dir_path.exists():
        shutil.rmtree(docs_dir_path)


def remove_docker_files():
    shutil.rmtree("compose")

    file_names = [
        "docker-compose.local.yml",
        "docker-compose.production.yml",
        ".dockerignore",
        "justfile",
    ]
    for file_name in file_names:
        Path(file_name).unlink()
    if "{{ cookiecutter.editor }}" == "PyCharm":
        file_names = ["docker_compose_up_django.xml", "docker_compose_up_docs.xml"]
        for file_name in file_names:
            Path(".idea", "runConfigurations", file_name).unlink()


def remove_nginx_docker_files():
    shutil.rmtree(Path("compose", "production", "nginx"))


def remove_utility_files():
    shutil.rmtree("utility")


def remove_prettier_pre_commit():
    remove_repo_from_pre_commit_config("mirrors-prettier")


def remove_repo_from_pre_commit_config(repo_to_remove: str):
    pre_commit_config = Path(".pre-commit-config.yaml")
    content = pre_commit_config.read_text().splitlines(keepends=True)

    removing = False
    new_lines = []
    for line in content:
        if removing and "- repo:" in line:
            removing = False
        if repo_to_remove in line:
            removing = True
        if not removing:
            new_lines.append(line)

    pre_commit_config.write_text("".join(new_lines))


def remove_celery_files():
    file_paths = [
        Path("config", "celery_app.py"),
        Path("{{ cookiecutter.project_slug }}", "apps", "users", "tasks.py"),
        Path("{{ cookiecutter.project_slug }}", "apps", "users", "tests", "test_tasks.py"),
    ]
    for file_path in file_paths:
        if file_path.exists():
            file_path.unlink()


def remove_async_files():
    file_paths = [
        Path("config", "asgi.py"),
        Path("config", "websocket.py"),
    ]
    for file_path in file_paths:
        if file_path.exists():
            file_path.unlink()


def remove_docs_files():
    """Remove documentation folder for pure API template."""
    docs_dir = Path("docs")
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
    # Remove docs-related files
    docs_files = [
        Path("docker-compose.docs.yml"),
        Path(".readthedocs.yml"),
    ]
    for doc_file in docs_files:
        if doc_file.exists():
            doc_file.unlink()


def remove_locale_files():
    """Remove locale folder for pure API template."""
    locale_dir = Path("locale")
    if locale_dir.exists():
        shutil.rmtree(locale_dir)


def remove_bin_folder():
    """Remove bin folder."""
    bin_dir = Path("bin")
    if bin_dir.exists():
        shutil.rmtree(bin_dir)


def remove_dottravisyml_file():
    Path(".travis.yml").unlink()


def remove_dotgitlabciyml_file():
    Path(".gitlab-ci.yml").unlink()


def remove_dotgithub_folder():
    shutil.rmtree(".github")


def remove_dotdrone_file():
    Path(".drone.yml").unlink()


def remove_channel_files():
    file_paths = [
        Path("config", "routing.py"),
        Path("{{ cookiecutter.project_slug }}", "apps", "users", "consumers.py"),
    ]
    for file_path in file_paths:
        if file_path.exists():
            file_path.unlink()


def generate_random_string(length, using_digits=False, using_ascii_letters=False, using_punctuation=False):  # noqa: FBT002
    """
    Example:
        opting out for 50 symbol-long, [a-z][A-Z][0-9] string
        would yield log_2((26+26+50)^50) ~= 334 bit strength.
    """
    if not using_sysrandom:
        return None

    symbols = []
    if using_digits:
        symbols += string.digits
    if using_ascii_letters:
        symbols += string.ascii_letters
    if using_punctuation:
        all_punctuation = set(string.punctuation)
        # These symbols can cause issues in environment variables
        unsuitable = {"'", '"', "\\", "$"}
        suitable = all_punctuation.difference(unsuitable)
        symbols += "".join(suitable)
    return "".join([random.choice(symbols) for _ in range(length)])


def set_flag(file_path: Path, flag, value=None, formatted=None, *args, **kwargs):
    if value is None:
        random_string = generate_random_string(*args, **kwargs)
        if random_string is None:
            print(
                "We couldn't find a secure pseudo-random number generator on your "
                f"system. Please, make sure to manually {flag} later.",
            )
            random_string = flag
        if formatted is not None:
            random_string = formatted.format(random_string)
        value = random_string

    with file_path.open("r+") as f:
        file_contents = f.read().replace(flag, value)
        f.seek(0)
        f.write(file_contents)
        f.truncate()

    return value


def set_django_secret_key(file_path: Path):
    return set_flag(
        file_path,
        "!!!SET DJANGO_SECRET_KEY!!!",
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )


def set_django_admin_url(file_path: Path):
    return set_flag(
        file_path,
        "!!!SET DJANGO_ADMIN_URL!!!",
        formatted="{}/",
        length=32,
        using_digits=True,
        using_ascii_letters=True,
    )


def generate_random_user():
    return generate_random_string(length=32, using_ascii_letters=True)


def generate_postgres_user(debug=False):  # noqa: FBT002
    return DEBUG_VALUE if debug else generate_random_user()


def set_postgres_user(file_path, value):
    return set_flag(file_path, "!!!SET POSTGRES_USER!!!", value=value)


def set_postgres_password(file_path, value=None):
    return set_flag(
        file_path,
        "!!!SET POSTGRES_PASSWORD!!!",
        value=value,
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )


def set_celery_flower_user(file_path, value):
    return set_flag(file_path, "!!!SET CELERY_FLOWER_USER!!!", value=value)


def set_celery_flower_password(file_path, value=None):
    return set_flag(
        file_path,
        "!!!SET CELERY_FLOWER_PASSWORD!!!",
        value=value,
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )


def append_to_gitignore_file(ignored_line):
    with Path(".gitignore").open("a") as gitignore_file:
        gitignore_file.write(ignored_line)
        gitignore_file.write("\n")


def set_flags_in_envs(postgres_user, celery_flower_user, debug=False):  # noqa: FBT002
    """Set flags in the single .env file."""
    env_path = Path(".env")
    
    if not env_path.exists():
        return
    
    env_content = env_path.read_text()
    
    # Generate secret key for Django
    django_secret_key = generate_random_string(50, using_digits=True, using_ascii_letters=True)
    env_content = env_content.replace("your-secret-key-here", django_secret_key)
    
    # Set postgres user
    env_content = env_content.replace("!!!SET POSTGRES_USER!!!", postgres_user)
    env_content = env_content.replace("POSTGRES_PASSWORD=postgres", f"POSTGRES_PASSWORD={DEBUG_VALUE if debug else generate_random_string(15, using_digits=True, using_ascii_letters=True)}")
    
    # Set Celery flower credentials if Celery is enabled
    if "{{ cookiecutter.use_celery }}" == "y":
        env_content = env_content.replace("!!!SET CELERY_FLOWER_USER!!!", celery_flower_user)
        env_content = env_content.replace("CELERY_FLOWER_PASSWORD=password", f"CELERY_FLOWER_PASSWORD={DEBUG_VALUE if debug else generate_random_string(15, using_digits=True, using_ascii_letters=True)}")
    
    env_path.write_text(env_content)


def set_flags_in_settings_files():
    set_django_secret_key(Path("config", "settings", "local.py"))
    set_django_secret_key(Path("config", "settings", "test.py"))


def remove_celery_compose_dirs():
    shutil.rmtree(Path("compose", "local", "django", "celery"))
    shutil.rmtree(Path("compose", "production", "django", "celery"))


def remove_node_dockerfile():
    shutil.rmtree(Path("compose", "local", "node"))


def remove_aws_dockerfile():
    shutil.rmtree(Path("compose", "production", "aws"))


def remove_drf_starter_files():
    Path("config", "api_router.py").unlink()
    shutil.rmtree(Path("{{cookiecutter.project_slug}}", "apps", "users", "api"))
    shutil.rmtree(Path("{{cookiecutter.project_slug}}", "apps", "users", "tests", "api"))
    

def remove_prometheus_grafana_files():
    """Remove Prometheus and Grafana configuration if not needed."""
    compose_local = Path("compose", "local")
    compose_prod = Path("compose", "production")
    
    prometheus_dirs = [
        compose_local / "prometheus",
        compose_prod / "prometheus",
    ]
    
    grafana_dirs = [
        compose_local / "grafana",
        compose_prod / "grafana",
    ]
    
    for dir_path in prometheus_dirs + grafana_dirs:
        if dir_path.exists():
            shutil.rmtree(dir_path)


def main():  # noqa: C901, PLR0912, PLR0915
    debug = "{{ cookiecutter.debug }}".lower() == "y"

    set_flags_in_envs(
        DEBUG_VALUE if debug else generate_random_user(),
        DEBUG_VALUE if debug else generate_random_user(),
        debug=debug,
    )
    set_flags_in_settings_files()

    if "{{ cookiecutter.open_source_license }}" == "Not open source":
        remove_open_source_files()

    if "{{ cookiecutter.username_type }}" == "username":
        remove_custom_user_manager_files()

    if "{{ cookiecutter.editor }}" != "PyCharm":
        remove_pycharm_files()

    if "{{ cookiecutter.use_docker }}".lower() == "y":
        remove_utility_files()
        if "{{ cookiecutter.cloud_provider }}".lower() != "none":
            remove_nginx_docker_files()
    else:
        remove_docker_files()

    if "{{ cookiecutter.use_docker }}".lower() == "y" and "{{ cookiecutter.cloud_provider}}" != "AWS":
        remove_aws_dockerfile()

    else:
        append_to_gitignore_file(".env")
        append_to_gitignore_file(".envs/*")
        if "{{ cookiecutter.keep_local_envs_in_vcs }}".lower() == "y":
            append_to_gitignore_file("!.envs/.local/")

    if "{{ cookiecutter.cloud_provider }}" == "None" and "{{ cookiecutter.use_docker }}".lower() == "n":
        print(
            WARNING + "You chose to not use any cloud providers nor Docker, "
            "media files won't be served in production." + TERMINATOR,
        )

    # Always remove for pure API template
    remove_docs_files()
    remove_locale_files()
    remove_bin_folder()

    if "{{ cookiecutter.use_celery }}".lower() == "n":
        remove_celery_files()
        if "{{ cookiecutter.use_docker }}".lower() == "y":
            remove_celery_compose_dirs()

    if "{{ cookiecutter.ci_tool }}" != "Travis":
        remove_dottravisyml_file()

    if "{{ cookiecutter.ci_tool }}" != "Gitlab":
        remove_dotgitlabciyml_file()

    if "{{ cookiecutter.ci_tool }}" != "Github":
        remove_dotgithub_folder()

    if "{{ cookiecutter.ci_tool }}" != "Drone":
        remove_dotdrone_file()

    if "{{ cookiecutter.use_async }}".lower() == "n":
        remove_async_files()

    if "{{ cookiecutter.use_channels }}".lower() == "n":
        remove_channel_files()

    if "{{ cookiecutter.monitoring }}".lower() == "none":
        remove_prometheus_grafana_files()

    setup_dependencies()

    print(SUCCESS + "Project initialized, keep up the good work!" + TERMINATOR)


def setup_dependencies():
    if "{{ cookiecutter.use_docker }}".lower() == "y":
        print("Installing python dependencies using uv...")
        # Build a trimmed down Docker image add dependencies with uv
        uv_docker_image_path = Path("compose/local/uv/Dockerfile")
        uv_image_tag = "cookiecutter-django-uv-runner:latest"
        try:
            subprocess.run(  # noqa: S603
                [  # noqa: S607
                    "docker",
                    "build",
                    "--load",
                    "-t",
                    uv_image_tag,
                    "-f",
                    str(uv_docker_image_path),
                    "-q",
                    ".",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error building Docker image: {e}", file=sys.stderr)
            sys.exit(1)

        current_path = Path.cwd().absolute()
        # Use Docker to run the uv command
        uv_cmd = ["docker", "run", "--rm", "-v", f"{current_path}:/app", uv_image_tag, "uv"]

        # Install production dependencies
        try:
            subprocess.run([*uv_cmd, "add", "--no-sync", "-r", "requirements/production.txt"], check=True)  # noqa: S603
        except subprocess.CalledProcessError as e:
            print(f"Error installing production dependencies: {e}", file=sys.stderr)
            sys.exit(1)

        # Install local (development) dependencies
        try:
            subprocess.run([*uv_cmd, "add", "--no-sync", "--dev", "-r", "requirements/local.txt"], check=True)  # noqa: S603
        except subprocess.CalledProcessError as e:
            print(f"Error installing local dependencies: {e}", file=sys.stderr)
            sys.exit(1)

        uv_image_parent_dir_path = Path("compose/local/uv")
        if uv_image_parent_dir_path.exists():
            shutil.rmtree(str(uv_image_parent_dir_path))
    else:
        print("Installing python dependencies using pip...")
        # Use pip with virtualenv for non-Docker setup
        try:
            # Install production dependencies
            subprocess.run(  # noqa: S603
                [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements/production.txt"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error installing production dependencies: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            # Install local (development) dependencies
            subprocess.run(  # noqa: S603
                [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements/local.txt"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error installing local dependencies: {e}", file=sys.stderr)
            sys.exit(1)

    # Remove the requirements directory
    requirements_dir = Path("requirements")
    if requirements_dir.exists():
        try:
            shutil.rmtree(requirements_dir)
        except Exception as e:  # noqa: BLE001
            print(f"Error removing 'requirements' folder: {e}", file=sys.stderr)
            sys.exit(1)

    print("Setup complete!")


if __name__ == "__main__":
    main()
