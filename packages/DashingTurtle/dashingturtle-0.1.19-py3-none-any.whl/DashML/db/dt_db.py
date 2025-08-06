import os
import argparse
import pathlib
import tempfile
import shutil
import sys
import subprocess
import importlib.resources as pkg_resources

PACKAGE_NAME = "DashML"
DB_SUBDIR = "db"
INIT_SQL_NAME = "init.sql"
COMPOSE_FILE = "docker-compose.yml"


def check_docker_access():
    # Check if docker is installed
    if not shutil.which("docker"):
        print("❌ Docker is not installed or not in PATH.")
        sys.exit(1)

    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        print("❌ Docker is running but your user lacks permission to access the Docker daemon.")
        print("➡️  Try running:")
        print("    sudo usermod -aG docker $USER")
        print("    newgrp docker  # or log out and back in")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error trying to access Docker: {e}")
        sys.exit(1)



def extract_resource(filename):
    tmp_dir = pathlib.Path(tempfile.mkdtemp(prefix="dashml_"))
    output_path = tmp_dir / filename

    with pkg_resources.files(f"{PACKAGE_NAME}.{DB_SUBDIR}").joinpath(filename).open("rb") as src:
        with open(output_path, "wb") as dst:
            shutil.copyfileobj(src, dst)

    return output_path


def run_docker_compose(command_args, extra_env=None):
    compose_path = pathlib.Path(__file__).parent.parent / DB_SUBDIR / COMPOSE_FILE

    if not compose_path.exists():
        print(f"❌ Could not find docker-compose.yml at {compose_path}")
        return

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    cmd = ["docker", "compose", "-f", str(compose_path)] + command_args
    subprocess.run(cmd, env=env)

def main():
    check_docker_access()

    parser = argparse.ArgumentParser(prog="dt_db", description="DashML DB manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("up", help="Start the database container")
    subparsers.add_parser("reset", help="Warning: Deletes the data!")
    subparsers.add_parser("down", help="Stop and remove the container")
    subparsers.add_parser("logs", help="Show container logs")
    subparsers.add_parser("status", help="Show container status")

    args = parser.parse_args()

    if args.command == "up":
        init_sql_path = extract_resource("init.sql")
        my_cnf_path = extract_resource("my.cnf")

        print(f"📦 Using init.sql: {init_sql_path}")
        print(f"⚙️  Using my.cnf:   {my_cnf_path}")

        run_docker_compose(["up", "--build", "-d"], {
            "INIT_SQL_PATH": str(init_sql_path),
            "MY_CNF_PATH": str(my_cnf_path)
        })

    elif args.command == "down":
        run_docker_compose(["down"])

    elif args.command == "del":
        run_docker_compose(["down", "-v"])

    elif args.command == "logs":
        run_docker_compose(["logs"])

    elif args.command == "status":
        run_docker_compose(["ps"])

    else:
        parser.print_help()
