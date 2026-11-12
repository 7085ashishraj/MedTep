"""Run the local verification suite with the selected Python interpreter."""
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main():
    node = shutil.which("node")
    if node is None:
        print("Node.js is required for the JavaScript checks. Install Node.js, then rerun this command.", file=sys.stderr)
        return 1

    # Only child processes receive these test values; .env and the running server are unchanged.
    environment = os.environ.copy()
    environment.update({
        "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
        "DJANGO_DEBUG": "False",
        "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1,testserver",
        "PYTHONUNBUFFERED": "1",
    })
    checks = [
        ("Django configuration", [sys.executable, "manage.py", "check"]),
        ("Migration drift", [sys.executable, "manage.py", "makemigrations", "--check", "--dry-run"]),
        ("Django tests", [sys.executable, "manage.py", "test", "--noinput"]),
        ("Shared UI checks", [node, "core/ui_frontend_tests.cjs"]),
        ("Facility checks", [node, "facilities/frontend_tests.cjs"]),
        ("SOS checks", [node, "emergency/frontend_tests.cjs"]),
        ("Ambulance checks", [node, "emergency/ambulance_frontend_tests.cjs"]),
    ]
    for label, command in checks:
        print(f"\nChecking: {label}", flush=True)
        try:
            result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
        except OSError as error:
            print(f"Could not start {label}: {error}", file=sys.stderr)
            return 1
        if result.returncode:
            print(f"Stopped: {label} failed. Fix the error above, then rerun.", file=sys.stderr)
            return 1
    print("\nAll 7 project check groups passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
