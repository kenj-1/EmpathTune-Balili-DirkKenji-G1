from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:router")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account successfully created for {user.username}! You can now log in.",
            )
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors indicated below.")
    else:
        form = UserRegistrationForm()

    return render(request, "registration/signup.html", {"form": form})