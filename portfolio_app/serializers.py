from rest_framework import serializers
from .models import Photographer, PhotoShoot, Photo, Campaign

class PhotographerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photographer
        fields = ['id', 'name', 'instagram', 'website']

class SimplePhotoSerializer(serializers.ModelSerializer):
    photographer = PhotographerSerializer(read_only=True)

    class Meta:
        model = Photo
        fields = [
            'id', 'image', 'title', 'description', 
            'is_portrait', 'photographer', 'photo_shoot_order',
            'carousel_order', 'show'
        ]

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'description',
            'type', 'client', 'video_url', 'web_url',
            'date', 'order'
        ]
class PhotoShootSerializer(serializers.ModelSerializer):
    photographer = PhotographerSerializer(read_only=True)
    photographer_id = serializers.IntegerField(write_only=True)
    photos = SimplePhotoSerializer(many=True, read_only=True)
    photos_count = serializers.SerializerMethodField()
    campaign = CampaignSerializer(read_only=True)
    campaign_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    

    class Meta:
        model = PhotoShoot
        fields = [
            'id', 'title', 'date', 'photographer', 'photographer_id', 'campaign', 'campaign_id',
            'description', 'location', 'order', 'show',
            'photos_count', 'photos', 'created_at', 'updated_at'
        ]

    def get_photos_count(self, obj):
        return obj.photos.count()

class PhotoSerializer(serializers.ModelSerializer):
    photographer = PhotographerSerializer(read_only=True)
    photographer_id = serializers.IntegerField(write_only=True)
    photo_shoot_id = serializers.IntegerField(write_only=True)
    shoot_slug = serializers.IntegerField(source='photo_shoot.order')
    class Meta:
        model = Photo
        fields = [
            'id', 'image', 'title', 'description',
            'photographer', 'photographer_id',
            'photo_shoot_id', 'shoot_slug',
            'is_portrait', 'photo_shoot_order',
            'carousel_order', 'show',
            'created_at', 'updated_at'
        ]

    def validate(self, data):
        if 'photographer_id' in data and 'photo_shoot_id' in data:
            photo_shoot = PhotoShoot.objects.get(id=data['photo_shoot_id'])
            if photo_shoot.photographer.id != data['photographer_id']:
                raise serializers.ValidationError(
                    "Photographer must match the photo shoot's photographer"
                )
        return data