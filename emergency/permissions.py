from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

OPERATOR_PERMISSIONS = (
    "emergency.view_ambulancerequest", "emergency.change_ambulancerequest",
)


def can_operate(user):
    return user.is_authenticated and user.is_active and user.is_staff and user.has_perms(OPERATOR_PERMISSIONS)


def operator_required(view):
    @wraps(view)
    @login_required
    def checked(request, *args, **kwargs):
        if not can_operate(request.user):
            raise PermissionDenied("This dashboard requires an authorised ambulance operator.")
        return view(request, *args, **kwargs)
    return checked
