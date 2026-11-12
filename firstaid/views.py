from django.core.paginator import InvalidPage, Paginator
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, authentication_classes, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .forms import GuideSearchForm
from .services import ICONS, guide_data, guide_sources, public_guides, public_helplines, source_link


def find_guide(slug):
    for guide in public_guides():
        if guide.slug == slug:
            return guide
    raise Http404("This guide is unavailable or is not published.")


def search_page(form):
    try:
        return Paginator(public_guides(form.cleaned_data["q"]), 20).page(form.cleaned_data["page"] or 1)
    except InvalidPage as exc:
        raise Http404("That guide page does not exist.") from exc


def page_query(params, number):
    query = params.copy()
    query["page"] = number
    return "?" + query.urlencode()


@require_GET
def guide_list(request):
    form = GuideSearchForm(request.GET)
    page = search_page(form) if form.is_valid() else None
    return render(request, "firstaid/guide_list.html", {
        "form": form, "page_obj": page,
        "cards": [{"guide": guide, "icon": ICONS.get(guide.slug, "bandaid")} for guide in page] if page else [],
        "previous_query": page_query(request.GET, page.previous_page_number()) if page and page.has_previous() else None,
        "next_query": page_query(request.GET, page.next_page_number()) if page and page.has_next() else None,
    }, status=400 if form.errors else 200)


@require_GET
def guide_detail(request, slug):
    guide = find_guide(slug)
    return render(request, "firstaid/guide_detail.html", {
        "guide": guide, "sources": guide_sources(guide), "icon": ICONS.get(guide.slug, "bandaid"),
    })


@require_GET
def helplines(request):
    return render(request, "firstaid/helplines.html", {
        "lines": [{"line": line, "source": source_link(line.source_url)} for line in public_helplines()],
    })


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def guide_list_api(request):
    form = GuideSearchForm(request.query_params)
    if not form.is_valid():
        return Response({"errors": dict(form.errors)}, status=400)
    page = search_page(form)
    return Response({
        "count": page.paginator.count,
        "next": request.build_absolute_uri(page_query(request.query_params, page.next_page_number())) if page.has_next() else None,
        "previous": request.build_absolute_uri(page_query(request.query_params, page.previous_page_number())) if page.has_previous() else None,
        "results": [guide_data(guide) for guide in page],
    })


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def guide_detail_api(request, slug):
    return Response(guide_data(find_guide(slug), include_steps=True))


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def helplines_api(request):
    return Response({"results": [{
        "name": line.name, "number": line.number, "region": line.region,
        "is_nationwide": line.is_nationwide, "description": line.description,
        "source_checked_on": line.verified_on, "source": source_link(line.source_url),
        "call_url": "tel:" + line.number,
    } for line in public_helplines()]})
