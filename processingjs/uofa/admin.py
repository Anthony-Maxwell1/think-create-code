from django.contrib import admin
from uofa.models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'username',)

admin.site.register(User, UserAdmin)
