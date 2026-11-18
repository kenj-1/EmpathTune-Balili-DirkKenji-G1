from django.urls import path
from .views import (
    MySongFeelingsListView,
    SongFeelingDeleteView,
    SongFeelingUpsertView,
    TrackCreateView,
    TrackDeleteView,
    TrackDiscoverView,
    TrackListView,
    TrackUpdateView,
)

app_name = "music"

urlpatterns = [
    # Curator Catalog CRUD Routes
    path("curator/tracks/", TrackListView.as_view(), name="curator_track_list"),
    path("curator/tracks/new/", TrackCreateView.as_view(), name="curator_track_create"),
    path("curator/tracks/<int:pk>/edit/", TrackUpdateView.as_view(), name="curator_track_update"),
    path("curator/tracks/<int:pk>/delete/", TrackDeleteView.as_view(), name="curator_track_delete"),
    # Listener Discovery & Personal Song Meanings CRUD Routes
    path("discover/", TrackDiscoverView.as_view(), name="track_discover"),
    path("track/<int:track_id>/feeling/", SongFeelingUpsertView.as_view(), name="song_feeling_upsert"),
    path("my-feelings/", MySongFeelingsListView.as_view(), name="my_feelings_list"),
    path("feeling/<int:pk>/delete/", SongFeelingDeleteView.as_view(), name="song_feeling_delete"),
]
