# posts/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group

User = get_user_model()


class TaskObjectPagesTests(TestCase):
    """
    """
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # создаем запись в БД пользователя
        cls.auth_user = User.objects.create_user(
            username='test_user')
        # создадим запись в модели Group в БД для проведения тестов
        cls.group_for_test = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.group_for_test_second = Group.objects.create(
            title='Тестовый заголовок Второй',
            description='Тестовый текст Второй',
            slug='test-slug-second'
        )
        # создадим пост в модели Post для проведения тестов
        # 1-без Group(slug-рубрики)
        cls.post_one = Post.objects.create(
            text=('Подумайте перед составлением '
                  'словаря с шаблонами и адресамиии.'),
            author=cls.auth_user
        )
        # 2-с Group(slug-рубрикой)
        cls.post_two = Post.objects.create(
            text=('Подумайте перед составлением'
                  ' словаря с шаблонами и адресамиии.'),
            author=cls.auth_user,
            group=cls.group_for_test
        )
        # создаём 2 клиентов
        # первый-неавторизованный. Для проверки доступа там,
        # где требуется авторизация
        cls.quest_client = Client()
        # второй-просто авторизованный клиент
        cls.authorized_client_auth_user = Client()
        # Авторизовываем клиентов auth_user
        cls.authorized_client_auth_user.force_login(cls.auth_user)

    def task_pages_show_correct_context(self):
        """
        Тестирование правильности отображаемого контента
        """
        response = self.authorized_client_auth_user.get(reverse('posts:index'))
        page_objects = response.context
        test_page_text = page_objects.text
        test_page_group = page_objects.group
        test_page_author = page_objects.author
        self.assertEqual(test_page_text, self.post_two.text)
        self.assertEqual(test_page_group, self.post_two.group)
        self.assertEqual(test_page_author, self.post_two.author)
        self.assertEqual(response.context.get('post').text, self.post_two.text)
        print(f'{response=}')

        # post_value_dict = {
        #     self.post_two.text: page_objects.text,
        #     self.post_two.group: page_objects.group,
        #     self.post_two.author: page_objects.author
        # }
        # for value, page_object in post_value_dict.items():
        #     with self.subTest(value=value):
        #         self.assertEqual(value, page_object)
