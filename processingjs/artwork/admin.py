from django.contrib import admin
from artwork.models import Artwork

class ArtworkAdmin(admin.ModelAdmin):
    readonly_fields = ('shared',)
    list_filter = ('author',)

admin.site.register(Artwork, ArtworkAdmin)
