from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from api.models import User


class CustomPermission(permissions.BasePermission):
    # def has_permission(self, request, view):
    #     # print(request.user)
    #     return True
    #
    # # object level permission control
    # def has_object_permission(self, request, view, obj):
    #     print(obj.user)
    #     print(request.user)
    #     return True

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
