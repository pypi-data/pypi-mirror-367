import argparse
import sys
from pathlib import Path
import importlib.resources


def main():
    parser = argparse.ArgumentParser(
        description="Create Keycloak Docker compose.yaml and .env files for development"
    )
    parser.parse_args()

    compose_file = Path("compose.yaml")
    if compose_file.exists():
        print("Error: compose.yaml already exists", file=sys.stderr)
        exit(1)

    with importlib.resources.open_text("ackc", "compose.yaml") as f:
        compose_content = f.read()

    compose_file.write_text(compose_content)
    print("compose.yaml: Created")

    env_file = Path(".env")
    with importlib.resources.open_text("ackc", ".env.example") as f:
        env_content = f.read()

    if env_file.exists():
        with env_file.open("a") as f:
            f.write("\n# From ackc\n")
            f.write(env_content)
        print(".env: Appended environment variables")
    else:
        env_file.write_text(env_content)
        print(".env: Created from .env.example")

    print("\nNext: Edit .env to uncomment and customize your Keycloak settings")


if __name__ == "__main__":
    main()
