from django.contrib import admin
from .models import MoodTag, SongFeeling, Track


@admin.register(MoodTag)
class MoodTagAdmin(admin.ModelAdmin):
    list_display = ("label", "slug", "icon")
    search_fields = ("label", "slug")
    prepopulated_fields = {"slug": ("label",)}


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "album", "genre", "created_by", "created_at")
    list_filter = ("genre", "moods", "created_at")
    search_fields = ("title", "artist", "album", "genre")
    filter_horizontal = ("moods",)


@admin.register(SongFeeling)
class SongFeelingAdmin(admin.ModelAdmin):
    list_display = ("listener", "track", "is_favorite", "updated_at")
    list_filter = ("is_favorite", "moods", "updated_at")
    search_fields = ("listener__username", "track__title", "track__artist", "note")
    filter_horizontal = ("moods",)
