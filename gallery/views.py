from functools import wraps
import os
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator, available_attrs
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect

# TODO : move these classes to a shared library

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
            self.object = super(CachedSingleObjectMixin, self).get_object(*args, **kwargs)
        return self.object


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


class UserHasPermMixin(object):

    '''Require user permissions on the object when dispatching the single object mixed-in view.'''
    user_perm = None
    raise_exception = False

    def user_has_perm(self, user):
        return user.has_perm(user_perm)

    def dispatch(self, request, *args, **kwargs):
        if self.user_has_perm(request.user):
            return super(UserHasPermMixin, self).dispatch(request, *args, **kwargs)

        if self.raise_exception or not hasattr(self, 'get_error_url'):
            raise PermissionDenied

        return HttpResponseRedirect(self.get_error_url())


class ObjectHasPermMixin(UserHasPermMixin, CachedSingleObjectMixin):

    '''Require user permissions on the object when dispatching the single object mixed-in view.'''
    user_perm = None
    raise_exception = False

    def user_has_perm(self, user):

        obj = self.get_object()
        perm_method = getattr(obj, self.user_perm)
        if perm_method(user):
            return True
        return False


class ModelHasPermMixin(UserHasPermMixin):

    """Require user permissions on the model when dispatching the mixed-in view."""

    def user_has_perm(self, user):

        model = self.get_model()
        perm_method = getattr(model, self.user_perm)
        if perm_method(user):
            return True
        return False
