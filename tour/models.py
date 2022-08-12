from unicodedata import name
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

LEVEL_CHECK = [
    ('difficulty', 'difficulty'),
    ('easy', 'easy'),
    ('medium', 'medium'),
]


# THE LOCATION MODEL THAT CONNECT WITH -> TOUR MODEL
class Location(models.Model):
    description = models.CharField(blank=True, null=True,max_length=100)
    address = models.CharField(blank=True, null=True,max_length=150)
    coordinates = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return self.address
    
    class Meta:
        verbose_name_plural = 'location'




# THE TOUR MODEL

class Tour(models.Model):
    ratingAvg = models.DecimalField(blank=True, null=True,max_digits=5,decimal_places=1)
    ratingQuantity = models.IntegerField(blank=True, null=True)
    startDates = models.JSONField(blank=True, null=True)
    name = models.CharField(blank=True, null=True,max_length=100)
    slug = models.SlugField(unique=True)
    duration = models.IntegerField(blank=True, null=True)
    maxGroupSize = models.IntegerField(blank=True, null=True)
    difficulty = models.CharField(max_length=10,choices=LEVEL_CHECK)
    price = models.IntegerField(blank=True, null=True)
    summary = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    coverImage = models.FileField(upload_to='cover_img/',blank=True, null=True)
    location = models.JSONField(blank=True, null=True)
    startLocation = models.ForeignKey(Location,on_delete=models.CASCADE)
 
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'tour'
 
 
 
 # THE Images MODEL THAT CONNECT WITH -> TOUR MODEL
 
class Images(models.Model):
    post = models.ForeignKey(Tour, default=None, on_delete=models.CASCADE)
    images = models.FileField(upload_to = 'tours_img/')
    
    class Meta:
        verbose_name_plural = 'images'




# POST REVIEW DATA class EmailField(max_length=254, **options)¶

class Review(models.Model):
    tour = models.SlugField(max_length=200,blank=True,null=True)
    user = models.EmailField(blank=True,null=True)
    review = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=5, blank=True, decimal_places=1, null=True)
    user_img = models.URLField(max_length=2000, blank=True,null=True)
    time_posted = models.TextField(blank=True, null=True)
    
    def __str__(self) -> str:
        return self.tour + '-' + self.user
    
    class Meta:
        unique_together = ('tour', 'user',)
    
class Tour_Guide(models.Model):
    name = models.CharField(blank=True, null=True,max_length=200)
    img = models.FileField(upload_to='tour_guide/',blank=True, null=True)
    creadAt = models.DateTimeField(auto_now=True)



class Booked_Tour(models.Model):
    user_email = models.CharField(blank=True, null=True,max_length=500)
    tour_slug = models.SlugField(blank=True, null=True)
    
    def __str__(self) -> str:
        return self.user_email + ' ------ ' + self.tour_slug
    
    class Meta:
        unique_together = ('user_email', 'tour_slug',)
     



# WORKING API KEY => SECRET
# client_id = 1045610393790-67euil14f1nc9acfdcn38i86lo9toegf.apps.googleusercontent.com
# 
# secret_key = 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






