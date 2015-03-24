from django.contrib import admin
from uofa.models import User

class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('password',)
    list_display = ('username', 'first_name',)

admin.site.register(User, UserAdmin)
