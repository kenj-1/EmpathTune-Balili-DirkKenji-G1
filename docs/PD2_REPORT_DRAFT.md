# Project Development 2 (PD2) — Completion Report Reference Content

> **Instructions:** Copy the sections below directly into `PD-Completion-Report-Template.docx`, fill in your final GitHub PR URLs and test account passwords if customized, and export the final document to `docs/EmpathTune-Balili-DirkKenji-G1-PD2.pdf`.

---

## 1. Project Identification

- **Project Title:** EmpathTune — Mood-Driven Music Discovery & Personal Song Meaning Platform
- **Student Name:** Dirk Kenji Balili
- **Group / Section:** Group 1 (G1)
- **Repository Name:** `EmpathTune-Balili-DirkKenji-G1`
- **Technology Stack:** Full-Stack Django 5.2 (`Django ORM` + `Django Forms` + `Django Templates`), Supabase PostgreSQL (`psycopg`), Bootstrap 5.3 (Midnight Indigo Theme)

---

## 2. Features Implemented

### A. Increment 1 (PD1) — Account & Role Management Feature (Preserved & Verified)
1. **Custom User Model (`accounts.models.User`):**
   - Extends `AbstractUser` with `role` (`listener` or `curator`), `contact_number`, and `bio`.
2. **User Registration (`/accounts/signup/`):**
   - `UserRegistrationForm` validates unique usernames and case-insensitive unique email addresses (`clean_email`), enforces Django password validators, hashes passwords automatically, and provides user feedback via `django.contrib.messages`.
3. **Authentication & Role-Based Routing (`/accounts/login/`, `/accounts/logout/`, `/`):**
   - Authenticates users and dispatches Curators/Superusers to `/dashboard/curator/` and Listeners to `/dashboard/listener/`.
4. **Role Access Control & Self-Only Profile Editing (`/profile/`):**
   - Server-side role checks prevent cross-role URL tampering with `messages.error` redirects.
   - `ProfileUpdateView.get_object()` strictly returns `self.request.user` so users can only view and edit their own profile.

---

### B. Increment 2 (PD2) — Core Vertical Slice: Mood Catalog Management & Personal Song Meanings

#### Module 1: Curator Mood Taxonomy & Track Catalog CRUD (`feature/mood-catalog-management`)
1. **Relational Database Models & Seed Migration (`music/models.py`, `music/migrations/`):**
   - `MoodTag`: `slug` (`SlugField(max_length=30, unique=True)`), `label` (`CharField(max_length=50)`), `icon` (`CharField(max_length=10)`), ordered by `label`.
   - `Track`: `title`, `artist`, `album`, `genre`, `preview_url`, `moods` (`ManyToManyField` to `MoodTag`), `created_by` (`ForeignKey` to `accounts.User`), `created_at`, and `updated_at`, ordered by `-created_at`.
   - Reversible data migration (`0002_seed_core_moods.py`) seeds EmpathTune's 6 core moods in Supabase PostgreSQL: `In love (♡)`, `Sad / hurt (☂)`, `Calm (◌)`, `Focused (◎)`, `Happy (☀)`, and `Energized (⚡)`.
2. **Curator Role Guard & Full CRUD Views (`music/views.py`, `music/forms.py`):**
   - `CuratorRequiredMixin` restricts catalog management to authenticated users with `role == "curator"` or `is_superuser`, redirecting unauthorized listeners with a `messages.error` alert.
   - `TrackForm` strips whitespace, rejects blank/whitespace-only `title` and `artist` values, validates `http://`/`https://` schemes on optional `preview_url` links, and renders `moods` checkboxes.
   - **Create (`/music/curator/tracks/new/`):** `TrackCreateView` binds `form.instance.created_by = request.user` and persists track metadata + mood tags to Supabase.
   - **Read (`/music/curator/tracks/`):** `TrackListView` supports keyword search (`?q=` across title, artist, album, genre) and mood tag filtering (`?mood=<slug>`).
   - **Update (`/music/curator/tracks/<int:pk>/edit/`):** `TrackUpdateView` updates track metadata and M2M mood tags.
   - **Delete (`/music/curator/tracks/<int:pk>/delete/`):** `TrackDeleteView` renders a confirmation view and deletes the track with `messages.success`.
3. **Live Curator Dashboard (`/dashboard/curator/`):**
   - Displays live Supabase counts (`Track.objects.count()`, `MoodTag.objects.count()`, `User.objects.filter(role="listener").count()`) and the 5 most recently curated tracks.

#### Module 2: Listener Track Discovery & Personal Song Meanings CRUD (`feature/personal-song-meanings`)
1. **Relational Model & Uniqueness Constraint (`music/models.py`, `0003_songfeeling.py`):**
   - `SongFeeling`: Links `listener` (`ForeignKey` to `accounts.User`) and `track` (`ForeignKey` to `Track`) with `moods` (`ManyToManyField` to `MoodTag`), `note` (`TextField(max_length=240, blank=True, default="")`), `is_favorite` (`BooleanField(default=False)`), `created_at`, and `updated_at`.
   - Enforces `UniqueConstraint(fields=["listener", "track"], name="unique_listener_track_feeling")` so each listener maintains one canonical personal meaning per track.
2. **Form Validation (`SongFeelingForm` in `music/forms.py`):**
   - Validates in `clean()` that the listener selects **at least 1 mood tag** or writes a **non-empty stripped `note`**, and rejects selections exceeding **3 mood tags** (`ValidationError`).
3. **Listener Role Guard, Discovery, & Owner-Scoped CRUD (`music/views.py`):**
   - `ListenerRequiredMixin` restricts personal song journal routes to `role == "listener"` or `is_superuser`, redirecting curators with a `messages.error` alert.
   - **Discover (`/music/discover/`):** `TrackDiscoverView` lets listeners search tracks and filter by mood tag while annotating each track with `track.user_feeling` for `request.user`.
   - **Create / Update (`/music/track/<int:track_id>/feeling/`):** `SongFeelingUpsertView` creates or updates the logged-in listener's `SongFeeling` (`get_or_create` scoped strictly to `listener=request.user`).
   - **Read Personal Journal (`/music/my-feelings/`):** `MySongFeelingsListView` queries strictly `SongFeeling.objects.filter(listener=request.user)` with search, mood, and favorites-only filters.
   - **Delete (`/music/feeling/<int:pk>/delete/`):** `SongFeelingDeleteView` scopes `get_queryset()` to `listener=request.user` so URL tampering on another listener's record returns `404 Not Found`.
4. **Live Listener Dashboard (`/dashboard/listener/`):**
   - Displays live Supabase metrics (saved meanings count, favorites count, available catalog tracks), mood discovery badges, and recent personal song reflections.

---

## 3. Gitflow Branches, Commit History, & Pull Requests

### Active Branches (All Preserved on Origin)
- `main` — Stable production release branch (zero direct commits).
- `develop` — Integration branch branched from `main`.
- `feature/mood-catalog-management` — Feature branch 1 (Curator `MoodTag` + `Track` CRUD).
- `feature/personal-song-meanings` — Feature branch 2 (Listener Discovery + `SongFeeling` CRUD).

### Pull Request Summary Table

| PR # | Source Branch | Target Branch | Title / Scope | Status |
| :--- | :--- | :--- | :--- | :--- |
| **PR #1** | `feature/mood-catalog-management` | `develop` | Curator MoodTag & Track Catalog CRUD, Seed Migration, & Live Curator Dashboard | Merged (`06eee5c`) |
| **PR #2** | `feature/personal-song-meanings` | `develop` | Listener Track Discovery, Personal SongFeeling CRUD, Ownership Isolation, & Unit Tests | Merged |
| **PR #3** | `develop` | `main` | Release Increment 2 (PD2): Integrated Mood Catalog & Personal Song Meanings Vertical Slice | Ready / Merged |

### Chronological Commit Log

| Commit Hash | Branch | Commit Message |
| :--- | :--- | :--- |
| `2fcf341` | `main` (PD1) | `feat: initialize Django project structure, requirements, and PostgreSQL configuration` |
| `3bf8359` | `main` (PD1) | `feat: implement CustomUser model with listener and curator roles and apply migrations` |
| `3570275` | `main` (PD1) | `feat: add user registration form, password hashing, validation, and messages` |
| `667ec5f` | `main` (PD1) | `feat: implement login authentication, role-based dashboards, and URL access protection` |
| `e16c5e9` | `main` (PD1) | `feat: implement secure user profile view and self-edit functionality restricted to owner` |
| `3a34a06` | `feature/mood-catalog-management` | `feat: add MoodTag and Track models and seed core moods in Supabase` |
| `312cda8` | `feature/mood-catalog-management` | `feat: implement curator track CRUD views, forms, templates, and live dashboard stats` |
| `55a9dc9` | `feature/mood-catalog-management` | `docs: add AGENTS instructions, project context, and append-only AI work log` |
| `06eee5c` | `develop` | `Merge pull request #1 from kenj-1/feature/mood-catalog-management` |
| `bcfb180` | `feature/personal-song-meanings` | `feat: add SongFeeling model with unique listener-track constraint and Supabase migration` |
| `3471a55` | `feature/personal-song-meanings` | `feat: implement listener track discovery, personal song meanings CRUD, and live listener dashboard` |
| `78868b4` | `feature/personal-song-meanings` | `docs: update project context and mark Feature 2 complete in AI work log` |

---

## 4. Remaining Tasks (Future Increments / Subsequent WBS Modules)

1. **Embedded Audio Preview Player & Queue Controller:**
   - Add an in-page HTML5 / waveform audio preview bar and queue controller so listeners can sample 30-second previews seamlessly while browsing `/music/discover/`.
2. **Listening Behavior & Session Analytics Tracking:**
   - Log listener playback events, mood transition history, and time-of-day mood trends to power personalized recommendations.
3. **Natural Language Mood Prompt Interpretation:**
   - Allow listeners to type free-text emotional prompts (e.g., *"late-night rainy study session"*) and automatically map them to weighted combinations of `MoodTag` and personal `SongFeeling` history.

---

## 5. Outstanding Issues & Known Limitations

1. **External Streaming Preview Links Only:**
   - The current catalog stores track metadata and external `preview_url` links (e.g., Spotify/YouTube/SoundCloud URLs) rather than hosting or streaming full-length commercial audio files on the server.
2. **Supabase Session Pooler Environment Requirement:**
   - Local execution and automated test runs require a valid `.env` file configured with Supabase PostgreSQL Session Pooler credentials (`sslmode="require"` on port `5432`), as SQLite is intentionally disabled per course requirements.

---

## 6. Test Accounts for Grading Verification

| Role | Username | Email | Password | Primary Routes to Test |
| :--- | :--- | :--- | :--- | :--- |
| **Curator** | `curator_demo` | `curator@empathtune.local` | `EmpathCurator2026!` | `/dashboard/curator/`, `/music/curator/tracks/`, `/music/curator/tracks/new/` |
| **Listener** | `listener_demo` | `listener@empathtune.local` | `EmpathListener2026!` | `/dashboard/listener/`, `/music/discover/`, `/music/my-feelings/` |
