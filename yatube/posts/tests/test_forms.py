# posts/tests/test_forms.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()


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

    def test_create_post(self):
        """
        Проверяем создание поста и отображение его в БД
        """
        sample_text = ('Модуль shutil - библиотека Python с удобными '
                       'инструментами для управления файлами и директориями: '
                       'создание, удаление, копирование, перемещение, '
                       'изменение папок и файлов')
        posts_count = Post.objects.count()
        form_data = {
            'text': str(sample_text),
            # поле group имеет взаимосвязь с базой Group и
            # cсылается через PrimaryKey(pk)
            'group': self.group_for_test.pk
        }
        # Отправляем POST-запрос от авторизованного пользователя
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:posts_author', kwargs={
            'username': self.auth_user.username
        }))
        # Проверяем, увеличилось ли число постов в БД
        self.assertEqual(Post.objects.count(), posts_count+1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                group=self.group_for_test.pk,
                text=sample_text,
                author=self.auth_user
            ).exists()
        )

    def test_edit_post(self):
        """
        Проверяем редактирование поста и отображение его в БД
        """
        # получаем данные из поля формы "текст" и сохраняем их
        response_get = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}))
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
        form_data = {
            'text': str(new_sample_text),
            # поле group имеет взаимосвязь с базой Group и
            # cсылается через PrimaryKey(pk)
            'group': self.new_group_for_test.pk
        }
        # Редактируем нужный пост
        self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True)
        # получаем новые данные из поля формы "текст" (они должны измениться)
        new_response_get = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}))
        new_text = new_response_get.context['form']
        self.assertNotEqual(old_text, new_text)
        # Проверяем, увеличилось ли число постов в БД
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                group=self.new_group_for_test.pk,
                text=new_sample_text,
                author=self.auth_user
            ).exists()
        )
