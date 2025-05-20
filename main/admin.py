from django.contrib import admin

# Register your models here.
from .models import Lovelist

@admin.register(Lovelist)
class LovelistAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'artist', 'cover_url')