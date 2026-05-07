# Agent Project Template

This is mise en place for agentic engineering.

Not a framework. Not a manifesto. A prep station.

When I start a project, I do not want a coding agent wandering around the repo with a head full of vibes and a context window full of yesterday's mistakes. I want the work broken down, labeled, ticketed, and ready for service. This repo gives me that.

The core script is [bootstrap_agent_project.py](/Users/dylanhardenbergh/Desktop/Projects/agent-project-template/bootstrap_agent_project.py). It lays down the structure I use to turn an idea into a PRD, a PRD into issues, and issues into controlled agent runs.

## The Line

The workflow is:

```text
G-Stack Office Hours-style project quiz
  -> PRD
  -> vertical issues
  -> issue lifecycle
  -> independent agent runs or Ralph loops
```

That is the whole kitchen.

The agent does not get one heroic prompt and a prayer. It gets product context, a small ticket, rules on the wall, and a test command that tells it whether the plate goes out or comes back.

The reason is simple: chat is a terrible place to store truth. It is smoky, crowded, and too easy to misremember. A repo is better. `AGENTS.md`, `docs/planning/`, `issues/`, `issues/progress.md`, tests, and git history become the memory. The agent can leave, come back fresh, and still know what happened.

## Office Hours First

I start with an Office Hours-style project interview, usually with Garry Tan / YC-style G-Stack Office Hours. Before code, before schema, before some grand architecture diagram, the agent has to help pin down the product.

Who is this for? What hurts? What do they do today instead? What is the smallest useful wedge? What are we absolutely not building yet?

This is not theater. Most software rot starts here. If the idea is mush, the code will be mush with imports. The interview forces the product to stand up straight before the agent starts chopping.

The output should be product clarity:

- the user
- the painful problem
- the current workaround
- the first useful wedge
- the non-goals
- the success criteria
- the assumptions that are still just guesses

That becomes durable context. Not a vibe from a chat thread. A file the next agent can read.

## The PRD

The PRD lives under `docs/planning/`.

It is not there to impress anyone. It is there so the repo can remember what the product is trying to do after the original conversation is gone.

A good PRD is sharp enough to cut issues from. It should cover the product promise, target user, use cases, non-goals, acceptance criteria, risks, and first milestone. It should not try to cosplay as a complete architecture. Architecture comes from pressure. The PRD just gives the pressure a direction.

This is especially important for Ralph loops and fresh agent sessions. A new session should be able to walk in cold, read the PRD, and understand the point of the work without needing the transcript that created it.

## Vertical Issues

The PRD gets broken into markdown issues under `issues/ready/`.

Each issue should be a vertical slice: one narrow, end-to-end piece of behavior that can be built, tested, reviewed, and moved to done.

Bad issue: "Build the billing backend."

Better issue: "User can update the billing email."

The second one has a user, a behavior, a way to verify it, and a natural boundary. It might touch UI, API, permissions, persistence, email, and tests. Good. Real product work cuts across layers. Agents need that pressure or they happily polish one layer while the feature remains useless.

Vertical slices work because they:

- keep the agent pointed at one outcome
- reduce context load per run
- create natural review checkpoints
- force implementation to connect the pieces that matter
- make progress visible

They are not free:

- slicing takes thought
- shared infrastructure can be awkward to fit
- tiny slices create overhead
- vague slices make confident agents do dumb work faster

The rule I use: an issue should produce one reviewable behavior. If nobody can tell whether it works without reading the agent's mind, it is not sliced well enough.

## Issue Lifecycle

The generated project uses local markdown files as the issue tracker.

Issues move through four folders:

- `issues/ready/` - prepped and ready
- `issues/in_progress/` - the one ticket on the station
- `issues/done/` - completed and verified
- `issues/blocked/` - waiting on access, a decision, or a dependency

The lifecycle scripts enforce the movement:

- `issue_start.py` moves one ready issue into progress and refuses to start if another issue is already active.
- `issue_done.py` moves an in-progress issue to done only when `--verified` is passed and required completion sections exist.
- `issue_block.py` moves an in-progress issue to blocked only when required blocked sections exist.
- `issue_lifecycle.py` contains the shared lifecycle logic and validation.

This is stricter than dragging files around by hand, and that is the point. Agents are good at sounding finished. The scripts make them leave evidence: changed files, verification, acceptance criteria, risks, blocked reason, attempted steps, and user action needed.

## Ralph Loops

A Ralph loop is a long-running agentic engineering pattern popularized by Geoffrey Huntley. The important move is that the loop is outside the agent session. A runner starts a fresh coding agent over and over. Each new session reloads state from the repo.

That fresh context is the whole trick.

One endless chat eventually becomes a walk-in fridge full of unlabeled containers. You think you know what is in there. You do not. A Ralph loop keeps the working memory clean. The repo holds the truth. The agent reads the rules, handles one issue, runs checks, updates files, and exits. The next pass starts fresh.

In this structure, one Ralph iteration should usually mean one issue. One ticket, one behavior, one verification path.

A healthy Ralph loop needs:

- crisp issues in `issues/ready/`
- one active issue in `issues/in_progress/`
- strong rules in `AGENTS.md`
- a reliable `just check`
- progress written to `issues/progress.md`
- a hard stop when the same failure repeats

The danger is obvious: a loop amplifies whatever you feed it. Bad PRD, bad issues, weak checks, lazy rules: the loop will not save you. It will just plate the wrong dish faster. Fix the prep. Improve the PRD, rewrite the issue, tighten `AGENTS.md`, or strengthen verification.

Background reading:

- [Geoffrey Huntley, Ralph Wiggum as a software engineer](https://ghuntley.com/ralph/)
- [Ralph Loop project](https://ralphloop.sh/)
- [ZeroSync technical deep dive](https://www.zerosync.co/blog/ralph-loop-technical-deep-dive)
- [Christopher Lee, Ralph Loops](https://chrisjunlee.com/ralph-loops)

## Feature-Based Development

This workflow is not only for starting from zero. It works just as well for a feature sprint inside an existing application.

The loop gets smaller:

```text
Feature Office Hours
  -> feature PRD
  -> vertical feature issues
  -> issue lifecycle
  -> independent agent runs or Ralph loops
```

The questions change. You are no longer asking, "What should this product be?" You are asking, "What behavior should change, what must stay intact, and where are the sharp edges?"

I still use Office Hours for features because feature requests lie by omission. "Add billing settings" sounds harmless until you find roles, invoices, webhooks, trials, old customers, mobile layout, and some job that runs at 2:00 a.m. with strong opinions.

A feature PRD should live in `docs/planning/` and stay scoped to the change. It should cover:

- current behavior
- desired behavior
- affected users or roles
- impacted screens, commands, APIs, jobs, or data models
- non-goals
- acceptance criteria
- existing behavior that must not regress
- rollout, migration, or compatibility notes
- open product or technical decisions

Feature slices should still be vertical. "Admin can resend an invitation email" is better than "add invite endpoint" because the former is a behavior. It naturally pulls in permissions, API, email delivery, UI state, and tests.

Feature work has more hidden coupling than greenfield work. That is the tax. A feature issue should name the likely affected areas and the behaviors that must keep working. Give the agent enough context to avoid breaking the room, but not so much that every run turns into a full-codebase renovation.

For a feature Ralph loop, one issue per fresh session is still the right default. Stop when the agent finds unclear behavior, broad refactoring outside the feature PRD, repeated test failures, or a migration/rollout decision that needs a human.

The distinction:

- full-application workflow creates product clarity before building the initial system
- feature workflow creates change clarity before modifying an existing system

Same mechanics. Smaller PRD. Sharper regression notes. Less tolerance for wandering.

## What The Python Script Does

[bootstrap_agent_project.py](/Users/dylanhardenbergh/Desktop/Projects/agent-project-template/bootstrap_agent_project.py) is a small Python bootstrapper.

It does not call an LLM. It does not write your PRD. It does not slice your issues. It does not connect to Supabase. It does not run Ralph loops.

It sets the station.

Specifically, the script:

- parses project metadata from CLI flags
- creates the target directory if needed
- renders template files with the project name, slug, product promise, and optional Supabase metadata
- creates the issue lifecycle folders
- writes `.gitkeep` placeholders for empty tracked folders
- writes lifecycle scripts and tests into the generated project
- optionally runs `git init`
- refuses to overwrite existing template-owned files unless `--force` is passed

The script is deliberately boring. Boring is good here. Boring means the next project starts with the same clean prep.

## What It Sets Up

Given a target directory, the script creates this structure:

```text
.
+-- AGENTS.md
+-- README.md
+-- docs/
|   +-- db-status.md
|   +-- planning/
+-- issues/
|   +-- blocked/
|   +-- done/
|   +-- in_progress/
|   +-- ready/
|   +-- progress.md
+-- scripts/
|   +-- __init__.py
|   +-- issue_block.py
|   +-- issue_done.py
|   +-- issue_lifecycle.py
|   +-- issue_start.py
+-- tests/
|   +-- test_issue_lifecycle.py
+-- justfile
+-- pyproject.toml
+-- .gitignore
```

What each part is for:

- `AGENTS.md` is the rules on the wall for coding agents.
- `docs/planning/` holds PRDs, feature briefs, design notes, and planning context.
- `docs/db-status.md` records database assumptions and migration status.
- `issues/ready/` contains work that is ready to run.
- `issues/in_progress/` contains the single active issue.
- `issues/done/` contains completed and verified work.
- `issues/blocked/` contains work waiting on access, a dependency, or a decision.
- `issues/progress.md` is the work log.
- `scripts/issue_*.py` enforce issue state transitions.
- `tests/test_issue_lifecycle.py` verifies the lifecycle scripts.
- `justfile` gives the project standard install, format, lint, test, and check commands.
- `pyproject.toml` defines the minimal Python project and dev dependencies.
- `.gitignore` keeps local junk out of the repo.

## Why It Sets Things Up This Way

The whole structure is about context control.

`AGENTS.md` saves you from repeating the rules every time. `docs/planning/` saves the product intent. `issues/` turns ambition into tickets small enough to execute. `issues/progress.md` gives future sessions a short service history. `just check` gives the agent a pass/fail signal that is not based on confidence or charm.

Local markdown issues are intentionally simple. Agents can read them. Agents can edit them. They work without API credentials. Codex, Claude Code, Cursor, or a shell-based Ralph runner can all use the same files. If you want GitHub Issues or Linear later, fine. Mirror them. Do not make the external tracker the thing the loop depends on.

One active issue is also intentional. Context sprawl is where agent runs go to die. If the active issue is too large, do not ask the agent to be smarter. Cut the issue smaller.

## How To Set Everything Up

Prerequisites on the machine running the bootstrap script:

- Python 3.11 or newer
- `git`, if you want `--git-init`

Prerequisites inside each generated project:

- Python 3.11 or newer
- [`just`](https://github.com/casey/just), for `just install` and `just check`

Create a new project:

```bash
python3 bootstrap_agent_project.py /path/to/new-project \
  --name "New Project" \
  --slug new-project \
  --product-promise "A short sentence describing what this product is meant to do." \
  --git-init
```

Optional Supabase metadata:

```bash
python3 bootstrap_agent_project.py /path/to/new-project \
  --name "New Project" \
  --slug new-project \
  --product-promise "A short sentence describing what this product is meant to do." \
  --supabase-ref your_project_ref \
  --supabase-url https://your_project_ref.supabase.co
```

Then enter the generated repo:

```bash
cd /path/to/new-project
just install
just check
```

Useful flags:

- `--force` overwrites files the template owns. Use this carefully on an existing project.
- `--git-init` runs `git init` in the target directory when it is not already a git repo.

The generated `just install` recipe creates a virtual environment under `/tmp/<project-slug>-venv` by default. Override that location with `AGENT_TEMPLATE_VENV` if needed:

```bash
AGENT_TEMPLATE_VENV=.venv just install
```

## How To Execute Work In A Generated Project

After setup, the normal flow is:

1. Run an Office Hours-style project quiz.
2. Save the resulting PRD under `docs/planning/`.
3. Convert the PRD into vertical issues under `issues/ready/`.
4. Run one issue manually or let a Ralph runner execute one issue per fresh session.
5. Keep `issues/progress.md` updated after done or blocked work.

The concrete issue lifecycle commands are:

```bash
python3 scripts/issue_start.py issues/ready/example.md
python3 scripts/issue_done.py issues/in_progress/example.md --verified
python3 scripts/issue_block.py issues/in_progress/example.md
```

The main verification command is:

```bash
just check
```

As the project grows, `just check` should grow with it. If browser tests, type checks, migrations, or security checks are required for done work, they belong in the verification path. Do not make the agent guess what "done" tastes like.

For feature-based work in an existing app, use the same path with a narrower planning doc:

1. Run Office Hours around the feature or feature set.
2. Save a feature PRD under `docs/planning/`.
3. Cut vertical feature issues into `issues/ready/`.
4. Execute one issue at a time, manually or through a Ralph loop.
5. Stop and revise the feature PRD if implementation exposes unclear behavior, unexpected coupling, or regression risk.

## Updating An Existing Project

You can run this against an existing directory, but the script refuses to overwrite template-owned files unless you pass `--force`. For existing repos, bootstrap into a temporary directory first, then copy over the pieces you want.

Use `--force` only when you are comfortable replacing:

- root `README.md`
- `AGENTS.md`
- `pyproject.toml`
- `justfile`
- issue lifecycle scripts and tests
- generated docs under `docs/`

## Current Limits

This template is intentionally minimal:

- It does not generate the PRD for you.
- It does not convert the PRD into issues by itself.
- It does not include a built-in Ralph runner yet.
- It does not integrate directly with GitHub Issues, Linear, Jira, or Supabase.
- It assumes Python tooling for the lifecycle scripts, even if the target app uses another stack.

Those limits are mostly intentional. This repo gives you the station, the labels, the tickets, and the rules. Product discovery, issue slicing, and execution loops can be handled by whichever agent tooling is best for the job.
