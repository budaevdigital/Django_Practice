from rest_framework import permissions


class AuthorPermission(permissions.BasePermission):
    message = 'Вы должны быть автором статьи'

    def has_object_permission(self, request, view, obj):
        # Если методы GET, HEAD или OPTIONS
        # то позволяем работать со списком или объёктом
        if request.method in permissions.SAFE_METHODS:
            return True
        # Если методы PUT, PATCH или DELETE
        # и пользователь является автором объекта
        return obj.author == request.user


class FollowPermission(permissions.BasePermission):
    message = 'Вы не можете подписаться, если вы не текущий пользователь'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
