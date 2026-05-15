# Context Is King

This is mise en place for autonomous agentic coding.

Not a framework. Not a dashboard. Not another place for a coding agent to hide bad state behind confident prose.

This repo is a file-system-driven coding loop. The filesystem is the control plane. The agent is disposable. If the agent crashes, gets confused, loses the thread, or walks into the context-window fog, the repo should still know exactly where the work stands.

The core script is [bootstrap_agent_project.py](/Users/dylanhardenbergh/Desktop/Projects/agent-project-template/bootstrap_agent_project.py). It lays down the project structure I use to turn product context into a PRD, a PRD into vertical issues, and issues into controlled agent runs.

The larger architecture is simple:

```text
Office Hours-style product or feature quiz
  -> PRD
  -> vertical issues
  -> file-system state machine
  -> validation and browser audit
  -> next-issue grooming
  -> independent agent runs or Ralph loops
```

The point is not to ask an agent to "build the app" and hope. Hope is not a system. The point is to keep state visible, keep context small, and make the agent prove the work before the next ticket goes out.

## Why This Exists

LLMs are powerful, but their memory is a rented room. The longer the session runs, the more the context window fills with half-remembered decisions, stale assumptions, and whatever just happened five minutes ago.

So I move memory out of the chat and into files:

- `AGENTS.md` for durable rules
- `docs/planning/` for PRDs and feature briefs
- `issues/` for task state
- `issues/progress.md` for the transaction log
- `justfile` for repeatable validation
- `audit.md` for user-facing verification notes when browser testing matters

The agent can leave. Another agent can arrive cold. The work should still be readable.

## The File-System State Machine

The generated project uses local markdown files as the issue tracker. No database. No SaaS dependency. No mystery queue living behind an API token.

Issues move through physical folders:

- `issues/ready/` - the backlog; prepped work waiting to be picked up
- `issues/in_progress/` - the active lock; one issue on the station
- `issues/done/` - verified history; completed work that future agents can inspect
- `issues/blocked/` - the escape hatch; work that needs access, a decision, or a human

The folder move is the state transition. Same-filesystem renames give you a simple, observable lock. If the machine goes down, you do not need to query a service to know what happened. You look at the folders.

The lifecycle scripts enforce that movement:

- `issue_start.py` moves one ready issue into progress and refuses to start if another issue is already active.
- `issue_done.py` moves an in-progress issue to done only when `--verified` is passed and required completion sections exist.
- `issue_block.py` moves an in-progress issue to blocked only when required blocked sections exist.
- `issue_lifecycle.py` contains the shared validation logic.

This is stricter than dragging files around by hand. Good. Agents are excellent at sounding finished. The scripts make them leave evidence.

## Core Context Files

Every serious agent run should start by loading a small, explicit set of files:

- `AGENTS.md`
- the relevant PRD or feature brief in `docs/planning/`
- `docs/db-status.md` when database work is possible
- `issues/progress.md`
- the current issue file

That set is the source of truth. Not the chat transcript. Not the agent's memory. Not a vague recollection of what the user said earlier.

This keeps the context window clean. The agent gets enough information to do the job, but not the entire attic. If the issue requires more context, that is a sign to add the missing facts to the issue or PRD, not to stuff another 30 files into the prompt.

## Progress As A Transaction Log

`issues/progress.md` is the work log. Treat it like a transaction log, not a diary.

It should record:

- issue started
- issue completed
- issue blocked
- verification run
- notable handoff or risk
- next human action needed

The current issue can hold detailed notes. `progress.md` should stay skimmable. A future agent should be able to read it quickly and understand the service history: what shipped, what failed, what is waiting, and where the bodies are buried.

## Office Hours First

I start with an Office Hours-style interview, usually Garry Tan / YC-style G-Stack Office Hours.

For a new product, the agent helps pin down the user, the pain, the current workaround, the narrowest useful wedge, and the success criteria.

For a feature sprint, the same move applies. The questions shift from "what should this product be?" to "what behavior should change, what must not regress, and where are the sharp edges?"

This is not ceremony. Most bad agent work starts before code. If the product idea is mush, the code will be mush with imports.

The output should be product clarity:

- who this is for
- what hurts
- what exists today
- what must change
- what should not be built yet
- what success looks like
- what assumptions are still just guesses

That clarity goes into files. The next session should not need the original conversation to understand the job.

## PRDs And Feature Briefs

Planning docs live under `docs/planning/`.

For a full application, write a PRD. It should cover the product promise, target user, use cases, non-goals, acceptance criteria, risks, and first milestone.

For an existing application, write a feature PRD. It should be smaller and sharper:

- current behavior
- desired behavior
- affected users or roles
- impacted screens, commands, APIs, jobs, or data models
- non-goals
- acceptance criteria
- existing behavior that must not regress
- rollout, migration, or compatibility notes
- open product or technical decisions

The PRD is not there to impress anyone. It is there so the repo remembers what the work is trying to do after the original chat is gone.

## Vertical Issues

The PRD gets cut into markdown issues under `issues/ready/`.

Each issue should be a vertical slice: one narrow, end-to-end behavior that can be built, tested, reviewed, and moved to done.

Bad issue: "Build the billing backend."

Better issue: "User can update the billing email."

The better issue has a user, a behavior, and a verification path. It may touch UI, API, permissions, persistence, and tests. Good. Real product work cuts across layers. Agents need that pressure or they happily polish one layer while the feature remains useless.

Vertical slices work because they:

- keep the agent pointed at one outcome
- reduce context load per run
- create natural review checkpoints
- force the implementation to connect the pieces that matter
- make progress visible

They are not free:

- slicing takes judgment
- shared infrastructure can be awkward to fit
- tiny slices create overhead
- vague slices make confident agents do dumb work faster

The rule I use: an issue should produce one reviewable behavior. If nobody can tell whether it works without reading the agent's mind, it is not sliced well enough.

## Execution Loop

The execution loop is deliberately plain:

1. Load the core markdown files.
2. Move one issue from `issues/ready/` to `issues/in_progress/`.
3. Implement only that issue.
4. Run standardized checks through `just`.
5. Run browser verification when user-facing behavior changed.
6. Write the evidence back into the issue and audit files.
7. Move the issue to `done` or `blocked`.
8. Update `issues/progress.md`.
9. Exit cleanly so the next session starts fresh.

The key is that validation is not based on the agent feeling good about the code. Validation is a command.

```bash
just check
```

As the project grows, `just check` should grow with it. If type checks, browser tests, migrations, seed checks, or security checks are required for done work, they belong in the verification path.

## Browser Audit

When the issue changes user-facing behavior, code checks are not enough. The agent should verify the behavior in a browser and leave a paper trail.

The intended pattern is:

- `test.md` describes the user-facing flows that need browser verification.
- The agent uses Codex Chrome or another browser runner to exercise those flows.
- `audit.md` records what was tested, what passed, what failed, screenshots or references when useful, and what remains risky.

Do not confuse agent audit with human approval. `audit.md` is the agent's evidence log. It says what the agent observed. It does not mean a human signed off unless a human actually did.

The current bootstrap script does not create `test.md` or `audit.md` yet. The architecture expects them for serious UI work, and future versions of the template should add them.

## Inter-Session Grooming

This is the handoff that keeps the next agent from walking in cold and hallucinating contracts.

Before closing an issue, the agent should inspect the next ready issue and add verified handoff notes when the current work created something the next issue depends on.

Examples:

- API route created
- import path
- exported function name
- request or response schema
- database table or column
- environment variable
- test helper

The word "verified" matters. Grooming is not a place for speculation. The agent should only write facts backed by code and passing checks.

A good handoff section in the next issue might include:

```markdown
## Verified handoff from previous issue

- Created API route: `POST /api/invitations`
- Request schema: `{ email: string, role: "admin" | "member" }`
- Response schema: `{ invitationId: string }`
- Import path: `src/features/invitations/api.ts`
- Verified by: `just check`
```

This solves one of the nastiest agent-loop problems: cold-start dependency drift. The next session does not have to rediscover the contract or make one up. The plate is labeled.

## Ralph Loops

A Ralph loop is a long-running agentic engineering pattern popularized by Geoffrey Huntley. The important move is that the loop runs outside the agent session. A runner starts a fresh coding agent over and over. Each new session reloads state from the repo.

That fresh context is the trick.

One endless chat eventually becomes a walk-in fridge full of unlabeled containers. You think you know what is in there. You do not. A Ralph loop keeps working memory clean. The repo holds the truth.

In this structure, one Ralph iteration should usually mean one issue. One ticket, one behavior, one verification path.

A healthy Ralph loop needs:

- crisp issues in `issues/ready/`
- one active issue in `issues/in_progress/`
- strong rules in `AGENTS.md`
- a reliable `just check`
- browser audit when the issue touches user-facing behavior
- progress written to `issues/progress.md`
- a hard stop when the same failure repeats

The danger is obvious: a loop amplifies whatever you feed it. Bad PRD, bad issues, weak checks, lazy rules: the loop will not save you. It will just plate the wrong dish faster. Fix the prep.

Background reading:

- [Geoffrey Huntley, Ralph Wiggum as a software engineer](https://ghuntley.com/ralph/)
- [Ralph Loop project](https://ralphloop.sh/)
- [ZeroSync technical deep dive](https://www.zerosync.co/blog/ralph-loop-technical-deep-dive)
- [Christopher Lee, Ralph Loops](https://chrisjunlee.com/ralph-loops)

## The Foreman Script

The foreman is the automation layer: a lean script that watches the queue, starts agent runs, and routes issues based on verified outcomes.

The shape is:

1. Look for the next markdown issue in `issues/ready/`.
2. Move it to `issues/in_progress/` as the lock.
3. Start the agent CLI with the current issue path.
4. Let the agent implement, validate, audit, groom the next issue, and exit.
5. Move the issue to `issues/done/` or `issues/blocked/`.
6. Loop back to the queue.

The foreman should not mark an issue done on exit code alone. Exit code is just one signal. Done should require:

- required issue sections exist
- required checks passed
- browser audit exists when required
- `issues/progress.md` was updated
- the lifecycle script accepts the transition

Blocked should be a first-class path, not an embarrassment. If the same failure repeats, if a product decision is missing, or if the issue requires a broad refactor outside its scope, the foreman should stop the bleeding and route the issue to `issues/blocked/`.

The current bootstrap script does not ship a foreman runner yet. The generated lifecycle scripts are the core it will sit on.

## What The Python Script Does Today

[bootstrap_agent_project.py](/Users/dylanhardenbergh/Desktop/Projects/agent-project-template/bootstrap_agent_project.py) is a small Python bootstrapper.

It does not call an LLM. It does not write your PRD. It does not slice your issues. It does not connect to Supabase. It does not run Ralph loops. It does not ship the foreman yet.

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
- `issues/progress.md` is the transaction log.
- `scripts/issue_*.py` enforce issue state transitions.
- `tests/test_issue_lifecycle.py` verifies the lifecycle scripts.
- `justfile` gives the project standard install, format, lint, test, and check commands.
- `pyproject.toml` defines the minimal Python project and dev dependencies.
- `.gitignore` keeps local junk out of the repo.

## Why This Shape Works

The whole structure is about context control.

`AGENTS.md` saves you from repeating the rules every time. `docs/planning/` saves product intent. `issues/` turns ambition into tickets small enough to execute. `issues/progress.md` gives future sessions a service history. `just check` gives the agent a pass/fail signal that is not based on confidence or charm.

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

1. Run an Office Hours-style project or feature quiz.
2. Save the resulting PRD or feature brief under `docs/planning/`.
3. Convert that planning doc into vertical issues under `issues/ready/`.
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

## Current Limits

This template currently establishes the workflow skeleton:

- It does not generate the PRD for you.
- It does not convert the PRD into issues by itself.
- It does not create `test.md` or `audit.md` yet.
- It does not include a built-in foreman or Ralph runner yet.
- It does not integrate directly with GitHub Issues, Linear, Jira, or Supabase.
- It assumes Python tooling for the lifecycle scripts, even if the target app uses another stack.

Those limits are mostly intentional for now. This repo gives you the station, the labels, the tickets, and the rules. Product discovery, issue slicing, browser audit, and execution loops can be handled by whichever agent tooling is best for the job.
