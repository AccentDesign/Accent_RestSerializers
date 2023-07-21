from django.db.models import ProtectedError

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .utils import set_rollback


def protected_entities_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data["status_code"] = response.status_code

    if isinstance(exc, ProtectedError):
        set_rollback()
        return Response(
            {"detail": _("Protected Error.")}, status=status.HTTP_400_BAD_REQUEST
        )

    return response
