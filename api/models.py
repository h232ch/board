from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=360)
    pub_date = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    # Custom data which can be used in serializer's fields
    def no_of_ratings(self):
        ratings = Rating.objects.filter(movie=self)
        return len(ratings)

    def avg_ratings(self):
        sum = 0
        ratings = Rating.objects.filter(movie=self)
        for rating in ratings:
            sum += rating.stars
        if len(ratings) > 0:
            return sum / len(ratings)
        else:
            return 0


class BoardComment(models.Model):
    movie = models.ForeignKey(Movie, related_name='comments', on_delete=models.CASCADE, null=True)
    comment = models.TextField(max_length=360)
    pub_date = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class Rating(models.Model):
    # If movie is deleted, Rating object will be deleted
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    # We use django default user model
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # We can use django core validator to check the stars (Min, max value)
    stars = models.IntegerField(validators=[MinValueValidator(1),
                                            MaxValueValidator(5)])

    # Setup unique, index together (should study this more)
    # unique together, two or more model fields to be unique, we can use this
    # index together, the fields will be indexed together
    class Meta:
        unique_together = (('user', 'movie'), )
        index_together = (('user', 'movie'), )

