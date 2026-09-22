from pathlib import Path


HOOK_CONTENT = """#!/bin/sh
if [ "$SKIP_MILESTONE_SYNC" = "1" ]; then
    exit 0
fi

if [ -x ".venv/Scripts/python.exe" ]; then
    PYTHON=".venv/Scripts/python.exe"
elif [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="python"
fi

"$PYTHON" scripts/sync_milestones.py || echo 'Milestone sync failed; commit was created successfully.'
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