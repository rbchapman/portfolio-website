from django.contrib import admin
from django.utils.html import format_html
from .models import Photographer, PhotoShoot, Photo, Campaign
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

class PhotoInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Photo
    fields = ['image', 'title', 'is_portrait', 'show', 'display_order']
    readonly_fields = ['display_order']
    extra = 0
    ordering = ['photo_shoot_order']
    
    def display_order(self, obj):
        return format_html('<strong>{}</strong>', obj.photo_shoot_order)
    display_order.short_description = 'Order'

@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ['name', 'instagram', 'website']
    search_fields = ['name']

@admin.register(Campaign)
class CampaignAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'client', 'order', 'video_url', 'web_url', 'type', 'date']
    list_filter = ['type']
    search_fields = ['title', 'description', 'client']
    ordering = ['order']

@admin.register(PhotoShoot)
class PhotoShootAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'photographer', 'campaign', 'date', 'location', 'order', 'show']
    list_filter = ['show', 'photographer', 'campaign']
    search_fields = ['title', 'description']
    ordering = ['order']
    inlines = [PhotoInline]

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'photo_shoot', 'photographer', 'order_display', 'carousel_order_display', 'show']
    list_filter = ['show', 'is_portrait', 'photo_shoot', 'photographer']
    search_fields = ['title', 'description']
    ordering = ['photo_shoot_order']
    readonly_fields = ['photographer', 'order_display', 'carousel_order_display']
    
    def order_display(self, obj):
        return format_html('<span style="background-color: #f0f0f0; padding: 3px 8px; border-radius: 10px; font-weight: bold;">{}</span>', obj.photo_shoot_order)
    order_display.short_description = 'Photo Order'
    
    def carousel_order_display(self, obj):
        if obj.carousel_order is not None:
            return format_html('<span style="background-color: #e6f7ff; padding: 3px 8px; border-radius: 10px; font-weight: bold;">{}</span>', obj.carousel_order)
        return '-'
    carousel_order_display.short_description = 'Carousel Order'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['photographer', 'order_display', 'carousel_order_display']
        return []
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new photo
            obj.photographer = obj.photo_shoot.photographer
        super().save_model(request, obj, form, change)