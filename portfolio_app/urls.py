from django.urls import path, include
from rest_framework import routers
from . import views

# Router to handle API routes
router = routers.DefaultRouter()
router.register(r'photographers', views.PhotographerViewSet)
router.register(r'photo-shoots', views.PhotoShootViewSet, basename='photo-shoot')
router.register(r'photos', views.PhotoViewSet, basename='photo')
router.register(r'campaigns', views.CampaignViewSet, basename='campaign')

# FRONT END URLS
urlpatterns = [
    # API ROUTES
    path('api/', include(router.urls)),
]