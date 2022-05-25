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
        auto_now_add=True,
        # оптимизация БД с помощью индексов
        db_index=True)
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
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Вставьте картинку размером до 5 Мб',
        # Аргумент upload_to указывает директорию,
        # в которую будут загружаться пользовательские файлы.
        upload_to='posts/',
        # Поле для картинки (необязательное)
        blank=True
    )

    class Meta:
        # переопределяем параметры фильтра и отображение имени
        # класса Post в ед. и мн. числе
        ordering = ('-pub_date'),
        verbose_name = 'Пост',
        verbose_name_plural = 'Посты'

    # для нормального отображения в списке
    # без этого метода, будет "Post object"
    # выведем 15 символов текста
    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    # настраиваем взаимоотношения и удаления, в случае удаления
    # объекта взаимосвязи
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментируемый пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField(max_length=500)
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария')

    def __str__(self):
        return self.text
