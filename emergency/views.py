from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_POST

from accounts.models import EmergencyContact

from .forms import EmergencyRequestForm
from .models import AmbulanceRequest, EmergencyRequest
from .services import build_emergency_message, build_share_options, google_maps_url, save_sos_request


@never_cache
@login_required
@require_GET
def start(request):
    return render(request, "emergency/start.html", {
        "form": EmergencyRequestForm(),
        "recent_requests": EmergencyRequest.objects.filter(user=request.user)[:5],
    })


@sensitive_post_parameters()
@never_cache
@require_POST
def create(request):
    wants_json = request.headers.get("Accept") == "application/json"
    if not request.user.is_authenticated:
        if wants_json:
            return JsonResponse({"error": "Sign in again before saving an SOS request."}, status=401)
        # After login, return to a GET page rather than the POST-only create URL.
        return redirect_to_login(reverse("emergency:start"), login_url=reverse("accounts:login"))
    form = EmergencyRequestForm(request.POST)
    if not form.is_valid():
        if wants_json:
            return JsonResponse({"errors": dict(form.errors)}, status=400)
        return render(request, "emergency/start.html", {"form": form}, status=400)
    emergency, created = save_sos_request(user=request.user, **form.cleaned_data)
    url = reverse("emergency:detail", kwargs={"pk": emergency.pk})
    if wants_json:
        return JsonResponse({"url": url, "created": created}, status=201 if created else 200)
    return redirect(url)


@never_cache
@login_required
@require_GET
def detail(request, pk):
    emergency = get_object_or_404(EmergencyRequest, pk=pk, user=request.user)
    message = build_emergency_message(emergency)
    contacts = EmergencyContact.objects.filter(profile__user=request.user).order_by("-is_primary", "name", "pk")
    return render(request, "emergency/detail.html", {
        "emergency": emergency, "share_message": message,
        "ambulance": AmbulanceRequest.objects.filter(emergency=emergency).first(),
        "maps_url": google_maps_url(emergency),
        "general_share": build_share_options(message),
        "contact_shares": [{"contact": contact, "options": build_share_options(message, contact.phone)} for contact in contacts],
    })
