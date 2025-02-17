from django.db import models
class Photographer(models.Model):
    name = models.CharField(max_length=200)
    instagram = models.CharField(max_length=30, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return self.name
class Campaign(models.Model):
    class CampaignType(models.TextChoices):
        FILM = 'FILM', 'Film Only'
        PHOTO = 'PHOTO', 'Photo Only'
        BOTH = 'BOTH', 'Film and Photo'
    title = models.CharField(max_length=100)
    client = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type = models.CharField(
        max_length=5,
        choices=CampaignType.choices,
        default=CampaignType.FILM
    )
    video_url = models.URLField(null=True, blank=True)
    web_url = models.URLField(null=True, blank=True)
    date = models.DateField()
    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
class PhotoShoot(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    photographer = models.ForeignKey(
        Photographer, 
        on_delete=models.PROTECT,
        related_name='photo_shoots'
    )
    description = models.TextField(blank=True)
    location = models.CharField(blank=True, max_length=200)
    show = models.BooleanField(default=True)
    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='photo_shoots'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} - {self.date}"
class Photo(models.Model):
    image = models.ImageField(upload_to='photos/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    photographer = models.ForeignKey(
        Photographer, 
        on_delete=models.PROTECT,
        related_name='photos'
    )
    photo_shoot = models.ForeignKey(
        PhotoShoot, 
        on_delete=models.CASCADE,
        related_name='photos'
    )
    is_portrait = models.BooleanField(
        default=False,
        help_text="Check if photo is in portrait orientation"
    )
    photo_shoot_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )
    carousel_order = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Optional. Only set for photos that should appear in the homepage carousel"
    )
    show = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=['carousel_order']),
            models.Index(fields=['photo_shoot_order']),
        ]
        ordering = ['photo_shoot_order']

    def __str__(self):
        return self.title