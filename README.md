# 🎵 EmpathTune — Mood-Driven Music Discovery & Personal Song Meaning Platform

- **Repository:** `EmpathTune-Balili-DirkKenji-G1`
- **Developer:** Dirk Kenji Balili (Group 1)
- **Tech Stack:** Full-Stack Django 5 (`Django ORM` + `Django Forms` + `Django Templates`) · Supabase PostgreSQL (`psycopg`) · Bootstrap 5.3 (Midnight Indigo Dark Theme)

---

## 1. Project Overview

**EmpathTune** is a full-stack Django web application backed by Supabase PostgreSQL that connects **Curator-defined emotional music taxonomy** with **Listener-authored personal song meanings**. Rather than organizing tracks only by genre or popularity, EmpathTune allows Curators to maintain a mood-tagged catalog across six core emotional states (`In love`, `Sad / hurt`, `Calm`, `Focused`, `Happy`, `Energized`) while giving Listeners a private space to discover songs by mood and record their own personal feelings, memories, and favorite tracks.

---

## 2. Implemented Features

### Increment 1 (PD1) — Account & Role Management Foundation
- **Custom User Model (`accounts.User`):** Extends `AbstractUser` with `role` (`listener` or `curator`), `contact_number`, and `bio`.
- **User Registration (`/accounts/signup/`):** Validates unique username and case-insensitive unique email, enforces Django password strength validators, hashes passwords automatically, and displays Bootstrap alert messages.
- **Authentication & Role Router (`/accounts/login/`, `/accounts/logout/`, `/`):** Authenticates users and routes them automatically to their designated role workspace (`/dashboard/listener/` or `/dashboard/curator/`).
- **Role-Protected Dashboards & URL Tamper Defense:** Server-side checks (`@login_required`, `CuratorRequiredMixin`, `ListenerRequiredMixin`) block cross-role URL access attempts and redirect with clear `messages.error` feedback.
- **Self-Only Profile Management (`/profile/`):** `ProfileUpdateView` overrides `get_object()` to strictly return `self.request.user`, ensuring users can only view and edit their own account profile.

### Increment 2 (PD2) — Core Vertical Slice: Mood Catalog Management & Personal Song Meanings

#### Feature 1: Curator Mood & Track Catalog Management (`feature/mood-catalog-management`)
- **Relational Models (`music/models.py`):**
  - `MoodTag`: `slug` (`unique=True`), `label`, and `icon` seeded via data migration (`0002_seed_core_moods.py`) with 6 core moods (`love` ♡, `sad` ☂, `calm` ◌, `focus` ◎, `happy` ☀, `energy` ⚡).
  - `Track`: `title`, `artist`, `album`, `genre`, `preview_url`, `moods` (`ManyToManyField` to `MoodTag`), `created_by` (`ForeignKey` to `accounts.User`), `created_at`, and `updated_at`.
- **Curator Full CRUD (`/music/curator/tracks/`):**
  - **Create (`/music/curator/tracks/new/`):** `TrackForm` strips whitespace, rejects blank titles/artists, validates `http://`/`https://` preview URLs, assigns `created_by = request.user`, and saves mood tag associations.
  - **Read (`/music/curator/tracks/`):** Search tracks by title, artist, album, or genre (`?q=`) and filter by mood tag (`?mood=<slug>`).
  - **Update (`/music/curator/tracks/<pk>/edit/`):** Edit track metadata and assigned mood tags.
  - **Delete (`/music/curator/tracks/<pk>/delete/`):** Confirmation screen and deletion with `messages.success`.
- **Live Curator Dashboard (`/dashboard/curator/`):** Displays real-time Supabase counts (`Track.objects.count()`, `MoodTag.objects.count()`, `User.objects.filter(role="listener").count()`) and recent curated tracks.

#### Feature 2: Listener Discovery & Personal Song Meanings (`feature/personal-song-meanings`)
- **Relational Model (`SongFeeling` in `music/models.py`):**
  - Links `listener` (`ForeignKey` to `accounts.User`) and `track` (`ForeignKey` to `Track`) with `moods` (`ManyToManyField` to `MoodTag`), `note` (`max_length=240`), `is_favorite` (`BooleanField`), and `UniqueConstraint(fields=["listener", "track"], name="unique_listener_track_feeling")`.
- **Listener Discovery & Owner-Scoped Personal Meaning CRUD:**
  - **Discover (`/music/discover/`):** Search and filter curated tracks by mood tag while seeing whether the logged-in listener has already logged a personal meaning for each track.
  - **Create / Update (`/music/track/<track_id>/feeling/`):** `SongFeelingForm` validates that the listener selects **1 to 3 mood tags** or provides a **non-empty reflection note** (rejecting empty submissions and `>3` mood tags), upserting the record strictly for `request.user`.
  - **Read Personal Journal (`/music/my-feelings/`):** Displays only `SongFeeling.objects.filter(listener=request.user)` with search, mood, and favorites-only filters.
  - **Delete (`/music/feeling/<pk>/delete/`):** Strictly scopes `get_queryset()` to `listener=request.user` so URL tampering cannot view or delete another listener's records.
- **Live Listener Dashboard (`/dashboard/listener/`):** Displays live Supabase counts (saved meanings, favorites, available catalog tracks), mood filter badges, and recent personal song reflections.

---

## 3. Local Setup & Execution (Windows PowerShell)

### Prerequisites
- Python 3.11+
- Access to the project's Supabase PostgreSQL instance (Session Pooler on port `5432`)

### Step-by-Step Setup

1. **Clone the repository and navigate to the project root:**
   ```powershell
   git clone https://github.com/kenj-1/EmpathTune-Balili-DirkKenji-G1.git
   cd EmpathTune-Balili-DirkKenji-G1
   ```

2. **Create and activate a Python virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables (`.env`):**
   Copy `.env.example` to `.env` and fill in your Supabase PostgreSQL credentials:
   ```powershell
   Copy-Item .env.example .env
   ```
   Required keys in `.env`:
   ```env
   EMPATH_SECRET_KEY=your-dev-secret-key
   DJANGO_DEBUG=1
   EMPATH_DB_HOST=aws-0-ap-southeast-1.pooler.supabase.com
   EMPATH_DB_PORT=5432
   EMPATH_DB_NAME=postgres
   EMPATH_DB_USER=postgres.your-project-ref
   EMPATH_DB_PASSWORD=your-database-password
   ```

5. **Apply database migrations (creates tables and seeds the 6 core moods in Supabase):**
   ```powershell
   python manage.py migrate
   ```

6. **Run system checks and automated tests:**
   ```powershell
   python manage.py check
   python manage.py test
   ```

7. **Start the Django development server:**
   ```powershell
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000/` in your browser.

---

## 4. Gitflow Branching Structure

This repository strictly follows the Gitflow workflow required for PD1 and PD2:

- `main` — Stable production release branch (no direct commits; updated only via release Pull Requests).
- `develop` — Integration branch created from `main` where feature branches are merged and verified.
- `feature/mood-catalog-management` — PD2 Feature Branch 1 (`MoodTag` + `Track` models, 6-mood data migration, Curator CRUD views/forms/templates, live Curator dashboard). Merged into `develop` via **PR #1**.
- `feature/personal-song-meanings` — PD2 Feature Branch 2 (`SongFeeling` model with unique listener-track constraint, Listener discovery, owner-scoped `SongFeeling` CRUD, live Listener dashboard, unit tests). Merged into `develop` via **PR #2**.
