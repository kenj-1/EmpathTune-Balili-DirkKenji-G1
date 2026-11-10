from django.urls import path
from .views import register_view

urlpatterns = [
    path("signup/", register_view, name="signup"),
]