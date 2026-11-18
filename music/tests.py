from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import SongFeelingForm, TrackForm
from .models import MoodTag, SongFeeling, Track

User = get_user_model()


class MoodCatalogAndFeelingTests(TestCase):
    def setUp(self):
        self.curator = User.objects.create_user(
            username="curator_user",
            email="curator@example.com",
            password="StrongPassword123!",
            role="curator",
        )
        self.listener_a = User.objects.create_user(
            username="listener_a",
            email="listener_a@example.com",
            password="StrongPassword123!",
            role="listener",
        )
        self.listener_b = User.objects.create_user(
            username="listener_b",
            email="listener_b@example.com",
            password="StrongPassword123!",
            role="listener",
        )
        self.track = Track.objects.create(
            title="Clair de Lune",
            artist="Claude Debussy",
            album="Suite bergamasque",
            genre="Classical",
            created_by=self.curator,
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
        self.client.login(username="listener_a", password="StrongPassword123!")
        response = self.client.get(reverse("music:curator_track_list"))
        self.assertRedirects(response, reverse("dashboard:listener"))

    def test_curator_blocked_from_listener_feelings(self):
        self.client.login(username="curator_user", password="StrongPassword123!")
        response = self.client.get(reverse("music:track_discover"))
        self.assertRedirects(response, reverse("dashboard:curator"))

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

    def test_song_feeling_form_rejects_empty_and_more_than_three_moods(self):
        # Empty mood tags and blank/whitespace note must be rejected
        empty_form = SongFeelingForm(data={"moods": [], "note": "   ", "is_favorite": False})
        self.assertFalse(empty_form.is_valid())

        # More than 3 mood tags must be rejected
        four_moods = list(MoodTag.objects.values_list("pk", flat=True)[:4])
        too_many_form = SongFeelingForm(
            data={"moods": four_moods, "note": "Too many moods", "is_favorite": False}
        )
        self.assertFalse(too_many_form.is_valid())
        self.assertIn("moods", too_many_form.errors)

        # Valid 1-3 moods or non-empty note succeeds
        valid_form = SongFeelingForm(
            data={"moods": four_moods[:2], "note": "Peaceful evening study song", "is_favorite": True}
        )
        self.assertTrue(valid_form.is_valid())

    def test_listener_owner_only_isolation_and_upsert(self):
        calm_mood = MoodTag.objects.get(slug="calm")
        focus_mood = MoodTag.objects.get(slug="focus")

        # Listener A creates a personal meaning
        self.client.login(username="listener_a", password="StrongPassword123!")
        upsert_url = reverse("music:song_feeling_upsert", args=[self.track.pk])
        resp = self.client.post(
            upsert_url,
            {
                "moods": [calm_mood.pk],
                "note": "Helps me unwind after class.",
                "is_favorite": True,
            },
        )
        self.assertRedirects(resp, reverse("music:my_feelings_list"))
        feeling_a = SongFeeling.objects.get(listener=self.listener_a, track=self.track)
        self.assertTrue(feeling_a.is_favorite)

        # Listener A updates the same track meaning (upsert enforces single row per listener+track)
        resp_update = self.client.post(
            upsert_url,
            {
                "moods": [calm_mood.pk, focus_mood.pk],
                "note": "Updated reflection note.",
                "is_favorite": False,
            },
        )
        self.assertRedirects(resp_update, reverse("music:my_feelings_list"))
        self.assertEqual(
            SongFeeling.objects.filter(listener=self.listener_a, track=self.track).count(),
            1,
        )
        feeling_a.refresh_from_db()
        self.assertEqual(feeling_a.note, "Updated reflection note.")
        self.assertFalse(feeling_a.is_favorite)

        # Listener B cannot see Listener A's feeling in MySongFeelingsListView or delete it
        self.client.logout()
        self.client.login(username="listener_b", password="StrongPassword123!")
        list_resp = self.client.get(reverse("music:my_feelings_list"))
        self.assertNotContains(list_resp, "Updated reflection note.")

        delete_url = reverse("music:song_feeling_delete", args=[feeling_a.pk])
        tamper_get = self.client.get(delete_url)
        self.assertEqual(tamper_get.status_code, 404)
        tamper_post = self.client.post(delete_url)
        self.assertEqual(tamper_post.status_code, 404)
        self.assertTrue(SongFeeling.objects.filter(pk=feeling_a.pk).exists())
