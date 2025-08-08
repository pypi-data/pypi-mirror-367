import subprocess
import argparse
from pathlib import Path

def get_modified_models(base_ref: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref, "--", "models/**/*.sql", "--diff-filter=AM"],
            capture_output=True,
            check=True,
            text=True,
            shell=False,
        )
        files = result.stdout.strip().split("\n")
        return [Path(f).stem for f in files if f.strip()]
    except subprocess.CalledProcessError:
        return []

def build_selector(models: list[str], number: str | None) -> str:
    suffix = f"+{number}" if number else "+"
    return " ".join(f"{model}{suffix}" for model in models)

def main():
    parser = argparse.ArgumentParser(description="Run dbt on changed models.")
    parser.add_argument("-m", "--main", action="store_true", help="Compare against origin/main instead of HEAD")
    parser.add_argument("-c", "--command", default="build", help="dbt command to run (default: build)")
    parser.add_argument("-t", "--target", default="dev", help="dbt target (default: dev)")
    parser.add_argument("-fr", "--full-refresh", action="store_true", help="Include --full-refresh")
    parser.add_argument("-ff", "--fail-fast", action="store_true", help="Include --fail-fast")
    parser.add_argument("-n", "--number", help="Add a number suffix after the '+' (e.g., +1)")

    args = parser.parse_args()
    base_ref = "origin/main" if args.main else "HEAD"

    models = get_modified_models(base_ref)

    if not models:
        print(f"No modified models compared to {base_ref}. Skipping dbt.")
        return

    selector = build_selector(models, args.number)

    cmd = ["dbt", args.command, "-s", selector, "-t", args.target]
    if args.full_refresh:
        cmd.append("--full-refresh")
    if args.fail_fast:
        cmd.append("--fail-fast")

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()