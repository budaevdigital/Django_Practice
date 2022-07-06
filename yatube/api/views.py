from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from .permissions import AuthorPermission
from .serializers import (PostSerializer,
                          CommentSerializer, GroupSerializer)
from posts.models import Post, Group


class PostViewSet(viewsets.ModelViewSet):
    """
    Позволяет просматривать посты всем НЕ-авторизованным пользователям.
    Авторизованным пользователям, доступны действия:
        - создавать;
        - редактировать (свои);
        - удалять (свои).
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        # Устанавливаем разрешение
        permissions.IsAuthenticatedOrReadOnly,
        AuthorPermission
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def perform_delete(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, AuthorPermission,)
    serializer_class = CommentSerializer

    # queryset во вьюсете не указываем
    # Нам тут нужны не все комментарии, а только связанные с id
    # Поэтому нужно переопределить метод get_queryset и применить фильтр
    def get_queryset(self):
        # Получаем id из эндпоинта
        id = self.kwargs.get('post_id')
        # И отбираем только нужные комментарии
        post = get_object_or_404(Post, id=id)
        new_queryset = post.comments.all()
        return new_queryset

    def perform_create(self, serializer):
        id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=id)
        serializer.save(author=self.request.user, post=post)

    def perform_update(self, serializer):
        id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=id)
        serializer.save(author=self.request.user, post=post)

    def perform_delete(self, serializer):
        id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=id)
        serializer.save(author=self.request.user, post=post)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
