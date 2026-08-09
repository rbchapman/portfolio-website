from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SiteCopy


class SiteCopyView(APIView):
    """Return all editable site copy as a single key/value object."""

    permission_classes = [AllowAny]

    def get(self, request):
        copy = dict(SiteCopy.objects.values_list('key', 'value'))
        return Response(copy)
