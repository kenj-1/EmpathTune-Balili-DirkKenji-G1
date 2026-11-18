# EmpathTune — Append-Only AI & Development Work Log

> **Ledger Rule:** This file is an **append-only** engineering record for `EmpathTune-Balili-DirkKenji-G1`. Existing historical entries must never be deleted. Append new entries or status updates chronologically as each milestone transitions from `Planned` -> `In progress` -> `Complete`.

---

## Entry 1 — Increment 1 (PD1) Baseline: Authentication, Role Dashboards, & Self-Profile Management

- **Date:** 2026-11-10
- **Branch:** `main` (and branched baseline on `develop`)
- **Commit Range:** `2fcf341` .. `e16c5e9`
- **Status:** `Complete`

### Commit History (PD1 Baseline)
1. `2fcf341` — `feat: initialize Django project structure, requirements, and PostgreSQL configuration`
2. `3bf8359` — `feat: implement CustomUser model with listener and curator roles and apply migrations`
3. `3570275` — `feat: add user registration form, password hashing, validation, and messages`
4. `667ec5f` — `feat: implement login authentication, role-based dashboards, and URL access protection`
5. `e16c5e9` — `feat: implement secure user profile view and self-edit functionality restricted to owner`

### Verified PD1 Deliverables
- **Supabase PostgreSQL Integration:** Configured `DATABASES['default']` using `django.db.backends.postgresql` (`psycopg`) and environment variables loaded from `.env` with `sslmode="require"`.
- **Custom User Model (`accounts.User`):** Added `role` (`listener` / `curator`), `contact_number`, and `bio` with initial migration `accounts/migrations/0001_initial.py`.
- **User Registration (`accounts/signup/`):** `UserRegistrationForm` with case-insensitive unique email validation, password strength validation, automatic password hashing, and Bootstrap-styled error/success alerts.
- **Authentication & Role Routing:** Login (`accounts/login/`), Logout (`accounts/logout/`), and `dashboard_router` (`/`) dispatching users to `/dashboard/listener/` or `/dashboard/curator/` based on role.
- **URL Access Protection & Self-Only Profile Editing:** Server-side role checks preventing cross-role dashboard access with `messages.error` redirects, and `ProfileUpdateView.get_object()` strictly returning `self.request.user`.

---

## Entry 2 — Increment 2 (PD2), Feature 1: Curator Mood & Track Catalog Management

- **Date:** 2026-11-18
- **Branch:** `feature/mood-catalog-management` (branched from `develop`)
- **Commit Range:** `3a34a06` .. `55a9dc9` (Merged into `develop` at `06eee5c` via PR #1)
- **Status:** `Complete`

### Commit History (`feature/mood-catalog-management`)
1. `3a34a06` — `feat: add MoodTag and Track models and seed core moods in Supabase`
2. `312cda8` — `feat: implement curator track CRUD views, forms, templates, and live dashboard stats`
3. `55a9dc9` — `docs: add AGENTS instructions, project context, and append-only AI work log`

### Changed & Created Files
- `config/settings.py` (registered `music` app in `INSTALLED_APPS`)
- `config/urls.py` (mounted `path("music/", include("music.urls"))`)
- `music/models.py` (`MoodTag` and `Track` relational models)
- `music/admin.py` (`MoodTagAdmin` and `TrackAdmin`)
- `music/migrations/0001_initial.py` (schema migration for `MoodTag` and `Track`)
- `music/migrations/0002_seed_core_moods.py` (data migration seeding 6 core moods: `love`, `sad`, `calm`, `focus`, `happy`, `energy`)
- `music/forms.py` (`TrackForm` with whitespace stripping, required field validation, URL validation, and `CheckboxSelectMultiple` mood widgets)
- `music/views.py` (`CuratorRequiredMixin`, `TrackListView`, `TrackCreateView`, `TrackUpdateView`, `TrackDeleteView`)
- `music/urls.py` (Curator CRUD routes under `app_name = "music"`)
- `music/tests.py` (automated tests for mood seeding, form validation, listener access blocking, and curator CRUD)
- `dashboard/views.py` & `templates/dashboard/curator_dashboard.html` (live Supabase counts for `Track`, `MoodTag`, and `User` listeners + recent curated tracks table)
- `templates/base.html` (added Curator Catalog navigation link)
- `templates/music/curator_track_list.html`, `templates/music/curator_track_form.html`, `templates/music/curator_track_confirm_delete.html`

---

## Entry 3 — Increment 2 (PD2), Feature 2: Listener Discovery & Personal Song Meanings

- **Date:** 2026-11-18
- **Branch:** `feature/personal-song-meanings` (branched from `develop`)
- **Commit Range:** `bcfb180` .. `78868b4` (Merged into `develop` via PR #2)
- **Status Transition:** `Planned` -> `In progress` -> `Complete`

### Commit History (`feature/personal-song-meanings`)
1. `bcfb180` — `feat: add SongFeeling model with unique listener-track constraint and Supabase migration`
2. `3471a55` — `feat: implement listener track discovery, personal song meanings CRUD, and live listener dashboard`
3. `78868b4` — `docs: update project context and mark Feature 2 complete in AI work log`

### Milestone 1 & Milestone 2 Deliverables Implemented
1. **Model & Supabase Migration (`music/models.py`, `music/admin.py`, `music/migrations/0003_songfeeling.py`):**
   - Added `SongFeeling` (`listener` FK to `settings.AUTH_USER_MODEL`, `track` FK to `Track`, `moods` M2M to `MoodTag`, `note` max 240 chars, `is_favorite`, `created_at`, `updated_at`) with `UniqueConstraint(fields=["listener", "track"], name="unique_listener_track_feeling")` and ordering by `-updated_at`.
   - Registered `SongFeelingAdmin` in `music/admin.py`.
2. **Form Validation (`SongFeelingForm` in `music/forms.py`):**
   - Styled checkboxes (`form-check-input`) for `moods` and `is_favorite`, and Bootstrap `form-control` textarea for `note`.
   - Enforced `clean()` validation requiring at least 1 selected mood tag or a non-empty stripped `note`, and rejecting selections with `> 3` mood tags.
3. **Listener Role Guard & Owner-Scoped CRUD (`music/views.py`, `music/urls.py`):**
   - Added `ListenerRequiredMixin` (`role == "listener"` or `is_superuser`, redirecting curators with `messages.error`).
   - Added `TrackDiscoverView` (`/music/discover/`), `SongFeelingUpsertView` (`/music/track/<int:track_id>/feeling/`), `MySongFeelingsListView` (`/music/my-feelings/`), and `SongFeelingDeleteView` (`/music/feeling/<int:pk>/delete/`).
   - Strictly scoped `SongFeeling` queries and deletions to `listener=request.user`.
4. **Midnight Indigo Templates & Live Listener Dashboard:**
   - Created `templates/music/track_discover.html`, `templates/music/song_feeling_form.html`, `templates/music/my_feelings_list.html`, and `templates/music/song_feeling_confirm_delete.html`.
   - Updated `dashboard/views.py` (`listener_dashboard`), `templates/dashboard/listener_dashboard.html`, and `templates/base.html` with live Supabase counts and navigation links.
5. **Automated Unit Tests (`music/tests.py`):**
   - Added tests verifying `SongFeelingForm` validation (empty feeling rejected, >3 moods rejected), curator access blocking, upsert behavior, and owner-only isolation between `listener_a` and `listener_b`.

---

## Entry 4 — Increment 2 Release Documentation & PD2 Completion Report Preparation

- **Date:** 2026-11-18
- **Branch:** `develop`
- **Status Transition:** `Planned` -> `In progress` -> `Complete`

### Deliverables Completed on `develop`
1. **Repository Hygiene Audit:**
   - Verified `.gitignore` excludes `venv/`, `.env`, `__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd`, `db.sqlite3`, `media/`, and `.DS_Store`.
   - Verified `requirements.txt` lists `Django>=5.0,<5.3`, `psycopg[binary]>=3.1`, and `python-dotenv>=1.0`.
2. **Comprehensive `README.md`:**
   - Documented PD1 Account Feature and PD2 Core Vertical Slice (`MoodTag`, `Track`, and `SongFeeling` models, forms, views, and templates), Windows PowerShell setup instructions, and Gitflow branch architecture.
3. **PD2 Completion Report Reference (`docs/PD2_REPORT_DRAFT.md`):**
   - Prepared structured report sections (Features Implemented, Gitflow Branches/Commits/PR Table, Remaining WBS Tasks, Outstanding Issues/Limitations, and Test Accounts table) ready for export to `docs/EmpathTune-Balili-DirkKenji-G1-PD2.pdf`.
4. **Next Step (Release PR #3):**
   - Export `docs/EmpathTune-Balili-DirkKenji-G1-PD2.pdf`, commit on `develop`, push `origin/develop`, and open/merge **PR #3 (`develop` -> `main`)**.

---

## Entry 5 — Database Mode Toggle (`EMPATH_DB_MODE`) with Supabase Default

- **Date:** 2026-11-18
- **Branch:** `develop`
- **Status Transition:** `In progress` -> `Complete`
- **Changed Files:**
  - `config/settings.py`
  - `.env.example`
  - `README.md`
  - `docs/project-context.md`
  - `docs/ai-work-log.md`
- **Summary & Verification:**
  - Implemented `EMPATH_DB_MODE` in `config/settings.py` defaulting strictly to Supabase PostgreSQL (`postgres` / `postgresql` / `supabase` / unset) with `sslmode="require"`, while supporting `local` / `sqlite` for offline workstation testing and raising `ImproperlyConfigured` on invalid values.
  - Verified `manage.py check` (0 issues) and `manage.py test` (7/7 tests passing) in a temporary shell session without modifying `.env` or leaving any `db.sqlite3` file.
