from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET

from .forms import CareSearchForm


@require_GET
def home(request):
    search_form = CareSearchForm()
    facility_url = reverse("facilities:nearby")
    quick_actions = [
        {
            "key": "hospitals", "title": "Nearby Hospitals", "icon": "hospital",
            "description": "Find a place for the care you need.",
            "href": facility_url, "status": "Explore nearby care",
        },
        {
            "key": "ambulance", "title": "Ambulance", "icon": "truck-front",
            "description": "Request transport and follow its progress.",
            "href": reverse("emergency:ambulance_start"), "status": "Project request & status",
        },
        {
            "key": "blood-banks", "title": "Blood Banks", "icon": "droplet",
            "description": "Look for blood banks in your area.", "tone": "teal",
            "href": facility_url + "?facility_type=blood_bank", "status": "Browse blood banks",
        },
        {
            "key": "pharmacies", "title": "Pharmacies", "icon": "capsule",
            "description": "Find a pharmacy close to you.", "tone": "teal",
            "href": facility_url + "?facility_type=pharmacy", "status": "Browse pharmacies",
        },
        {
            "key": "first-aid", "title": "First Aid", "icon": "bandaid",
            "description": "Clear, step-by-step guides for urgent moments.",
            "href": reverse("firstaid:guide_list"), "status": "Read adult first-aid guides",
        },
        {
            "key": "helplines", "title": "Helplines", "icon": "telephone",
            "description": "Keep essential emergency numbers in reach.",
            "href": reverse("firstaid:helplines"), "status": "Numbers & coverage",
        },
    ]
    return render(request, "core/home.html", {
        "search_form": search_form,
        "quick_actions": quick_actions,
    })
