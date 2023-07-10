from rest_framework import mixins
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import Movie, Rating, BoardComment
from api.permissions import CustomPermission
# from api.permissions import CustomPermission
from api.serializers import MovieSerializer, RatingSerializer, UserSerializer, PaginationSet, BoardCommentSerializer, \
    MovieListSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    # permission_classes = (IsAuthenticated, )


class BoardCommentSet(viewsets.ModelViewSet):
    queryset = BoardComment.objects.all()
    serializer_class = BoardCommentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.order_by("-pub_date").all()
    serializer_class = MovieSerializer
    pagination_class = PaginationSet

    # Token auth settings
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (AllowAny, )
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # We can make a custom login like below
    # http://localhost:8000/api/movies/1/rate_movie/
    # detail True means "we are going to use this after detail url")
    @action(detail=True, methods=['POST'])
    def rate_movie(self, request, pk=None):
        if 'stars' in request.data:
            movie = Movie.objects.get(id=pk)
            stars = request.data['stars']

            # If we use token auth, ViewSet finds the user based on
            # token listed in the request header
            user = request.user

            # User test
            # user = User.objects.get(id=1)
            # print('user', user)

            try:
                rating = Rating.objects.get(user=user.id, movie=movie.id)
                # Code should be changed (the star number should be 0-5)
                rating.stars = stars
                rating.save()

                serializer = RatingSerializer(rating, many=False)
                response = {'message': 'Rating updated', 'result': serializer.data}
                return Response(response, status=status.HTTP_200_OK)
            except:
                rating = Rating.objects.create(user=user, movie=movie, stars=stars)
                serializer = RatingSerializer(rating, many=False)
                response = {'message': 'Rating created', 'result': serializer.data}
                return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'message': 'You need to provide stars'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)




class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    authentication_classes = (TokenAuthentication,)

    # permission_classes = (IsAuthenticated, )
    # permission_classes = (CustomPermission, )

    # Owner data filtering
    def list(self, request, *args, **kwargs):
        queryset = Rating.objects.filter(user=request.user.id)
        serializer = RatingSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user = request.user

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

    def create(self, request, *args, **kwargs):
        response = {'message': 'You can create'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class MovieListViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    pagination_class = PaginationSet

    queryset = Movie.objects.order_by('-pub_date').all()
    serializer_class = MovieListSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        if 'search' in request.query_params:
            search = request.query_params['search']
            queryset = Movie.objects.order_by("-pub_date").filter(title__contains=search)

            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)

            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            queryset = self.get_queryset()

            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)

            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)

    # def create(self, request):
    #     if 'search' in request.data:
    #         search = request.data['search']
    #         queryset = Movie.objects.order_by("-pub_date").filter(title__contains=search)
    #
    #         page = self.paginate_queryset(queryset)
    #         serializer = self.get_serializer(page, many=True)
    #
    #         result = self.get_paginated_response(serializer.data)
    #         return Response(result.data, status=status.HTTP_200_OK)

