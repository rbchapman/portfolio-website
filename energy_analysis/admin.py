from django.contrib import admin

from .models import SiteCopy


@admin.register(SiteCopy)
class SiteCopyAdmin(admin.ModelAdmin):
    list_display = ('key', 'page', 'section', 'updated_at')
    list_filter = ('page', 'section')
    search_fields = ('key', 'value', 'page', 'section')
    ordering = ('page', 'section', 'key')
    readonly_fields = ('updated_at',)
