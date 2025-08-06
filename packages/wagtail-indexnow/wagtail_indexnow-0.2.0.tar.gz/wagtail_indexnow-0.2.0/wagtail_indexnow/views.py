from django.http import Http404, HttpResponse
from django.utils.crypto import constant_time_compare
from django.views import View

from .utils import get_key


class KeyView(View):
    def get(self, request, key):
        if not constant_time_compare(key, get_key()):
            raise Http404()

        return HttpResponse(key)
