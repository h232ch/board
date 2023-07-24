from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit and delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the article.
        return obj.user == request.user


class IsAdminOrIsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to allow admin users to have full privileges (GET, POST, PUT, DELETE),
    while allowing non-admin users to read their own data (GET) and update or delete their own records.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Allow read access to all requests.
        if request.method in SAFE_METHODS:
            return True

        # Allow write (update, delete) access only if the user is the owner of the object.
        return obj.user == request.user

