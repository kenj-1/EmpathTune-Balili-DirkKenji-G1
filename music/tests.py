from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import TrackForm
from .models import MoodTag, Track

User = get_user_model()


class MoodCatalogTests(TestCase):
    def setUp(self):
        self.curator = User.objects.create_user(
            username="curator_user",
            email="curator@example.com",
            password="StrongPassword123!",
            role="curator",
        )
        self.listener = User.objects.create_user(
            username="listener_user",
            email="listener@example.com",
            password="StrongPassword123!",
            role="listener",
        )

    def test_core_moods_seeded(self):
        expected_slugs = {"love", "sad", "calm", "focus", "happy", "energy"}
        seeded_slugs = set(MoodTag.objects.values_list("slug", flat=True))
        self.assertTrue(expected_slugs.issubset(seeded_slugs))
        self.assertEqual(MoodTag.objects.count(), 6)

    def test_track_form_strips_and_rejects_whitespace(self):
        form = TrackForm(data={"title": "   ", "artist": "   "})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("artist", form.errors)

    def test_listener_blocked_from_curator_crud(self):
        self.client.login(username="listener_user", password="StrongPassword123!")
        response = self.client.get(reverse("music:curator_track_list"))
        self.assertRedirects(response, reverse("dashboard:listener"))

    def test_curator_full_track_crud(self):
        self.client.login(username="curator_user", password="StrongPassword123!")
        calm_mood = MoodTag.objects.get(slug="calm")

        # Create
        create_resp = self.client.post(
            reverse("music:curator_track_create"),
            {
                "title": "Weightless",
                "artist": "Marconi Union",
                "album": "Weightless (Ambient Transmissions)",
                "genre": "Ambient",
                "preview_url": "https://example.com/weightless",
                "moods": [calm_mood.pk],
            },
        )
        self.assertRedirects(create_resp, reverse("music:curator_track_list"))
        track = Track.objects.get(title="Weightless")
        self.assertEqual(track.created_by, self.curator)
        self.assertIn(calm_mood, track.moods.all())

        # Update
        update_resp = self.client.post(
            reverse("music:curator_track_update", args=[track.pk]),
            {
                "title": "Weightless (Extended)",
                "artist": "Marconi Union",
                "album": "Ambient Works",
                "genre": "Ambient",
                "preview_url": "https://example.com/weightless",
                "moods": [calm_mood.pk],
            },
        )
        self.assertRedirects(update_resp, reverse("music:curator_track_list"))
        track.refresh_from_db()
        self.assertEqual(track.title, "Weightless (Extended)")

        # Delete
        delete_resp = self.client.post(
            reverse("music:curator_track_delete", args=[track.pk])
        )
        self.assertRedirects(delete_resp, reverse("music:curator_track_list"))
        self.assertFalse(Track.objects.filter(pk=track.pk).exists())
