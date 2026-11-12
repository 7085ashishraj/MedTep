from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import EmergencyContactForm, LoginForm, MedicalProfileForm, RegistrationForm
from .models import EmergencyContact, MedicalProfile
from .services import save_emergency_contact


def _safe_next(request):
    candidate = (
        request.POST.get("next", "") if request.method == "POST"
        else request.GET.get("next", "")
    )
    if url_has_allowed_host_and_scheme(
        candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        return candidate
    return resolve_url(settings.LOGIN_REDIRECT_URL)


@sensitive_post_parameters()
@never_cache
@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    form = RegistrationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save()
            MedicalProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, "Your account is ready. Add your medical details when you're ready.")
        return redirect("accounts:profile_edit")
    return render(request, "accounts/auth_form.html", {
        "form": form, "is_registration": True,
    })


@sensitive_post_parameters()
@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(_safe_next(request))
    form = LoginForm(request=request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Welcome back. You're signed in.")
        return redirect(_safe_next(request))
    return render(request, "accounts/auth_form.html", {
        "form": form, "is_registration": False, "next": _safe_next(request),
    })


@never_cache
@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You've been signed out.")
    return redirect("core:home")


@never_cache
@login_required
@require_GET
def profile_detail(request):
    profile = MedicalProfile.objects.filter(user=request.user).first()
    contacts = profile.emergency_contacts.all() if profile else []
    return render(request, "accounts/profile.html", {"profile": profile, "contacts": contacts})


@sensitive_post_parameters()
@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    profile = MedicalProfile.objects.filter(user=request.user).first()
    form = MedicalProfileForm(
        request.POST if request.method == "POST" else None,
        instance=profile or MedicalProfile(user=request.user),
    )
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            # get_or_create also handles existing admin accounts without a profile.
            profile, _ = MedicalProfile.objects.get_or_create(user=request.user)
            for field in ("blood_group", "allergies", "medical_conditions"):
                setattr(profile, field, form.cleaned_data[field])
            profile.save()
        messages.success(request, "Your medical profile has been saved.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile_form.html", {"form": form})


@sensitive_post_parameters()
@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def contact_add(request):
    profile = MedicalProfile.objects.filter(user=request.user).first()
    if profile is None:
        messages.info(request, "Save your medical profile before adding a contact.")
        return redirect("accounts:profile_edit")
    form = EmergencyContactForm(
        request.POST if request.method == "POST" else None, profile=profile,
    )
    if request.method == "POST" and form.is_valid():
        save_emergency_contact(profile=profile, data=form.cleaned_data)
        messages.success(request, "Emergency contact added.")
        return redirect("accounts:profile")
    return render(request, "accounts/contact_form.html", {"form": form, "is_edit": False})


@sensitive_post_parameters()
@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def contact_edit(request, pk):
    contact = get_object_or_404(EmergencyContact, pk=pk, profile__user=request.user)
    form = EmergencyContactForm(
        request.POST if request.method == "POST" else None,
        instance=contact, profile=contact.profile,
    )
    if request.method == "POST" and form.is_valid():
        save_emergency_contact(profile=contact.profile, data=form.cleaned_data, contact=contact)
        messages.success(request, "Emergency contact updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/contact_form.html", {"form": form, "is_edit": True})


@sensitive_post_parameters()
@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def contact_delete(request, pk):
    contact = get_object_or_404(EmergencyContact, pk=pk, profile__user=request.user)
    if request.method == "POST":
        contact.delete()
        messages.success(request, "Emergency contact removed.")
        return redirect("accounts:profile")
    return render(request, "accounts/contact_confirm_delete.html", {"contact": contact})
