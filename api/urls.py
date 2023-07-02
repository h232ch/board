
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from api.views import MovieViewSet, RatingViewSet, UserViewSet, BoardCommentSet, MovieListViewSet

router = routers.DefaultRouter()
router.register('movies', MovieViewSet)
router.register('movielist', MovieListViewSet)
router.register('ratings', RatingViewSet)
router.register('users', UserViewSet)
router.register('comments', BoardCommentSet)

urlpatterns = [
    path('', include(router.urls)),
]
