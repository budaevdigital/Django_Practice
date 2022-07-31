from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from posts.models import (Post, Group,
                          Tag, TagPost,
                          Comment, User, Follow)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class PostSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(
        queryset=Group.objects.all(),
        slug_field='slug',
        required=False,
    )
    author = serializers.ReadOnlyField(source='author.username')

    # переопределяем поле Tags
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ('id', 'author', 'group', 'text', 'tags', 'pub_date', 'image')

    def create(self, validated_data):
        # Если в исходном запросе не было поля tags
        if 'tags' not in self.initial_data:
            # То создаём запись о post без tags
            post = Post.objects.create(**validated_data)
            return post
        # Иначе делаем следующее:
        # Уберём список tags из словаря validated_data и сохраним его
        tags = validated_data.pop('tags')
        # Сначала добавляем post в БД
        post = Post.objects.create(**validated_data)
        # А потом добавляем tags в БД
        for tag in tags:
            current_tag, status = Tag.objects.get_or_create(**tag)
            # И связываем каждый tag с этим post
            TagPost.objects.create(tag=current_tag, post=post)
        return post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    post = serializers.ReadOnlyField(source='post.id')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'post', 'author', 'created')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Group


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()

    )

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]

    def validate_author(self, value):
        # сравним поле пользователя с автором
        # ограничим возможность подписки на самого себя
        user = self.context.get('request').user
        for count in user.follower.all():
            if value == count.author:
                raise serializers.ValidationError(
                    'Вы уже подписанны на этого автора')
        # follower = user.following
        if user == value:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')

        return value
