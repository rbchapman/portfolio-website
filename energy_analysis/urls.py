from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnergyDataViewSet

router = DefaultRouter()
router.register(r'energy-data', EnergyDataViewSet, basename='energydata')

urlpatterns = [
    path('api/', include(router.urls)),
]