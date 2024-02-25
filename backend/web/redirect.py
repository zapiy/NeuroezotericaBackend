from django.urls import reverse
from django.http import HttpResponseRedirect
from urllib.parse import urlencode


def resolve_url(viewname, *args, **kwargs):
    url = reverse(viewname, args = args)
    if kwargs:
        params = urlencode(kwargs)
        url += f"?{params}"
    return url

def redirect(viewname, *args, **kwargs):
    return HttpResponseRedirect(resolve_url(viewname, *args, **kwargs))
