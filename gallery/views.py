from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoggedInMixin(object):
    """Require login when dispatching the mixed-in view."""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)
