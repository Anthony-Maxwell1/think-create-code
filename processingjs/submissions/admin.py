from django.contrib import admin
from submissions.models import Submission

class SubmissionAdmin(admin.ModelAdmin):
    list_filter = ('submitted_by','exhibition_id',)

admin.site.register(Submission, SubmissionAdmin)
