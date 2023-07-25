from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from api.models import Movie, Rating, BoardComment, Rule, Dog


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


class BoardCommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = BoardComment
        fields = ('id', 'user', 'movie', 'comment', 'pub_date')


class MovieSerializer(serializers.ModelSerializer):
    # Fixing user
    user = serializers.ReadOnlyField(source='user.username')
    comments = BoardCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ('id', 'title', 'pub_date', 'description',
                  'no_of_ratings', 'avg_ratings', 'user', 'comments')


class MovieListSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Movie
        fields = ('id', 'title', 'pub_date', 'user')


class PaginationSet (PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class DogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dog
        fields = '__all__'


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ('id', 'data',)


class JwtUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()

