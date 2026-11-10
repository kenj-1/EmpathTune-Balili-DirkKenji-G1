from django.urls import path
from .views import dashboard_router, listener_dashboard, curator_dashboard, ProfileUpdateView

app_name = "dashboard"

urlpatterns = [
    path("", dashboard_router, name="router"),
    path("dashboard/listener/", listener_dashboard, name="listener"),
    path("dashboard/curator/", curator_dashboard, name="curator"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
]