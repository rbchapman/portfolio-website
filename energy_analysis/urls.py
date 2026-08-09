from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EnergyDataViewSet
from .site_copy_views import SiteCopyView

router = DefaultRouter()
router.register(r'energy', EnergyDataViewSet, basename='energy')

urlpatterns = [
    path('api/site-copy/', SiteCopyView.as_view(), name='site-copy'),
    path('api/', include(router.urls)),
]
