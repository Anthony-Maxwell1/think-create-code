from django.views.generic import TemplateView
from harvard.django_auth_lti.mixins import LTIUtilityMixin, LTIRoleRestrictionMixin
from uofa.views import TemplatePathMixin, CSRFExemptMixin

# TODO - combine CSRFExemption and LTIUtility ?
class LTILoginView(CSRFExemptMixin, LTIUtilityMixin, TemplatePathMixin, TemplateView):

    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('lti.html')

    # TODO : if user's name isn't set, show page requesting one
    # once user name is set, redirect to self.request.POST['custom_page'] (or home)
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LTILoginView, self).get_context_data(**kwargs)
        context['post'] = self.request.POST.items()
        context['get'] = self.request.GET.items()
        context['lti_roles'] = self.current_user_roles()
        return context
