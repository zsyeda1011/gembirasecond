from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
 id = models.AutoField(primary_key=True)
 name = models.CharField(max_length=255)
 price = models.IntegerField()
 description = models.TextField()
 image = models.ImageField(upload_to='movie_images/')

 amount_left = models.PositiveIntegerField(default=1, blank=True, null=True)


 def __str__(self):
    return str(self.id) + ' - ' + self.name
 
 def purchase(self):

        if self.amount_left is not None and self.amount_left > 0:
            self.amount_left -= 1
            self.save()
 
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class Petition(models.Model):
    id = models.AutoField(primary_key=True)
    movie_name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    yes_votes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.id} - {self.movie_name}"
    
class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(default = 1)

    class Meta:
        unique_together = ('movie', 'user')
        
    def __str__(self):
        return f"{self.movie.name} - {self.user.username}: {self.value}"