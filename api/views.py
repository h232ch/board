from django.contrib.auth import get_user_model
from rest_framework import mixins
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import  AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.models import Movie, Rating, BoardComment, Rule, Dog
from api.permissions import IsOwnerOrReadOnly
from api.serializers import MovieSerializer, RatingSerializer, UserSerializer, PaginationSet, BoardCommentSerializer, \
    MovieListSerializer, DogSerializer, RuleSerializer

import ipaddress
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response




# Jwt view setting
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def example_view(request):
    return Response({"message": "You are authenticated!"})


class SecretView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({"message": "You have accessed the secret view!"})


class UserCheckView(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        if request.user:
            user = request.user
            # Your view logic...
            return Response({'user': user.username}, status.HTTP_200_OK)
        else:
            return Response({'message': 'You are not login'}, status.HTTP_403_FORBIDDEN)


# class UserViewSet(viewsets.ModelViewSet):
class UserViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class BoardCommentSet(viewsets.ModelViewSet):
    queryset = BoardComment.objects.all()
    serializer_class = BoardCommentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly | IsAdminUser)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.order_by("-pub_date").all()
    serializer_class = MovieSerializer
    pagination_class = PaginationSet

    # Token auth settings
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly | IsAdminUser )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'])
    def rate_movie(self, request, pk=None):
        if 'stars' in request.data:
            movie = Movie.objects.get(id=pk)
            stars = request.data['stars']
            user = request.user

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
    authentication_classes = (JWTAuthentication,)

    # Owner data filtering
    def list(self, request, *args, **kwargs):
        queryset = Rating.objects.filter(user=request.user.id)
        serializer = RatingSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        # print(request.user)
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


class DogViewSet(viewsets.ModelViewSet):
    queryset = Dog.objects.all()
    serializer_class = DogSerializer
    permission_classes = (AllowAny,)
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
        elif network1.num_addresses > network2.num_addresses:
            return False
        elif network1.overlaps(network2):
            return True
        else:
            return False

    except ipaddress.AddressValueError as e:
        # print(f"Invalid network address: {e}")
        return Response({'result': {'error': 'Check the searching ip or port format.'}},
                        status.HTTP_500_INTERNAL_SERVER_ERROR)


class RuleViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    pagination_class = PaginationSet

    def list(self, request, *args, **kwargs):
        if ('src' in request.query_params) or ('dst' in request.query_params) \
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
            serializer = RuleSerializer(queryset, many=True)
            return Response({'result': serializer.data}, status.HTTP_200_OK)

        else:
            queryset = self.get_queryset()
            serializer = RuleSerializer(queryset, many=True)
            return Response({'result': serializer.data}, status.HTTP_200_OK)


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # Call the parent's post method to authenticate the user and get the token
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = response.data.get('token')

        # Retrieve the user associated with the token
        user = Token.objects.get(key=token).user
        # Add the username to the response data
        response.data['username'] = user.username

        return response
