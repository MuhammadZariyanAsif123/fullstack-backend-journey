from pathlib import Path


HOOK_CONTENT = """#!/bin/sh
python scripts/sync_milestones.py || echo 'Milestone sync failed; commit was created successfully.'
"""


def main():
    repository_root = Path(__file__).resolve().parent.parent
    hooks_directory = repository_root / ".git" / "hooks"
    if not hooks_directory.is_dir():
        raise RuntimeError(f"Git hooks directory not found: {hooks_directory}")

    hook_path = hooks_directory / "post-commit"
    hook_path.write_text(HOOK_CONTENT, encoding="utf-8", newline="\n")
    print(f"Installed post-commit hook at {hook_path}")


if __name__ == "__main__":
    main()