from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=25)
    description = models.TextField(max_length=500)

    # для нормального отображения в списке
    # без этого метода, будет "Group object"
    # выведем просто название группы
    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='group',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу'
    )

    # для нормального отображения в списке
    # без этого метода, будет "Post object"
    # выведем 15 символов текста
    def __str__(self):
        return self.text[:15]
