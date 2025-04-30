from django.db import models

# Create your models here.
profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
