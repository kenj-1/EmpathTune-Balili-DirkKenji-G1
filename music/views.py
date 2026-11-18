from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import TrackForm
from .models import MoodTag, Track


class CuratorRequiredMixin(LoginRequiredMixin):
    """Ensures the current user is authenticated and holds Curator or Superuser privileges."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if getattr(request.user, "role", None) != "curator" and not request.user.is_superuser:
            messages.error(
                request,
                "Access denied: You do not have Curator privileges to manage the music catalog.",
            )
            return redirect("dashboard:listener")
        return super().dispatch(request, *args, **kwargs)


class TrackListView(CuratorRequiredMixin, ListView):
    model = Track
    template_name = "music/curator_track_list.html"
    context_object_name = "tracks"

    def get_queryset(self):
        queryset = Track.objects.select_related("created_by").prefetch_related("moods")
        q = self.request.GET.get("q", "").strip()
        mood = self.request.GET.get("mood", "").strip()

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(artist__icontains=q)
                | Q(album__icontains=q)
                | Q(genre__icontains=q)
            )
        if mood:
            queryset = queryset.filter(moods__slug=mood)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mood_tags"] = MoodTag.objects.all()
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["selected_mood"] = self.request.GET.get("mood", "").strip()
        context["total_catalog_count"] = Track.objects.count()
        return context


class TrackCreateView(CuratorRequiredMixin, CreateView):
    model = Track
    form_class = TrackForm
    template_name = "music/curator_track_form.html"
    success_url = reverse_lazy("music:curator_track_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Track "{self.object.title}" by {self.object.artist} has been added to the catalog.',
        )
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors highlighted below.")
        return super().form_invalid(form)


class TrackUpdateView(CuratorRequiredMixin, UpdateView):
    model = Track
    form_class = TrackForm
    template_name = "music/curator_track_form.html"
    success_url = reverse_lazy("music:curator_track_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Track "{self.object.title}" has been updated successfully.',
        )
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors highlighted below.")
        return super().form_invalid(form)


class TrackDeleteView(CuratorRequiredMixin, DeleteView):
    model = Track
    template_name = "music/curator_track_confirm_delete.html"
    context_object_name = "track"
    success_url = reverse_lazy("music:curator_track_list")

    def form_valid(self, form):
        track_title = self.object.title
        track_artist = self.object.artist
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Track "{track_title}" by {track_artist} has been deleted from the catalog.',
        )
        return response
