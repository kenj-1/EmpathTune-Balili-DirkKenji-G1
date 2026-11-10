from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from accounts.forms import UserProfileForm
from accounts.models import User

@login_required
def dashboard_router(request):
    """Dispatches users directly to their designated role dashboard."""
    if request.user.role == "curator" or request.user.is_superuser:
        return redirect("dashboard:curator")
    return redirect("dashboard:listener")


@login_required
def listener_dashboard(request):
    """Listener-only space with personal mood preferences."""
    if request.user.role != "listener" and not request.user.is_superuser:
        messages.error(request, "Access denied: Curators cannot access the personal Listener workspace.")
        return redirect("dashboard:curator")

    context = {
        "title": "Listener Workspace",
        "saved_moods": ["In Love", "Calm", "Focused", "Need Uplift"],
        "recent_sessions": [
            {"title": "Midnight Reflections", "feeling": "Calm", "time": "2 hours ago"},
            {"title": "Study Flow Session", "feeling": "Focused", "time": "Yesterday"},
        ],
    }
    return render(request, "dashboard/listener_dashboard.html", context)


@login_required
def curator_dashboard(request):
    """Curator-only administrative catalog space with URL tamper defense."""
    if request.user.role != "curator" and not request.user.is_superuser:
        messages.error(request, "Access denied: You do not have Curator privileges to view that page.")
        return redirect("dashboard:listener")

    context = {
        "title": "Curator Management Console",
        "catalog_stats": {
            "total_recordings": 128,
            "pending_mood_audits": 14,
            "active_listeners": 42,
        },
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