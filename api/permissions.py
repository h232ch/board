from rest_framework import permissions
from .models import User


class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # print(request.user)
        return True

    # object level permission control
    def has_object_permission(self, request, view, obj):
        print(obj.user)
        print(request.user)
        return True

