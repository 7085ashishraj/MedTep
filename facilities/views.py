from django.core.paginator import InvalidPage
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes, renderer_classes,
)
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .forms import FacilitySearchForm
from .serializers import FacilityMatchSerializer
from .services import search_facilities


def page_query(params, number):
    query = params.copy()
    query["page"] = number
    return "?" + query.urlencode()


@never_cache
@require_GET
def nearby(request):
    form = FacilitySearchForm(request.GET)
    page = None
    origin = None
    markers = []
    if form.is_valid():
        try:
            page = search_facilities(form.cleaned_data)
        except InvalidPage as error:
            raise Http404("That results page does not exist.") from error
        if form.cleaned_data["latitude"] is not None:
            origin = {"latitude": form.cleaned_data["latitude"], "longitude": form.cleaned_data["longitude"]}
        markers = FacilityMatchSerializer(page.object_list, many=True).data
    response = render(request, "facilities/nearby.html", {
        "form": form, "page_obj": page, "has_location": origin is not None,
        "map_data": {"origin": origin, "results": markers},
        "previous_query": page_query(request.GET, page.previous_page_number()) if page and page.has_previous() else None,
        "next_query": page_query(request.GET, page.next_page_number()) if page and page.has_next() else None,
    }, status=200 if not form.errors else 400)
    # OSM requires a Referer; send only our origin across domains, not coordinates.
    response["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@never_cache
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def nearby_api(request):
    form = FacilitySearchForm(request.query_params)
    if not form.is_valid():
        return Response({"errors": dict(form.errors)}, status=400)
    try:
        page = search_facilities(form.cleaned_data)
    except InvalidPage as error:
        raise NotFound("That results page does not exist.") from error
    return Response({
        "count": page.paginator.count,
        "page": page.number,
        "pages": page.paginator.num_pages,
        "next": request.build_absolute_uri(page_query(request.query_params, page.next_page_number())) if page.has_next() else None,
        "previous": request.build_absolute_uri(page_query(request.query_params, page.previous_page_number())) if page.has_previous() else None,
        "results": FacilityMatchSerializer(page.object_list, many=True).data,
    })
