from rest_framework import serializers
from .models import Photographer, PhotoShoot, Photo, Campaign

# Enhanced helper function for Cloudinary image optimization
def get_cloudinary_urls(image):
    """Generate optimized image variants for Cloudinary with improved face detection"""
    if not image:
        return None
        
    # Handle CloudinaryResource objects
    if hasattr(image, 'url'):
        base_url = image.url
    else:
        base_url = str(image)
    
    # Extract cloudinary part
    try:
        cloudinary_id = base_url.split('/upload/')[-1]
        cloudinary_base = base_url.split('/upload/')[0]
    except (ValueError, IndexError, AttributeError):
        return {'full': base_url}  # Return original if parsing fails
    
    # Build URLs with transformations
    return {
        # Full resolution for modal view - Centered on face with appropriate padding
        'full': f"{cloudinary_base}/upload/c_fill,w_1300,h_800,g_face,q_auto:eco,f_auto/{cloudinary_id}",

        'featured': f"{cloudinary_base}/upload/c_fill,w_1300,h_800,g_face,q_auto:eco,f_auto/{cloudinary_id}",
        
        'grid': f"{cloudinary_base}/upload/c_fill,w_400,g_auto:face,q_auto:best,dpr_2.0,f_auto/{cloudinary_id}",
        
        'large': f"{cloudinary_base}/upload/c_fill,w_400,h_600,g_auto:face,q_auto:good,f_auto,dpr_2.0/{cloudinary_id}",
    }

class PhotographerSerializer(serializers.ModelSerializer):
    website_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Photographer
        fields = ['id', 'name', 'instagram', 'website', 'website_display']
    
    def get_website_display(self, obj):
        """Return a clean version of the website URL without protocol and trailing slash"""
        if not obj.website:
            return None
            
        # Remove protocol (http://, https://)
        clean_url = obj.website.replace('http://', '').replace('https://', '')
        
        # Remove trailing slash if present
        if clean_url.endswith('/'):
            clean_url = clean_url[:-1]
            
        return clean_url
    
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
    shoot_year = serializers.SerializerMethodField()
    photo_count = serializers.SerializerMethodField()
    shoot_location = serializers.CharField(source='photo_shoot.location')
    shoot_order = serializers.IntegerField(source='photo_shoot.order')
    
    class Meta:
        model = Photo
        fields = [
            'id', 'image', 'title', 'description', 
            'photographer', 'is_portrait', 'photo_shoot_order',
            'carousel_order', 'show', 'optimized_images',
            'shoot_id', 'shoot_title', 'shoot_date', 'shoot_year', 'shoot_location', 'shoot_order', 'photo_count'
        ]
    
    def get_shoot_year(self, obj):
        """Extract only the year from the photo shoot date"""
        if obj.photo_shoot and obj.photo_shoot.date:
            return obj.photo_shoot.date.year
        return None
    
    def get_optimized_images(self, obj):
        """Get optimized Cloudinary images with dynamic sizing based on orientation"""
        # Get the base URLs from the helper function
        urls = get_cloudinary_urls(obj.image)
        
        if not urls:
            return None
            
        # Modify the grid URL if it's a landscape photo
        if hasattr(obj, 'is_portrait') and not obj.is_portrait and 'grid' in urls:
            grid_url = urls['grid']
            urls['grid'] = grid_url.replace('w_400', 'w_800')
        
        return urls
        
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
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Check if first_photo_only parameter is set
        if request and request.query_params.get('first_photo_only') == 'true':
            if data.get('photos') and len(data['photos']) > 0:
                # Sort photos by photo_shoot_order if needed
                photos = sorted(data['photos'], key=lambda p: p.get('photo_shoot_order', 0) if p.get('photo_shoot_order') is not None else float('inf'))
                # Only keep the first photo for each photoshoot
                data['photos'] = [photos[0]] if photos else []
        
        return data