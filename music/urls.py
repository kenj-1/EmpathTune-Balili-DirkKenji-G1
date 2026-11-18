from django.urls import path
from .views import (
    TrackCreateView,
    TrackDeleteView,
    TrackListView,
    TrackUpdateView,
)

app_name = "music"

urlpatterns = [
    path("curator/tracks/", TrackListView.as_view(), name="curator_track_list"),
    path("curator/tracks/new/", TrackCreateView.as_view(), name="curator_track_create"),
    path("curator/tracks/<int:pk>/edit/", TrackUpdateView.as_view(), name="curator_track_update"),
    path("curator/tracks/<int:pk>/delete/", TrackDeleteView.as_view(), name="curator_track_delete"),
]
