import os
import re
from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.utils.decorators import method_decorator, available_attrs
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.core.urlresolvers import reverse, resolve, get_script_prefix
from django.contrib.auth import REDIRECT_FIELD_NAME


class LoggedInMixin(object):
    """Require login when dispatching the mixed-in view."""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class CachedSingleObjectMixin(object):

    def __init__(self):
        self.object = None

    def get_object(self, *args, **kwargs):
        '''Caches the object fetched by get_object'''
        if not self.object:
            self.object = self._get_object(*args, **kwargs)
        return self.object

    def _get_object(self, *args, **kwargs):
        '''Allows subclasses to override the get_object method'''
        return super(CachedSingleObjectMixin, self).get_object(*args, **kwargs)


class TemplatePathMixin(object):

    template_path = ''

    @classmethod
    def prepend_template_path(cls, *argv):
        return os.path.join(cls.template_dir, *argv)


class PostOnlyMixin(object):

    def dispatch(self, request, *args, **kwargs):
        method = request.method.lower()
        if (method == 'post') or (method == 'put'):
            return super(PostOnlyMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied


# https://gist.github.com/cyberdelia/1231560
class CSRFExemptMixin(object):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptMixin, self).dispatch(*args, **kwargs)


class UserHasPermMixin(object):

    '''Require user permissions on the object when dispatching the single object mixed-in view.'''
    user_perm = None
    raise_exception = False

    def user_has_perm(self, user, perm):
        return user.has_perm(perm)

    def dispatch(self, request, *args, **kwargs):
        if self.user_has_perm(request.user, self.user_perm):
            return super(UserHasPermMixin, self).dispatch(request, *args, **kwargs)

        if self.raise_exception or not hasattr(self, 'get_error_url'):
            raise PermissionDenied

        return HttpResponseRedirect(self.get_error_url())


class MethodUserPermMixin(UserHasPermMixin):

    '''Require per-HTTP-method user permissions on the object when dispatching the single object mixed-in view.'''
    method_user_perm = None # { 'METHOD' : 'user_perm' }

    def request_has_perm(self, request):
        allowed = False
        if self.method_user_perm:
            if request.method in self.method_user_perm:
                perm = self.method_user_perm[request.method]
                if perm:
                    allowed = self.user_has_perm(request.user, perm)
                else:
                    allowed = False
            else:
                allowed = True
        elif self.user_perm:
            allowed = self.user_has_perm(request.user, self.user_perm)

        return allowed

    def dispatch(self, request, *args, **kwargs):
        if self.request_has_perm(request):
            return super(UserHasPermMixin, self).dispatch(request, *args, **kwargs)

        if self.raise_exception:
            raise PermissionDenied

        elif not self.request.user.is_authenticated():
            return redirect_to_login(self.request.path)

        elif not hasattr(self, 'get_error_url'):
            raise PermissionDenied

        return HttpResponseRedirect(self.get_error_url())


class _ObjectPermMixin(object):

    '''Require user permissions on the object when dispatching the single object mixed-in view.'''
    def user_has_perm(self, user, perm):

        obj = self.get_object()
        perm_method = getattr(obj, perm)
        if perm_method(user):
            return True
        return False


class ObjectHasPermMixin(_ObjectPermMixin, UserHasPermMixin, CachedSingleObjectMixin):
    pass


class MethodObjectHasPermMixin(_ObjectPermMixin, MethodUserPermMixin, CachedSingleObjectMixin):
    pass


class ModelHasPermMixin(UserHasPermMixin):

    """Require user permissions on the model when dispatching the mixed-in view."""

    def user_has_perm(self, user, perm):

        model = self.get_model()
        perm_method = getattr(model, perm)
        if perm_method(user):
            return True
        return False


class JsonResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        return {}
