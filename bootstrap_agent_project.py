#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
from textwrap import dedent


@dataclass(frozen=True)
class ProjectConfig:
    target: Path
    name: str
    slug: str
    product_promise: str
    supabase_ref: str
    supabase_url: str
    force: bool
    git_init: bool


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap a generic agent-oriented project workspace."
    )
    parser.add_argument("target", type=Path, help="Directory to create or populate.")
    parser.add_argument("--name", required=True, help="Human-readable project name.")
    parser.add_argument("--slug", required=True, help="Machine-readable project slug.")
    parser.add_argument(
        "--product-promise",
        default="Describe the product promise here.",
        help="Short mission or product promise for AGENTS.md.",
    )
    parser.add_argument(
        "--supabase-ref", default="", help="Optional Supabase project ref."
    )
    parser.add_argument(
        "--supabase-url", default="", help="Optional Supabase project URL."
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite template-owned files."
    )
    parser.add_argument(
        "--git-init", action="store_true", help="Run git init in the target."
    )
    args = parser.parse_args(argv)

    config = ProjectConfig(
        target=args.target.expanduser().resolve(),
        name=args.name,
        slug=args.slug,
        product_promise=args.product_promise,
        supabase_ref=args.supabase_ref,
        supabase_url=args.supabase_url,
        force=args.force,
        git_init=args.git_init,
    )

    try:
        bootstrap(config)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"Bootstrapped agent project at {config.target}")
    print("Next steps:")
    print("  1. Edit AGENTS.md for project-specific rules.")
    print("  2. Add planning docs under docs/planning/.")
    print("  3. Add the first issue under issues/ready/.")
    print("  4. Run: just check")
    return 0


def bootstrap(config: ProjectConfig) -> None:
    config.target.mkdir(parents=True, exist_ok=True)

    files = render_files(config)
    for relative_path, content in files.items():
        write_file(config.target / relative_path, content, force=config.force)

    for directory in (
        "issues/ready",
        "issues/in_progress",
        "issues/done",
        "issues/blocked",
        "docs/planning",
        "scripts",
        "tests",
    ):
        (config.target / directory).mkdir(parents=True, exist_ok=True)

    for placeholder in (
        "issues/ready/.gitkeep",
        "issues/in_progress/.gitkeep",
        "issues/done/.gitkeep",
        "issues/blocked/.gitkeep",
        "docs/planning/.gitkeep",
    ):
        write_file(config.target / placeholder, "", force=config.force)

    if config.git_init and not (config.target / ".git").exists():
        subprocess.run(["git", "init"], cwd=config.target, check=True)


def write_file(path: Path, content: str, *, force: bool) -> None:
    if path.exists() and not force:
        raise RuntimeError(f"{path} already exists. Re-run with --force to overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_files(config: ProjectConfig) -> dict[str, str]:
    replacements = {
        "{{PROJECT_NAME}}": config.name,
        "{{PROJECT_SLUG}}": config.slug,
        "{{PRODUCT_PROMISE}}": config.product_promise,
        "{{SUPABASE_PROJECT_REF}}": config.supabase_ref or "unset",
        "{{SUPABASE_URL}}": config.supabase_url or "unset",
    }

    templates = {
        ".gitignore": GITIGNORE,
        "AGENTS.md": AGENTS,
        "README.md": README,
        "pyproject.toml": PYPROJECT,
        "docs/db-status.md": DB_STATUS,
        "issues/progress.md": PROGRESS,
        "justfile": JUSTFILE,
        "scripts/__init__.py": SCRIPTS_INIT,
        "scripts/issue_lifecycle.py": ISSUE_LIFECYCLE,
        "scripts/issue_start.py": ISSUE_START,
        "scripts/issue_done.py": ISSUE_DONE,
        "scripts/issue_block.py": ISSUE_BLOCK,
        "tests/test_issue_lifecycle.py": ISSUE_LIFECYCLE_TESTS,
    }

    rendered: dict[str, str] = {}
    for path, content in templates.items():
        for key, value in replacements.items():
            content = content.replace(key, value)
        rendered[path] = content
    return rendered


GITIGNORE = dedent(
    """\
    .DS_Store
    .env
    .mypy_cache/
    .pytest_cache/
    .ruff_cache/
    __pycache__/
    *.py[cod]
    """
)


README = dedent(
    """\
    # {{PROJECT_NAME}}

    {{PRODUCT_PROMISE}}

    ## Agent Workflow

    Start an issue:

    ```bash
    python3 scripts/issue_start.py issues/ready/example.md
    ```

    Finish an issue:

    ```bash
    python3 scripts/issue_done.py issues/in_progress/example.md --verified
    ```

    Block an issue:

    ```bash
    python3 scripts/issue_block.py issues/in_progress/example.md
    ```

    ## Checks

    ```bash
    just install
    just check
    ```
    """
)


PYPROJECT = dedent(
    """\
    [project]
    name = "{{PROJECT_SLUG}}"
    version = "0.1.0"
    description = "Agent-oriented project workspace"
    requires-python = ">=3.11"
    dependencies = []

    [project.optional-dependencies]
    dev = [
        "pytest>=8.2,<9.0",
        "ruff>=0.4.0,<1.0",
    ]

    [tool.pytest.ini_options]
    testpaths = ["tests"]

    [tool.ruff]
    line-length = 100
    target-version = "py311"

    [tool.ruff.lint]
    select = ["E", "F", "I", "UP", "B"]
    """
)


AGENTS = dedent(
    """\
    # AGENTS.md

    ## Mission
    {{PRODUCT_PROMISE}}

    ## Source Of Truth
    Read these in order:
    1. AGENTS.md
    2. docs/db-status.md
    3. docs/planning/
    4. The current issue file

    If sources conflict, follow the current issue, then AGENTS.md, then planning docs.

    ## Non-Negotiables
    - Implement exactly one issue at a time.
    - Use the issue lifecycle scripts instead of moving issue files manually.
    - Write or update tests before implementation when behavior changes.
    - Run tests before finishing.
    - Do not commit real secrets.
    - Do not weaken or delete tests to make them pass.
    - Do not create broad abstractions before they are needed.

    ## Database
    - Read docs/db-status.md before any schema work.
    - Never commit database passwords, service role keys, access tokens, or raw connection strings.
    - If a task changes schema, add migrations and update docs/db-status.md after verification.

    ## Done Definition
    An issue is done only when:
    - Acceptance criteria are met.
    - Tests pass locally.
    - Relevant docs or examples are updated.
    - Changed files are summarized in the issue.
    - Known risks or follow-ups are written in the issue.

    ## Issue Lifecycle
    Issue files live in:
    - `issues/ready/` - not started.
    - `issues/in_progress/` - currently being worked.
    - `issues/done/` - completed and verified.
    - `issues/blocked/` - blocked by missing access, dependency, or decision.

    For every issue implementation session:
    1. Before coding, run `python3 scripts/issue_start.py <issue-path>`.
    2. Work only that issue.
    3. Before finishing, update the issue file with:
       - changed files summary
       - verification commands and results
       - acceptance criteria pass/fail
       - risks or follow-ups
    4. Run required verification, including `just check` unless explicitly blocked.
    5. When done, run `python3 scripts/issue_done.py <issue-path> --verified`.
    6. Update `issues/progress.md`.
    7. Commit the issue movement and implementation together unless the user asks otherwise.

    If an issue cannot be completed:
    1. Update the issue file with `Blocked`, `Attempted steps`, `User action needed`, and `Verification` sections.
    2. Run `python3 scripts/issue_block.py <issue-path>`.
    3. Update `issues/progress.md`.

    Do not manually move issue files unless a lifecycle script is broken.
    """
)


DB_STATUS = dedent(
    """\
    # Database Status

    Last updated: not configured

    ## Project

    - Project name: {{PROJECT_NAME}}
    - Project slug: `{{PROJECT_SLUG}}`
    - Supabase project ref: `{{SUPABASE_PROJECT_REF}}`
    - Supabase URL: `{{SUPABASE_URL}}`
    - Repo linked: no

    Never commit database passwords, service role keys, access tokens, generated local secret files, or raw connection strings.

    ## Current Schema State

    - Last local migration: none
    - Last remote migration: none
    - Local and remote migrations match: not verified
    - Application tables: none
    - Seed data: none

    ## Agent Workflow

    For issues that change database schema:

    1. Read this file before coding.
    2. Add or update migrations.
    3. Add or update tests that verify migration-critical behavior where practical.
    4. Run `just check`.
    5. If the issue requires remote DB configuration, push migrations.
    6. Verify remote migration status.
    7. Update this file with the new migration version, schema summary, verification status, and follow-ups.
    8. Update `issues/progress.md` with a short work-log entry.

    For issues that do not change database schema:

    - Do not change migrations.
    - Do not push database changes.
    - Leave this file unchanged unless DB status or verification changed.
    """
)


PROGRESS = dedent(
    """\
    # Progress

    This document is the project work log. Add a short dated entry after each completed or blocked issue.
    """
)


JUSTFILE = dedent(
    """\
    set shell := ["bash", "-uc"]
    venv := env_var_or_default("AGENT_TEMPLATE_VENV", "/tmp/{{PROJECT_SLUG}}-venv")
    python := venv + "/bin/python"

    install:
        python3 -m venv {{venv}}
        {{python}} -m pip install --upgrade pip
        {{python}} -m pip install -e ".[dev]"

    format:
        {{python}} -m ruff format tests scripts

    format-check:
        {{python}} -m ruff format --check tests scripts

    lint:
        {{python}} -m ruff check tests scripts

    lint-fix:
        {{python}} -m ruff check --fix tests scripts

    test:
        {{python}} -m pytest -q

    check:
        just format-check
        just lint
        just test
    """
)


SCRIPTS_INIT = '"""Project maintenance scripts."""\n'


ISSUE_START = dedent(
    """\
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from scripts.issue_lifecycle import main_start

    if __name__ == "__main__":
        raise SystemExit(main_start())
    """
)


ISSUE_DONE = dedent(
    """\
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from scripts.issue_lifecycle import main_done

    if __name__ == "__main__":
        raise SystemExit(main_done())
    """
)


ISSUE_BLOCK = dedent(
    """\
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from scripts.issue_lifecycle import main_block

    if __name__ == "__main__":
        raise SystemExit(main_block())
    """
)


ISSUE_LIFECYCLE = dedent(
    """\
    from __future__ import annotations

    import argparse
    import re
    import sys
    from dataclasses import dataclass
    from pathlib import Path

    ISSUES_DIR = Path("issues")
    READY_DIR = ISSUES_DIR / "ready"
    IN_PROGRESS_DIR = ISSUES_DIR / "in_progress"
    DONE_DIR = ISSUES_DIR / "done"
    BLOCKED_DIR = ISSUES_DIR / "blocked"
    ISSUE_DIRS = (READY_DIR, IN_PROGRESS_DIR, DONE_DIR, BLOCKED_DIR)
    DONE_REQUIRED_HEADINGS = (
        "Changed files",
        "Verification",
        "Acceptance criteria",
        "Risks",
    )
    BLOCKED_REQUIRED_HEADINGS = (
        "Blocked",
        "Attempted steps",
        "User action needed",
        "Verification",
    )


    class IssueLifecycleError(RuntimeError):
        pass


    @dataclass(frozen=True)
    class MoveResult:
        source: Path
        destination: Path
        status: str


    def ensure_issue_dirs() -> None:
        for directory in ISSUE_DIRS:
            directory.mkdir(parents=True, exist_ok=True)
            gitkeep = directory / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.write_text("", encoding="utf-8")


    def start_issue(issue_path: Path) -> MoveResult:
        ensure_issue_dirs()
        source = _resolve_issue_path(issue_path)
        _require_parent(source, READY_DIR)
        _require_no_other_in_progress()
        destination = (Path.cwd() / IN_PROGRESS_DIR / source.name).resolve()
        _move_with_status(source, destination, "in_progress")
        return MoveResult(source=source, destination=destination, status="in_progress")


    def complete_issue(issue_path: Path, *, verified: bool) -> MoveResult:
        ensure_issue_dirs()
        source = _resolve_issue_path(issue_path)
        _require_parent(source, IN_PROGRESS_DIR)
        if not verified:
            raise IssueLifecycleError("Refusing to mark done without --verified after checks pass.")
        text = source.read_text(encoding="utf-8")
        _require_headings(text, DONE_REQUIRED_HEADINGS, "done")
        destination = (Path.cwd() / DONE_DIR / source.name).resolve()
        _move_with_status(source, destination, "done")
        return MoveResult(source=source, destination=destination, status="done")


    def block_issue(issue_path: Path) -> MoveResult:
        ensure_issue_dirs()
        source = _resolve_issue_path(issue_path)
        _require_parent(source, IN_PROGRESS_DIR)
        text = source.read_text(encoding="utf-8")
        _require_headings(text, BLOCKED_REQUIRED_HEADINGS, "blocked")
        destination = (Path.cwd() / BLOCKED_DIR / source.name).resolve()
        _move_with_status(source, destination, "blocked")
        return MoveResult(source=source, destination=destination, status="blocked")


    def _resolve_issue_path(issue_path: Path) -> Path:
        path = issue_path.expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        path = path.resolve()
        if not path.exists():
            raise IssueLifecycleError(f"Issue file does not exist: {issue_path}")
        if path.suffix != ".md":
            raise IssueLifecycleError(f"Issue file must be a markdown file: {issue_path}")
        return path


    def _require_parent(path: Path, expected_parent: Path) -> None:
        expected = (Path.cwd() / expected_parent).resolve()
        if path.parent != expected:
            raise IssueLifecycleError(f"Expected issue under {expected_parent}/, got {path}")


    def _require_no_other_in_progress() -> None:
        existing = [
            path for path in (Path.cwd() / IN_PROGRESS_DIR).glob("*.md") if path.name != ".gitkeep"
        ]
        if existing:
            names = ", ".join(path.name for path in existing)
            raise IssueLifecycleError(f"Another issue is already in progress: {names}")


    def _move_with_status(source: Path, destination: Path, status: str) -> None:
        if destination.exists():
            raise IssueLifecycleError(f"Destination already exists: {destination}")
        text = source.read_text(encoding="utf-8")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(_replace_status(text, status), encoding="utf-8")
        source.unlink()


    def _replace_status(text: str, status: str) -> str:
        if text.startswith("---\\n"):
            end = text.find("\\n---", 4)
            if end != -1:
                frontmatter = text[:end]
                rest = text[end:]
                if re.search(r"(?m)^status:\\s*.*$", frontmatter):
                    frontmatter = re.sub(r"(?m)^status:\\s*.*$", f"status: {status}", frontmatter)
                else:
                    frontmatter = f"{frontmatter}\\nstatus: {status}"
                return f"{frontmatter}{rest}"

        if re.search(r"(?m)^status:\\s*.*$", text):
            return re.sub(r"(?m)^status:\\s*.*$", f"status: {status}", text, count=1)

        return f"---\\nstatus: {status}\\n---\\n{text}"


    def _require_headings(text: str, headings: tuple[str, ...], target_status: str) -> None:
        missing = [
            heading
            for heading in headings
            if not re.search(rf"(?im)^#+\\s+{re.escape(heading)}\\b", text)
        ]
        if missing:
            joined = ", ".join(missing)
            raise IssueLifecycleError(
                f"Refusing to mark {target_status}; missing required section(s): {joined}"
            )


    def main_start(argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description="Move an issue from ready to in_progress.")
        parser.add_argument("issue", type=Path)
        args = parser.parse_args(argv)
        return _run(lambda: start_issue(args.issue))


    def main_done(argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description="Move an issue from in_progress to done.")
        parser.add_argument("issue", type=Path)
        parser.add_argument(
            "--verified",
            action="store_true",
            help="Required acknowledgement that issue verification passed.",
        )
        args = parser.parse_args(argv)
        return _run(lambda: complete_issue(args.issue, verified=args.verified))


    def main_block(argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description="Move an issue from in_progress to blocked.")
        parser.add_argument("issue", type=Path)
        args = parser.parse_args(argv)
        return _run(lambda: block_issue(args.issue))


    def _run(action: object) -> int:
        try:
            result = action()
        except IssueLifecycleError as error:
            print(f"error: {error}", file=sys.stderr)
            return 1

        if isinstance(result, MoveResult):
            print(f"{result.source} -> {result.destination} ({result.status})")
        return 0
    """
)


ISSUE_LIFECYCLE_TESTS = dedent(
    '''\
    from pathlib import Path

    import pytest

    from scripts.issue_lifecycle import (
        IssueLifecycleError,
        block_issue,
        complete_issue,
        start_issue,
    )


    def write_issue(path: Path, status: str = "ready", body: str = "# Test Issue\\n") -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\\nstatus: {status}\\n---\\n{body}", encoding="utf-8")


    def test_start_issue_moves_ready_issue_to_in_progress(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        issue = tmp_path / "issues" / "ready" / "example.md"
        write_issue(issue)

        result = start_issue(Path("issues/ready/example.md"))

        assert result.destination == (tmp_path / "issues" / "in_progress" / "example.md").resolve()
        assert not issue.exists()
        assert "status: in_progress" in result.destination.read_text(encoding="utf-8")


    def test_start_issue_refuses_when_another_issue_is_in_progress(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        write_issue(tmp_path / "issues" / "ready" / "example.md")
        write_issue(tmp_path / "issues" / "in_progress" / "other.md", status="in_progress")

        with pytest.raises(IssueLifecycleError, match="already in progress"):
            start_issue(Path("issues/ready/example.md"))


    def test_complete_issue_requires_verified_flag(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        issue = tmp_path / "issues" / "in_progress" / "example.md"
        write_issue(issue, status="in_progress", body=done_body())

        with pytest.raises(IssueLifecycleError, match="--verified"):
            complete_issue(Path("issues/in_progress/example.md"), verified=False)


    def test_complete_issue_moves_to_done_when_sections_exist(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        issue = tmp_path / "issues" / "in_progress" / "example.md"
        write_issue(issue, status="in_progress", body=done_body())

        result = complete_issue(Path("issues/in_progress/example.md"), verified=True)

        assert result.destination == (tmp_path / "issues" / "done" / "example.md").resolve()
        assert not issue.exists()
        assert "status: done" in result.destination.read_text(encoding="utf-8")


    def test_block_issue_requires_blocked_sections(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        issue = tmp_path / "issues" / "in_progress" / "example.md"
        write_issue(issue, status="in_progress")

        with pytest.raises(IssueLifecycleError, match="missing required section"):
            block_issue(Path("issues/in_progress/example.md"))


    def test_block_issue_moves_to_blocked_when_sections_exist(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        issue = tmp_path / "issues" / "in_progress" / "example.md"
        write_issue(issue, status="in_progress", body=blocked_body())

        result = block_issue(Path("issues/in_progress/example.md"))

        assert result.destination == (tmp_path / "issues" / "blocked" / "example.md").resolve()
        assert not issue.exists()
        assert "status: blocked" in result.destination.read_text(encoding="utf-8")


    def done_body() -> str:
        return """# Test Issue

    ## Changed files
    None.

    ## Verification
    `just check` passed.

    ## Acceptance criteria
    Pass.

    ## Risks
    None.
    """


    def blocked_body() -> str:
        return """# Test Issue

    ## Blocked
    Missing access.

    ## Attempted steps
    Tried the configured command.

    ## User action needed
    Grant access.

    ## Verification
    Not run.
    """
    '''
)


if __name__ == "__main__":
    raise SystemExit(main())
