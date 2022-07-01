from rest_framework import permissions


class AuthorPermission(permissions.BasePermission):
    message = 'Вы должны быть автором статьи'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class FollowPermission(permissions.BasePermission):
    message = 'Вы не можете подписаться, если вы не текущий пользователь'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user
