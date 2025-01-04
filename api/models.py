from django.db import models
from django.contrib.auth.models import User


class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relasi ke tabel user
    id_movie = models.CharField(max_length=50)  
    rating = models.FloatField()
    genre = models.CharField(max_length=100, default="Unknown") 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.user.username} - Movie ID: {self.id_movie} - Rating: {self.rating}"
