# posts/tests/test_forms.py
import shutil
import tempfile
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from posts.models import Post, Group
from posts.forms import PostForm


# Создаем временную папку для медиа-файлов
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)

User = get_user_model()


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCorrectCreateEditPost(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.auth_user = User.objects.create_user(
            username='test_user')
        cls.group_for_test = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post_with_slug = Post.objects.create(
            text=('Подумайте перед составлением'
                  ' словаря с шаблонами и адресамиии.'),
            author=cls.auth_user,
            group=cls.group_for_test
        )
        cls.post_without_slug = Post.objects.create(
            text=('Подумайте перед составлением'
                  ' словаря с шаблонами и адресамиии.'),
            author=cls.auth_user
        )
        cls.form = PostForm()
        # незарегистрированный пользователь
        cls.quest_client = Client()
        # Пользователь, который есть в БД и который авторизовался
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.auth_user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """
        Проверяем создание поста и отображение его в БД
        """
        sample_text = ('Модуль shutil - библиотека Python с удобными '
                       'инструментами для управления файлами и директориями: '
                       'создание, удаление, копирование, перемещение, '
                       'изменение папок и файлов')
        posts_count = Post.objects.count()

        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': str(sample_text),
            # поле group имеет взаимосвязь с базой Group и
            # cсылается через PrimaryKey(pk)
            'group': self.group_for_test.pk,
            'image': uploaded,
        }
        # Отправляем POST-запрос от авторизованного пользователя
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.auth_user.username
        }))
        # Проверяем, увеличилось ли число постов в БД
        self.assertEqual(Post.objects.count(), posts_count+1)
        # Проверяем, что создалась запись с заданным слагом и gif
        self.assertTrue(
            Post.objects.filter(
                group=self.group_for_test.pk,
                text=sample_text,
                author=self.auth_user,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """
        Проверяем редактирование поста и отображение его в БД
        """
        # получаем данные из поля формы "текст" и сохраняем их
        response_get = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 2}))
        old_text = response_get.context['form']
        posts_count = Post.objects.count()
        new_sample_text = ('При тестировании модуль SimpleUploadFile не '
                           'эмулирует сохранение картинок, а на самом деле '
                           'сохраняет их в директорию media/tasks. В '
                           'результате после каждого теста в этой директории '
                           'будет добавляться по картинке. Лучше прибраться '
                           'за собой и не оставлять никакого мусора после.')

        self.new_group_for_test = Group.objects.create(
            title='Новый тестовый заголовок',
            description='Новый тестовый текст',
            slug='new-test-slug'
        )
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': str(new_sample_text),
            # поле group имеет взаимосвязь с базой Group и
            # cсылается через PrimaryKey(pk)
            'group': self.new_group_for_test.pk,
            'image': uploaded,
        }
        # Редактируем нужный пост
        self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 2}),
            data=form_data,
            follow=True
        )
        # получаем новые данные из поля формы "текст" (они должны измениться)
        new_response_get = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 2}))
        new_text = new_response_get.context['form']
        self.assertNotEqual(old_text, new_text)
        # Проверяем, увеличилось ли число постов в БД
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что создалась запись с заданным слагом и gif
        self.assertTrue(
            Post.objects.filter(
                group=self.new_group_for_test.pk,
                text=new_sample_text,
                author=self.auth_user,
                image='posts/small2.gif'
            ).exists()
        )

    def test_correct_form_for_create_post(self):
        """
        Тестрируем выводимые поля в форме при создании поста
        """
        response = self.auth_client.get(
            reverse('posts:post_create'))
        forms_field = {
            'group': forms.fields.ChoiceField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField
        }
        for value, excepted in forms_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, excepted)

    def test_correct_form_for_edit_post(self):
        """
        Тестрируем выводимые поля в форме при редактировании поста
        """
        # присваиваем ID для post_id, чтобы автором поста был auth_user
        post_id = 1
        response = self.auth_client.get(
            reverse('posts:post_edit', kwargs={
                'post_id': post_id}))
        forms_field = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField
        }
        for value, excepted in forms_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, excepted)
