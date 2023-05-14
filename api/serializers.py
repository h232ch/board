from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api.models import Movie, Rating


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'title', 'description',
                  'no_of_ratings', 'avg_ratings')


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('id', 'stars', 'user', 'movie')


# User serializer setting
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        # Password needs to be only writable and required
        # Below code make UserSerializer doesn't show the password anymore
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True
            }
        }

        # def create(self, validated_data):
        #     user = User.objects.create_user(**validated_data)
        #     # Token is related to User model so that we can use this like below
        #     # When user is created, Token will be created
        #     # You can check the relationship OneToOne in Token model
        #     token = Token.objects.create(user=user)
        #     return user

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

