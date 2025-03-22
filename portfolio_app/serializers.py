from rest_framework import serializers
from .models import Photographer, PhotoShoot, Photo, Campaign

# Enhanced helper function for Cloudinary image optimization
def get_optimized_images(image):
    """Generate optimized image variants for Cloudinary with improved quality"""
    if not image:
        return None
        
    # Handle CloudinaryResource objects
    if hasattr(image, 'url'):
        # Get the base URL
        base_url = image.url
    else:
        # Handle it as a string if somehow it's not a CloudinaryResource
        base_url = str(image)
    
    # Extract cloudinary part
    try:
        # Form: https://res.cloudinary.com/your-cloud/image/upload/v1234/path/to/image.jpg
        cloudinary_id = base_url.split('/upload/')[-1]
        cloudinary_base = base_url.split('/upload/')[0]
    except (ValueError, IndexError, AttributeError):
        return {'full': base_url}  # Return original if parsing fails
    
    # Build URLs with transformations
    return {
        # Large for slightly lower resolution
        'large': f"{cloudinary_base}/upload/c_limit,w_1200,q_auto:good,f_auto/{cloudinary_id}",
        
        # Full resolution (original)
        'full': base_url
    }

class PhotographerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photographer
        fields = ['id', 'name', 'instagram', 'website']
class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'description',
            'type', 'client', 'video_url', 'web_url',
            'date', 'order'
        ]
class PhotoSerializer(serializers.ModelSerializer):
    photographer = PhotographerSerializer(read_only=True)
    optimized_images = serializers.SerializerMethodField()
    
    # Essential PhotoShoot metadata flattened directly into the Photo
    shoot_id = serializers.IntegerField(source='photo_shoot.id')
    shoot_title = serializers.CharField(source='photo_shoot.title')
    shoot_date = serializers.DateField(source='photo_shoot.date')
    photo_count = serializers.SerializerMethodField()
    shoot_location = serializers.CharField(source='photo_shoot.location')
    shoot_order = serializers.IntegerField(source='photo_shoot.order')
    
    class Meta:
        model = Photo
        fields = [
            'id', 'image', 'title', 'description', 
            'photographer', 'is_portrait', 'photo_shoot_order',
            'carousel_order', 'show', 'optimized_images',
            'shoot_id', 'shoot_title', 'shoot_date', 'shoot_location', 'shoot_order', 'photo_count'
        ]
    
    def get_optimized_images(self, obj):
        return get_optimized_images(obj.image)
    def get_photo_count(self, obj):
        return obj.photo_shoot.photos.count()
    def validate(self, data):
        if 'photographer_id' in data and 'photo_shoot_id' in data:
            photo_shoot = PhotoShoot.objects.get(id=data['photo_shoot_id'])
        if photo_shoot.photographer.id != data['photographer_id']:
            raise serializers.ValidationError(
                "Photographer must match the photo shoot's photographer"
            )
        return data
    
class PhotoShootSerializer(serializers.ModelSerializer):
    photographer = PhotographerSerializer(read_only=True)
    photographer_id = serializers.IntegerField(write_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
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