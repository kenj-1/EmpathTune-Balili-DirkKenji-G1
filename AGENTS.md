# AGENTS.md — EmpathTune Engineering & Gitflow Operating Rules

This repository (`EmpathTune-Balili-DirkKenji-G1`) follows strict full-stack Django engineering, security, and Gitflow standards for **Project Development 1 (PD1)** and **Project Development 2 (PD2)**. Every coding agent or developer working in this workspace **must** follow the rules below.

---

## 1. Mandatory Pre-Task & Post-Task Workflow (Persistent Project Memory)

1. **Read Context First:** Before modifying any code, configuration, or documentation, read:
   - [`docs/project-context.md`](docs/project-context.md) — System architecture, data models, role-based access rules, and vertical slice specifications.
   - [`docs/ai-work-log.md`](docs/ai-work-log.md) — Append-only chronological ledger of all completed, active, and planned milestones.
2. **Inspect Repository State:** Check `git status`, `git branch -a`, and `git log --oneline -n 10` before starting work to verify the active branch and commit state.
3. **Append-Only Ledger Updates:**
   - Never delete or overwrite historical entries in `docs/ai-work-log.md`.
   - Record every task transition (`Planned` -> `In progress` -> `Complete`) with exact commit hashes, modified file lists, database migrations, and Pull Request references.

---

## 2. Technology Stack & Architecture Constraints

- **Framework:** Full-Stack Django (`Django ORM` + `Django Forms` + `Django Templates`).
  - Do **not** replace server-rendered Django Templates with a separate SPA framework.
  - Maintain the dark **Midnight Indigo** Bootstrap 5.3 theme (`templates/base.html`).
- **Database:** **Supabase PostgreSQL** via `psycopg` configured through environment variables in `config/settings.py`.
  - **Never use SQLite (`db.sqlite3`)** for development, testing, or migrations.
  - All schema and data migrations must be applied cleanly to Supabase PostgreSQL via `python manage.py migrate`.

---

## 3. Security & Secret Hygiene

1. **Zero `.env` Exposure:** Never read, inspect, print, log, or stage `.env`, database passwords, or `SECRET_KEY` values in terminal output, code comments, or documentation.
2. **Clean Tracking:** Ensure `.gitignore` excludes `.env`, `venv/`, `__pycache__/`, and `*.sqlite3`. Keep `requirements.txt` accurate and minimal.
3. **Access Control & Ownership Enforcement:**
   - Unauthenticated users must be redirected to `login` (`@login_required` / `LoginRequiredMixin`).
   - Role boundaries (`listener` vs `curator`) must be enforced on the server side (`CuratorRequiredMixin`, `ListenerRequiredMixin`, and role checks in views) with clear `messages.error` feedback on unauthorized URL access attempts.
   - Personal user records (`ProfileUpdateView`, `SongFeeling` CRUD) must strictly scope queries and mutations to `request.user` so URL/ID tampering cannot view, edit, or delete another user's data.

---

## 4. Strict Gitflow & Commit Discipline

1. **Branch Hierarchy:**
   - `main`: Production/release branch containing only stable, verified increments. **Never commit directly to `main`.**
   - `develop`: Integration branch branched from `main`. All feature branches merge into `develop` via Pull Requests before a release PR merges `develop` -> `main`.
   - `feature/<feature-name>`: Branched from `develop` for each vertical slice:
     - `feature/mood-catalog-management` (Curator `MoodTag` + `Track` catalog management)
     - `feature/personal-song-meanings` (Listener discovery + personal `SongFeeling` CRUD)
   - **Never delete merged feature branches** (local or remote on GitHub); they are required for grading inspection.
2. **Explicit Staging & Incremental Commits:**
   - **Never run blind `git add .` or `git add -A`.** Always stage explicit file paths (`git add <path1> <path2>`).
   - Write clear, conventional commit messages (`feat: ...`, `fix: ...`, `docs: ...`, `test: ...`) that represent logical, incremental units of work.
3. **Preserve PD1 Features:**
   - All Increment 1 (PD1) Account Features—registration with validation/hashing, login/logout, role router & dashboards, and self-only profile editing—must remain intact and functional across all PD2 branches.
