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
        # Thumbnail with improved quality
        'thumbnail': f"{cloudinary_base}/upload/c_fill,g_auto,w_400,h_400,q_85,f_auto,e_improve,fl_progressive/{cloudinary_id}",
        
        # Medium size for general display
        'medium': f"{cloudinary_base}/upload/c_fill,g_auto,w_800,q_90,f_auto,e_improve,fl_progressive/{cloudinary_id}",
        
        # Large for detailed viewing
        'large': f"{cloudinary_base}/upload/c_fill,g_auto,w_1200,q_90,f_auto,e_improve,fl_progressive/{cloudinary_id}",
        
        # Full resolution (original)
        'full': base_url
    }

class PhotographerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photographer
        fields = ['id', 'name', 'instagram', 'website']

class SimplePhotoSerializer(serializers.ModelSerializer):
    photographer = PhotographerSerializer(read_only=True)
    optimized_images = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = [
            'id', 'image', 'title', 'description', 
            'is_portrait', 'photographer', 'photo_shoot_order',
            'carousel_order', 'show', 'optimized_images'
        ]
    
    def get_optimized_images(self, obj):
        return get_optimized_images(obj.image)

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
    optimized_images = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = [
            'id', 'image', 'title', 'description',
            'photographer', 'photographer_id',
            'photo_shoot_id', 'shoot_slug',
            'is_portrait', 'photo_shoot_order',
            'carousel_order', 'show',
            'created_at', 'updated_at', 'optimized_images'
        ]

    def get_optimized_images(self, obj):
        return get_optimized_images(obj.image)

    def validate(self, data):
        if 'photographer_id' in data and 'photo_shoot_id' in data:
            photo_shoot = PhotoShoot.objects.get(id=data['photo_shoot_id'])
            if photo_shoot.photographer.id != data['photographer_id']:
                raise serializers.ValidationError(
                    "Photographer must match the photo shoot's photographer"
                )
        return data