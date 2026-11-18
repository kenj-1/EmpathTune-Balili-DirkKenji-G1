from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import SongFeelingForm, TrackForm
from .models import MoodTag, SongFeeling, Track


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


class ListenerRequiredMixin(LoginRequiredMixin):
    """Ensures the current user is authenticated and holds Listener or Superuser privileges."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if getattr(request.user, "role", None) != "listener" and not request.user.is_superuser:
            messages.error(
                request,
                "Access denied: Curators cannot access personal Listener song meanings.",
            )
            return redirect("dashboard:curator")
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


class TrackDiscoverView(ListenerRequiredMixin, ListView):
    model = Track
    template_name = "music/track_discover.html"
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
        user_feelings = (
            SongFeeling.objects.filter(listener=self.request.user)
            .prefetch_related("moods")
        )
        feelings_by_track = {f.track_id: f for f in user_feelings}

        for track in context["tracks"]:
            track.user_feeling = feelings_by_track.get(track.pk)

        context["mood_tags"] = MoodTag.objects.all()
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["selected_mood"] = self.request.GET.get("mood", "").strip()
        context["saved_track_ids"] = set(feelings_by_track.keys())
        context["total_catalog_count"] = Track.objects.count()
        return context


class SongFeelingUpsertView(ListenerRequiredMixin, View):
    template_name = "music/song_feeling_form.html"

    def get_track(self, track_id):
        return get_object_or_404(Track.objects.prefetch_related("moods"), pk=track_id)

    def get(self, request, track_id):
        track = self.get_track(track_id)
        feeling = SongFeeling.objects.filter(listener=request.user, track=track).first()
        form = SongFeelingForm(instance=feeling)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "track": track,
                "feeling": feeling,
                "is_update": feeling is not None,
            },
        )

    def post(self, request, track_id):
        track = self.get_track(track_id)
        existing_feeling = SongFeeling.objects.filter(
            listener=request.user, track=track
        ).first()
        form = SongFeelingForm(request.POST, instance=existing_feeling)

        if form.is_valid():
            feeling, created = SongFeeling.objects.get_or_create(
                listener=request.user,
                track=track,
                defaults={
                    "note": form.cleaned_data["note"],
                    "is_favorite": form.cleaned_data["is_favorite"],
                },
            )
            if not created:
                feeling.note = form.cleaned_data["note"]
                feeling.is_favorite = form.cleaned_data["is_favorite"]
                feeling.save()
            feeling.moods.set(form.cleaned_data["moods"])

            action_word = "saved" if created else "updated"
            messages.success(
                request,
                f'Your personal meaning for "{track.title}" has been {action_word}.',
            )
            return redirect("music:my_feelings_list")

        messages.error(request, "Please correct the errors highlighted below.")
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "track": track,
                "feeling": existing_feeling,
                "is_update": existing_feeling is not None,
            },
        )


class MySongFeelingsListView(ListenerRequiredMixin, ListView):
    model = SongFeeling
    template_name = "music/my_feelings_list.html"
    context_object_name = "feelings"

    def get_queryset(self):
        queryset = (
            SongFeeling.objects.filter(listener=self.request.user)
            .select_related("track")
            .prefetch_related("moods", "track__moods")
        )
        mood = self.request.GET.get("mood", "").strip()
        q = self.request.GET.get("q", "").strip()
        favorites_only = self.request.GET.get("favorites", "").strip() == "1"

        if mood:
            queryset = queryset.filter(moods__slug=mood)
        if q:
            queryset = queryset.filter(
                Q(track__title__icontains=q)
                | Q(track__artist__icontains=q)
                | Q(note__icontains=q)
            )
        if favorites_only:
            queryset = queryset.filter(is_favorite=True)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_qs = SongFeeling.objects.filter(listener=self.request.user)
        context["mood_tags"] = MoodTag.objects.all()
        context["selected_mood"] = self.request.GET.get("mood", "").strip()
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["favorites_only"] = self.request.GET.get("favorites", "").strip() == "1"
        context["total_feelings_count"] = user_qs.count()
        context["favorites_count"] = user_qs.filter(is_favorite=True).count()
        return context


class SongFeelingDeleteView(ListenerRequiredMixin, DeleteView):
    model = SongFeeling
    template_name = "music/song_feeling_confirm_delete.html"
    context_object_name = "feeling"
    success_url = reverse_lazy("music:my_feelings_list")

    def get_queryset(self):
        # Strict owner-only filter: prevents deleting or inspecting another listener's SongFeeling
        return SongFeeling.objects.filter(listener=self.request.user).select_related("track")

    def form_valid(self, form):
        track_title = self.object.track.title
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Your personal meaning for "{track_title}" was removed.',
        )
        return response
