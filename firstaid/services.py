import re
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from .models import EmergencyHelpline, FirstAidGuide
from .validators import validate_https_source

ICONS = {
    "adult-cpr": "heart-pulse", "severe-bleeding": "droplet", "thermal-burns": "thermometer-half",
    "adult-choking": "lungs", "recovery-position": "person-heart",
}
SOURCE_LABELS = {
    "www.nhs.uk": "NHS", "www.sja.org.uk": "St John Ambulance",
    "www.resus.org.uk": "Resuscitation Council UK", "www.mha.gov.in": "Ministry of Home Affairs",
    "nhm.gov.in": "National Health Mission",
}


def source_link(url):
    try:
        validate_https_source(url)
    except ValidationError:
        return None
    host = urlsplit(url).hostname
    return {"label": SOURCE_LABELS.get(host, host), "url": url}


def public_guides(query=""):
    guides = FirstAidGuide.objects.filter(
        is_published=True, source_checked_on__lte=timezone.localdate(), steps__isnull=False,
    ).prefetch_related("steps").distinct()
    if query:
        guides = guides.filter(Q(title__icontains=query) | Q(summary__icontains=query))
    # The small educational catalogue also checks URLs at read time so even
    # malformed direct database writes cannot expose an unsafe source link.
    return [guide for guide in guides if source_link(guide.source_url)]


def guide_sources(guide):
    return [link for url in (guide.source_url, guide.supporting_source_url) if url and (link := source_link(url))]


def public_helplines():
    candidates = EmergencyHelpline.objects.filter(
        is_active=True, verified_on__lte=timezone.localdate(),
    ).order_by("-is_nationwide", "number", "region", "pk")
    lines = [line for line in candidates if source_link(line.source_url)
             and re.fullmatch(r"\+?[0-9]{2,15}", line.number) and line.number.strip("+0")]
    priority = {"112": 0, "108": 1, "102": 2}
    return sorted(lines, key=lambda line: (not line.is_nationwide, priority.get(line.number, 99), line.number, line.region, line.pk))


def guide_data(guide, *, include_steps=False):
    data = {
        "slug": guide.slug, "title": guide.title, "summary": guide.summary,
        "audience": guide.audience, "urgent_advice": guide.urgent_advice,
        "warnings": guide.warnings, "source_checked_on": guide.source_checked_on,
        "clinical_reviewed_on": guide.reviewed_on, "sources": guide_sources(guide),
    }
    if include_steps:
        data["steps"] = [{"position": step.position, "heading": step.heading, "instruction": step.instruction} for step in guide.steps.all()]
    return data
