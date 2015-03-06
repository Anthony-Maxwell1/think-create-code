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
