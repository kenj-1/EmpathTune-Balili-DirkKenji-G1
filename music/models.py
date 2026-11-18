from django.conf import settings
from django.db import models


class MoodTag(models.Model):
    slug = models.SlugField(max_length=30, unique=True)
    label = models.CharField(max_length=50)
    icon = models.CharField(max_length=10, blank=True, default="")

    class Meta:
        ordering = ["label"]

    def __str__(self):
        return f"{self.icon} {self.label}".strip()


class Track(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    album = models.CharField(max_length=200, blank=True, default="")
    genre = models.CharField(max_length=80, blank=True, default="")
    preview_url = models.URLField(blank=True, default="")
    moods = models.ManyToManyField(MoodTag, related_name="tracks", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="curated_tracks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — {self.artist}"
