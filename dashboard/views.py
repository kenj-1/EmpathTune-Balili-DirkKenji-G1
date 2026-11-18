from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from accounts.forms import UserProfileForm
from accounts.models import User
from music.models import MoodTag, SongFeeling, Track


@login_required
def dashboard_router(request):
    """Dispatches users directly to their designated role dashboard."""
    if request.user.role == "curator" or request.user.is_superuser:
        return redirect("dashboard:curator")
    return redirect("dashboard:listener")


@login_required
def listener_dashboard(request):
    """Listener-only space with personal mood preferences and saved song meanings."""
    if request.user.role != "listener" and not request.user.is_superuser:
        messages.error(request, "Access denied: Curators cannot access the personal Listener workspace.")
        return redirect("dashboard:curator")

    user_feelings_qs = (
        SongFeeling.objects.filter(listener=request.user)
        .select_related("track")
        .prefetch_related("moods")
    )
    saved_meanings_count = user_feelings_qs.count()
    favorites_count = user_feelings_qs.filter(is_favorite=True).count()
    available_tracks_count = Track.objects.count()
    recent_feelings = user_feelings_qs[:5]
    mood_tags = MoodTag.objects.all()

    context = {
        "title": "Listener Workspace",
        "listener_stats": {
            "saved_meanings_count": saved_meanings_count,
            "favorites_count": favorites_count,
            "available_tracks_count": available_tracks_count,
        },
        "saved_meanings_count": saved_meanings_count,
        "favorites_count": favorites_count,
        "available_tracks_count": available_tracks_count,
        "recent_feelings": recent_feelings,
        "mood_tags": mood_tags,
    }
    return render(request, "dashboard/listener_dashboard.html", context)


@login_required
def curator_dashboard(request):
    """Curator-only administrative catalog space with URL tamper defense."""
    if request.user.role != "curator" and not request.user.is_superuser:
        messages.error(request, "Access denied: You do not have Curator privileges to view that page.")
        return redirect("dashboard:listener")

    total_tracks = Track.objects.count()
    total_moods = MoodTag.objects.count()
    active_listeners = User.objects.filter(role="listener").count()
    recent_tracks = Track.objects.select_related("created_by").prefetch_related("moods")[:5]

    context = {
        "title": "Curator Management Console",
        "catalog_stats": {
            "total_recordings": total_tracks,
            "mood_tags_count": total_moods,
            "pending_mood_audits": total_moods,
            "active_listeners": active_listeners,
        },
        "total_tracks": total_tracks,
        "mood_tags_count": total_moods,
        "active_listeners": active_listeners,
        "recent_tracks": recent_tracks,
    }
    return render(request, "dashboard/curator_dashboard.html", context)


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "dashboard/profile.html"
    success_url = reverse_lazy("dashboard:profile")
    success_message = "Your profile has been updated successfully!"

    def get_object(self, queryset=None):
        # Security Guard: strictly returns the logged-in user so URL manipulation cannot touch other records
        return self.request.user
