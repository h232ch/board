from rest_framework import mixins
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import Movie, Rating, BoardComment, Rule, Dog
from api.permissions import CustomPermission
# from api.permissions import CustomPermission
from api.serializers import MovieSerializer, RatingSerializer, UserSerializer, PaginationSet, BoardCommentSerializer, \
    MovieListSerializer, DogSerializer, RuleSerializer

import ipaddress


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


class DogViewSet(viewsets.ModelViewSet):
    queryset = Dog.objects.all()
    serializer_class = DogSerializer
    permission_classes = (AllowAny, )
    pagination_class = PaginationSet


def compare_ip_networks(network_str1, network_str2):

    if network_str1.find('/') == -1:
        network_str1 = network_str1 + '/32'
    if network_str2.find('/') == -1:
        network_str2 = network_str2 + '/32'

    try:
        network1 = ipaddress.ip_network(network_str1, strict=False)
        network2 = ipaddress.ip_network(network_str2, strict=False)

        # Compare the networks
        if network1 == network2:
            return True
        elif network1.overlaps(network2):
            return True
        else:
            return False

    except ipaddress.AddressValueError as e:
        print(f"Invalid network address: {e}")
        return "Invalid network address."


class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    permission_classes = (AllowAny, )
    pagination_class = PaginationSet

    def list(self, request, *args, **kwargs):
        if ('src' in request.query_params) or ('dst' in request.query_params)\
                or ('port' in request.query_params):

            searchSrc = request.query_params['src']
            searchDst = request.query_params['dst']
            searchPort = request.query_params['port']
            queryset = self.get_queryset()

            p_result = []
            d_result = []
            s_result = []

            for i in queryset:
                if searchPort != '':
                    for svc in i.data['service']:
                        for k, v in svc.items():
                            for k, v in v.items():
                                if k != 'description':
                                    if searchPort == v:
                                        p_result.append(i.id)

                source = i.data['source']
                destination = i.data['destination']
                for src in source:
                    if searchSrc != '':
                        if compare_ip_networks(searchSrc, src['ip']):
                            s_result.append(i.id)
                for dst in destination:
                    if searchDst != '':
                        if compare_ip_networks(searchDst, dst['ip']):
                            d_result.append(i.id)

            if searchSrc != '' and searchDst != '' and searchPort != '':
                result = list(set(p_result) & set(d_result) & set(s_result))
            elif searchSrc != '' and searchDst != '':
                result = list(set(d_result) & set(s_result))
            elif searchSrc != '' and searchPort != '':
                result = list(set(p_result) & set(s_result))
            elif searchDst != '' and searchPort != '':
                result = list(set(p_result) & set(d_result))
            else:
                result = list(set(p_result) | set(d_result) | set(s_result))

            queryset = Rule.objects.filter(id__in=result)
            # page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(many=True)

            serializer = RuleSerializer(queryset, many=True)
            return Response({'result': serializer.data}, status.HTTP_200_OK)

            # result = self.get_paginated_response(serializer.data)
            # return Response(result.data, status=status.HTTP_200_OK)

        else:
            queryset = self.get_queryset()
            # page = self.paginate_queryset(queryset)
            # serializer = self.get_serializer( many=True)

            # result = self.get_paginated_response(serializer.data)
            # return Response(result.data, status=status.HTTP_200_OK)

            serializer = RuleSerializer(queryset, many=True)
            return Response({'result': serializer.data}, status.HTTP_200_OK)
