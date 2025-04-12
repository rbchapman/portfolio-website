from django.shortcuts import render
from rest_framework import viewsets
from .models import Photographer, PhotoShoot, Photo, Campaign
from .serializers import (
    PhotographerSerializer,
    PhotoShootSerializer,
    PhotoSerializer,
    CampaignSerializer
)

class PhotographerViewSet(viewsets.ModelViewSet):
    queryset = Photographer.objects.all()
    serializer_class = PhotographerSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']
    def get_queryset(self):
        return super().get_queryset()

class PhotoShootViewSet(viewsets.ModelViewSet):
    serializer_class = PhotoShootSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = PhotoShoot.objects.all()
        # Always filter to only your photoshoots
        # Replace with your actual photographer ID
        my_photographer_id = 1
        queryset = queryset.filter(photographer_id=my_photographer_id)
        
        # Filter by show status
        show = self.request.query_params.get('show', True)
        if show:
            queryset = queryset.filter(show=show)
        
        return queryset.order_by('order')

class PhotoViewSet(viewsets.ModelViewSet):
    serializer_class = PhotoSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = Photo.objects.all()

        # Only return photos by other photographers
        my_photographer_id = 1
        queryset = queryset.exclude(photographer_id=my_photographer_id)

        # Filter by show status
        show = self.request.query_params.get('show', True)
        if show:
            queryset = queryset.filter(show=show)

        # Filter carousel photos
        carousel = self.request.query_params.get('carousel')
        if carousel:
            queryset = queryset.exclude(
                carousel_order=None
            ).order_by('carousel_order')
            return queryset

        # Default ordering by photo_shoot_order
        return queryset.order_by('photo_shoot_order')