"""Only used by isolated error-page tests; not included by config.urls."""
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.urls import path

from config.urls import urlpatterns as application_urls


def error_view(request, code):
    errors = {
        400: SuspiciousOperation, 403: PermissionDenied,
        404: Http404, 500: RuntimeError,
    }
    raise errors[code]("PRIVATE diagnostic text must not reach a public error page")


urlpatterns = [path("_ui-test-error/<int:code>/", error_view), *application_urls]
