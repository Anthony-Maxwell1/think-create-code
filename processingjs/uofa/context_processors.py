from django.conf import settings

def analytics(request):
    """
    Adds static-related context variables to the context.

    """
    return {'ALLOW_ANALYTICS': settings.ALLOW_ANALYTICS}

def referer(request):
    """
    Adds the HTTP_REFERER request META to the context.

    """
    return {'HTTP_REFERER': request.META.get('HTTP_REFERER')}

def base_url(request):
    """
    Adds the application BASE_URL to the context.
    """
    if request.is_secure():
        scheme = 'https://'
    else:
        scheme = 'http://'

    return {'BASE_URL': scheme + request.get_host(),}
