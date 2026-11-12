from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_http_methods

from .ambulance_services import ambulance_snapshot, request_ambulance, update_ambulance
from .forms import AmbulanceDashboardForm, AmbulanceOperatorForm
from .models import AmbulanceRequest, EmergencyRequest
from .permissions import operator_required
from .services import google_maps_url


@never_cache
@login_required
@require_GET
def start(request):
    return render(request, "emergency/ambulance_start.html", {
        "locations": EmergencyRequest.objects.filter(user=request.user).select_related("ambulance_request")[:10],
    })


@never_cache
@require_http_methods(["GET", "POST"])
def request_transport(request, pk):
    if not request.user.is_authenticated:
        return redirect_to_login(request.path, login_url=reverse("accounts:login"))
    emergency = get_object_or_404(EmergencyRequest, pk=pk, user=request.user)
    existing = AmbulanceRequest.objects.filter(emergency=emergency).first()
    if existing:
        return redirect("emergency:ambulance_detail", pk=existing.pk)
    error = None
    if request.method == "POST":
        try:
            ambulance, _ = request_ambulance(user=request.user, emergency_pk=pk)
        except ValidationError as exc:
            error = " ".join(exc.messages)
        else:
            return redirect("emergency:ambulance_detail", pk=ambulance.pk)
    return render(request, "emergency/ambulance_request.html", {
        "emergency": emergency, "maps_url": google_maps_url(emergency), "error": error,
        "can_request": emergency.status == EmergencyRequest.Status.ACTIVE,
    }, status=400 if error else 200)


def owned_ambulance(request, pk):
    return get_object_or_404(
        AmbulanceRequest.objects.select_related("emergency", "facility").prefetch_related("status_events"),
        pk=pk, emergency__user=request.user,
    )


@never_cache
@login_required
@require_GET
def detail(request, pk):
    ambulance = owned_ambulance(request, pk)
    return render(request, "emergency/ambulance_detail.html", {
        "ambulance": ambulance, "snapshot": ambulance_snapshot(ambulance),
        "maps_url": google_maps_url(ambulance.emergency),
    })


@never_cache
@login_required
@require_GET
def status(request, pk):
    return JsonResponse(ambulance_snapshot(owned_ambulance(request, pk)))


@never_cache
@operator_required
@require_GET
def dashboard(request):
    form = AmbulanceDashboardForm(request.GET)
    rows = AmbulanceRequest.objects.select_related("emergency__user", "facility")
    counts = rows.aggregate(
        requested=Count("pk", filter=Q(status="requested")),
        progressing=Count("pk", filter=Q(status__in=["accepted", "on_the_way"])),
        completed=Count("pk", filter=Q(status="completed")),
    )
    page = None
    if form.is_valid():
        chosen = form.cleaned_data["status"] or "open"
        if chosen == "open":
            rows = rows.exclude(status="completed")
        elif chosen != "all":
            rows = rows.filter(status=chosen)
        try:
            page = Paginator(rows, 25).page(form.cleaned_data["page"] or 1)
        except InvalidPage as exc:
            raise Http404("That queue page does not exist.") from exc
    def page_query(number):
        params = request.GET.copy()
        params["page"] = number
        return "?" + params.urlencode()
    return render(request, "emergency/operator_dashboard.html", {
        "form": form, "page_obj": page, "counts": counts,
        "previous_query": page_query(page.previous_page_number()) if page and page.has_previous() else None,
        "next_query": page_query(page.next_page_number()) if page and page.has_next() else None,
    }, status=400 if form.errors else 200)


@sensitive_post_parameters()
@never_cache
@operator_required
@require_http_methods(["GET", "POST"])
def operator_update(request, pk):
    ambulance = get_object_or_404(
        AmbulanceRequest.objects.select_related("emergency__user", "facility").prefetch_related("status_events__changed_by"), pk=pk,
    )
    form = AmbulanceOperatorForm(request.POST if request.method == "POST" else None, ambulance=ambulance)
    code = 200
    if request.method == "POST":
        valid = form.is_valid()
        if form.cleaned_data.get("expected_version") is not None and form.cleaned_data["expected_version"] != ambulance.version:
            form.add_error(None, "Another operator changed this request. Reload the latest version before saving.")
            code = 409
        elif valid:
            try:
                update_ambulance(operator=request.user, pk=pk, **form.cleaned_data)
            except ValidationError as exc:
                form.add_error(None, exc)
                code = 409 if exc.code == "stale" else 400
            else:
                messages.success(request, "Project request updated. No external provider has been contacted.")
                return redirect("emergency:operator_update", pk=pk)
        else:
            code = 400
    return render(request, "emergency/operator_update.html", {
        "ambulance": ambulance, "form": form,
        "maps_url": google_maps_url(ambulance.emergency),
    }, status=code)
