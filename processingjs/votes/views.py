from django.shortcuts import render
from django.views.generic import View, CreateView, DeleteView, DetailView
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.utils.translation import ugettext as _

from uofa.views import PostOnlyMixin, CSRFExemptMixin, LoggedInMixin, JsonResponseMixin, ObjectHasPermMixin
from votes.models import Vote, VoteForm

class VoteView(JsonResponseMixin):
    model = Vote
    form_class = VoteForm

    def get_success_url(self):
        return reverse('vote-view', kwargs={'pk': self.object.id})

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get_data(self, context):
        """
        Returns a serializable Vote object
        """
        data = super(VoteView, self).get_data(context)
        obj = context.get('object')
        if obj:
            data['id'] = obj.id
            data['voted_by'] = '%s' % obj.voted_by
            data['status'] = '%s' % obj.get_status_display()
            data['submission'] = '%s' % obj.submission
            data['created_at'] = '%s' % obj.created_at
        return data


class ShowVoteView(LoggedInMixin, VoteView, DetailView):
    pass

class NoOpView(LoggedInMixin, VoteView, View):

    def get(self, request, *args, **kwargs):
        return self.render_to_response({'status': 'ok'})


class CreateVoteView(CSRFExemptMixin, PostOnlyMixin, VoteView, CreateView):

    def get_form_kwargs(self):
        '''Get form data from the request url'''
        kwargs = super(CreateVoteView, self).get_form_kwargs()
        resolved_kwargs = self.request.resolver_match.kwargs
        kwargs.update({
            'data': {
                'submission': resolved_kwargs.get('submission'),
                'status': resolved_kwargs.get('status'),
            }
        })
        return kwargs

    def form_valid(self, form):
        # Throw exception if user isn't allowed to vote on this submission
        submission = form.instance.submission
        if submission and submission.can_vote(self.request.user):
            # Set voted_by to current user
            form.instance.voted_by = self.request.user

            return super(CreateVoteView, self).form_valid(form)
        raise PermissionDenied

    def form_invalid(self, form):
        raise SuspiciousOperation


class DeleteVoteView(CSRFExemptMixin, PostOnlyMixin, ObjectHasPermMixin, VoteView, DeleteView):

    user_perm = 'can_delete'
    raise_exception = True

    def _get_object(self, queryset=None):
        '''Determine the vote pk via the user and submission ids'''
        if queryset is None:
            queryset = self.get_queryset()

        resolved_kwargs = self.request.resolver_match.kwargs
        submission_id = resolved_kwargs.get('submission')
        voted_by = self.request.user.id
        queryset = queryset.filter(submission__exact=submission_id,
                                   voted_by__exact=voted_by)

        # Get the single item from the filtered queryset
        try:
            return queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

    def get_success_url(self):
        return reverse('vote-ok')
