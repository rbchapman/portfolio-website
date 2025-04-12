from django.contrib import admin
from .models import Photographer, PhotoShoot, Photo, Campaign
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

class PhotoInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Photo
    fields = ['image', 'title', 'is_portrait', 'show', 'photo_shoot_order']
    extra = 0
    ordering = ['photo_shoot_order']
@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ['name', 'instagram', 'website', 'id']
    search_fields = ['name']
@admin.register(Campaign)
class CampaignAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'client', 'order', 'video_url', 'web_url', 'type', 'date']
    list_filter = ['type']
    search_fields = ['title', 'description', 'client'],
    ordering = ['order']
@admin.register(PhotoShoot)
class PhotoShootAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'photographer', 'campaign', 'date', 'location', 'order', 'show']
    list_filter = ['show', 'photographer', 'campaign']
    search_fields = ['title', 'description']
    ordering = ['order']
    inlines = [PhotoInline]
@admin.register(Photo)
class PhotoAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'photo_shoot', 'photographer', 'carousel_order', 'show']
    list_filter = ['show', 'is_portrait', 'photo_shoot', 'photographer']
    search_fields = ['title', 'description']
    ordering = ['photo_shoot_order']

    def get_readonly_fields(self, request, obj=None):
        return ['photographer'] if obj else []
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new photo
            obj.photographer = obj.photo_shoot.photographer
        super().save_model(request, obj, form, change)