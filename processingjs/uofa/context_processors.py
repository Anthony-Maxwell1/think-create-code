from django.conf import settings

def analytics(request):
    """
    Adds static-related context variables to the context.

    """
    return {'ALLOW_ANALYTICS': settings.ALLOW_ANALYTICS}
