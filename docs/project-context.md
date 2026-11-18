# EmpathTune — Project Context & Architecture Reference

- **Repository:** `EmpathTune-Balili-DirkKenji-G1`
- **Student / Developer:** Dirk Kenji Balili (Group 1)
- **Architecture:** Full-Stack Server-Rendered Django (`Django ORM` + `Django Forms` + `Django Templates`)
- **Database:** Supabase PostgreSQL (`psycopg`, SSL-enabled connection via environment variables)
- **UI Design System:** Midnight Indigo Dark Theme (Bootstrap 5.3 via `templates/base.html`)

---

## 1. System Overview

**EmpathTune** is a mood-driven music discovery and emotional journaling web application built with Django and backed by Supabase PostgreSQL. Unlike conventional streaming catalogs that organize music solely by genre or popularity, EmpathTune bridges **Curator-defined emotional taxonomy** with **Listener-authored personal song meanings**:

1. **Curators (`role="curator"`)** maintain the canonical music catalog (`Track`) and assign emotional taxonomy tags (`MoodTag`) across six core emotional contexts (`In love`, `Sad / hurt`, `Calm`, `Focused`, `Happy`, `Energized`).
2. **Listeners (`role="listener"`)** explore the curated catalog by mood or keyword and record their own private emotional associations and memories (`SongFeeling`) for individual tracks.

---

## 2. Increment 1 (PD1) Baseline on `main` (Commits `2fcf341` .. `e16c5e9`)

Increment 1 established the authentication, role-based authorization, and account management foundation across `config/`, `accounts/`, `dashboard/`, and `templates/`:

- **Custom User Model (`accounts.models.User`):**
  - Extends `AbstractUser` (`AUTH_USER_MODEL = "accounts.User"`).
  - Fields: `role` (`"listener"` default or `"curator"`), `contact_number` (`CharField(max_length=20)`), and `bio` (`TextField(max_length=300)`).
  - Helper methods: `is_curator()` and `is_listener()`.
- **User Registration (`accounts.views.register_view`, `accounts.forms.UserRegistrationForm`):**
  - Validates unique username and case-insensitive unique email (`clean_email`), enforces Django's password validators, hashes passwords via `UserCreationForm`, and displays `django.contrib.messages` alerts.
- **Authentication & Role Routing (`dashboard.views.dashboard_router`):**
  - Standard login/logout views (`accounts/login/`, `accounts/logout/`) redirecting authenticated users to `dashboard:router`.
  - Dispatches Curators/Superusers to `/dashboard/curator/` and Listeners to `/dashboard/listener/`.
- **Role-Based Dashboards & URL Tamper Defense:**
  - `listener_dashboard` (`/dashboard/listener/`): Protected by `@login_required` and blocks Curators (non-superusers) with an error message redirect.
  - `curator_dashboard` (`/dashboard/curator/`): Protected by `@login_required` and blocks Listeners with an error message redirect to `dashboard:listener`.
- **Self-Only Profile Management (`dashboard.views.ProfileUpdateView`):**
  - Uses `LoginRequiredMixin`, `SuccessMessageMixin`, and `UpdateView` with `UserProfileForm`.
  - Overrides `get_object()` to strictly return `self.request.user`, preventing horizontal privilege escalation or URL tampering.

---

## 3. Increment 2 (PD2) Core Vertical Slice Architecture

Increment 2 expands EmpathTune from static role dashboards into a complete relational, database-driven application across two feature branches merged into `develop` and released to `main`.

### Feature Branch 1: `feature/mood-catalog-management` (Curator Catalog & Taxonomy)

Implemented in the `music` app (`music/models.py`, `music/forms.py`, `music/views.py`, `music/urls.py`, `music/admin.py`) and integrated with `dashboard/views.py`:

- **Relational Models (`music/models.py`):**
  - `MoodTag`:
    - `slug`: `SlugField(max_length=30, unique=True)`
    - `label`: `CharField(max_length=50)`
    - `icon`: `CharField(max_length=10, blank=True, default="")`
    - Ordered by `label`.
  - `Track`:
    - `title`: `CharField(max_length=200)`
    - `artist`: `CharField(max_length=200)`
    - `album`: `CharField(max_length=200, blank=True, default="")`
    - `genre`: `CharField(max_length=80, blank=True, default="")`
    - `preview_url`: `URLField(blank=True, default="")`
    - `moods`: `ManyToManyField(MoodTag, related_name="tracks", blank=True)`
    - `created_by`: `ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="curated_tracks")`
    - `created_at` (`auto_now_add=True`), `updated_at` (`auto_now=True`), ordered by `-created_at`.
- **Core Mood Seeding (`music/migrations/0002_seed_core_moods.py`):**
  - Reversible `RunPython` data migration seeding EmpathTune's 6 core moods in Supabase:
    1. `love` — `In love` (`♡`)
    2. `sad` — `Sad / hurt` (`☂`)
    3. `calm` — `Calm` (`◌`)
    4. `focus` — `Focused` (`◎`)
    5. `happy` — `Happy` (`☀`)
    6. `energy` — `Energized` (`⚡`)
- **Curator Access Guard & Full CRUD (`music/views.py`, `music/forms.py`):**
  - `CuratorRequiredMixin`: Verifies authentication and `request.user.role == "curator" or request.user.is_superuser`; redirects unauthorized Listeners to `dashboard:listener` with a `messages.error` alert.
  - `TrackForm`: Validates non-blank/whitespace-stripped `title` and `artist`, validates `http://`/`https://` scheme on optional `preview_url`, and renders `moods` with `CheckboxSelectMultiple`.
  - `TrackListView` (`/music/curator/tracks/`): Search (`q` across title, artist, album, genre) and filter by mood slug (`mood`).
  - `TrackCreateView` (`/music/curator/tracks/new/`): Assigns `form.instance.created_by = request.user` and emits `messages.success`.
  - `TrackUpdateView` (`/music/curator/tracks/<int:pk>/edit/`): Updates track fields and M2M mood tags with `messages.success`.
  - `TrackDeleteView` (`/music/curator/tracks/<int:pk>/delete/`): Confirmation screen and deletion with `messages.success`.
- **Live Curator Dashboard (`dashboard/views.py`, `templates/dashboard/curator_dashboard.html`):**
  - Displays real Supabase counts (`Track.objects.count()`, `MoodTag.objects.count()`, `User.objects.filter(role="listener").count()`) and the 5 most recent curated tracks.

---

### Feature Branch 2: `feature/personal-song-meanings` (Listener Discovery & Personal Meanings)

Planned as the second PD2 vertical slice on `feature/personal-song-meanings` (branched from `develop` after PR #1 merge):

- **Relational Model (`SongFeeling` in `music/models.py`):**
  - `listener`: `ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="song_feelings")`
  - `track`: `ForeignKey(Track, on_delete=models.CASCADE, related_name="listener_feelings")`
  - `personal_moods`: `ManyToManyField(MoodTag, related_name="personal_song_feelings", blank=True)`
  - `note`: `TextField(max_length=500, blank=True, default="")`
  - `created_at` (`auto_now_add=True`), `updated_at` (`auto_now=True`)
  - Constraints & Ordering: `UniqueConstraint(fields=["listener", "track"], name="unique_listener_track_feeling")`, ordered by `-updated_at`.
- **Form Validation (`SongFeelingForm` in `music/forms.py`):**
  - Requires at least 1–3 personal mood tags (`personal_moods`) **or** a non-empty stripped `note` (rejects submissions where both are empty, and caps `personal_moods` at a maximum of 3 tags).
- **Listener Discovery & Owner-Scoped CRUD (`music/views.py`, `dashboard/views.py`):**
  - Listener Catalog Discovery (`/music/discover/`): Allows authenticated Listeners to browse/search curated `Track` records, filter by `MoodTag`, listen to preview links, and see whether they have already logged a personal meaning for each track.
  - Create/Update `SongFeeling` (`/music/tracks/<int:track_id>/feeling/`): Upserts the logged-in listener's `SongFeeling` for a track (`listener = request.user`).
  - Edit/Delete `SongFeeling` (`/music/feelings/<int:pk>/edit/`, `/music/feelings/<int:pk>/delete/`): Queryset strictly filtered by `listener=request.user` so no listener can view, modify, or delete another user's personal song meanings.
  - Live Listener Dashboard (`/dashboard/listener/`): Replaces static placeholders with the listener's real saved `SongFeeling` entries, mood tag distribution, and quick links to discover tracks.
