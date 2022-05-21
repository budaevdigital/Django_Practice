# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus
from django.urls import reverse
from posts.models import Group, Post

STATUS_200 = HTTPStatus.OK  # Переход на страницу
STATUS_404 = HTTPStatus.NOT_FOUND   # страница не найдена
STATUS_302 = HTTPStatus.FOUND   # Редирект

User = get_user_model()


class TaskURLTests(TestCase):
    """
    Тестируем страницы сайта на доступность с разным уровнем
    доступа пользователей
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём две записи пользователей в БД
        # первый-автор статьи для проверки доступа
        # к странице редактирования своего поста
        cls.auth_user_author = User.objects.create_user(
            username='test_user_author')

        # второй-просто авторизованный пользователь
        cls.auth_user = User.objects.create_user(
            username='test_user')

        # создадим запись в модели Group в БД для проведения тестов
        cls.group_for_test = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )

        # создадим два поста в модели Post для проведения тестов
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
            author=cls.auth_user_author,
            group=cls.group_for_test
        )

        # создаём 3 клиентов
        # первый-неавторизованный. Для проверки доступа там,
        # где требуется авторизация
        cls.quest_client = Client()
        # второй-авторизованный автор стать. Для проверки редактирования поста
        cls.authorized_client_auth_user_author = Client()
        # третий-просто авторизованный клиент
        cls.authorized_client_auth_user = Client()

        # Авторизовываем клиентов auth_user_author и auth_user
        cls.authorized_client_auth_user.force_login(cls.auth_user)
        cls.authorized_client_auth_user_author.force_login(
            cls.auth_user_author)

    def test_urls_use_correct_template(self):
        """
        Тестируем URL-адрес на использование соответствующего ШАБЛОНА
        для АВТОРИЗОВАННОГО пользователя
        """
        # Шаблоны по адресам
        templates_url_names = {
            # главная / доступ-всем
            reverse('posts:index'): 'posts/group_posts.html',
            # список постов в рубрике / доступ-всем
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group_for_test.slug}
                ): 'posts/group_posts.html',
            # список постов определённого автора / доступ-всем
            reverse(
                'posts:posts_author',
                kwargs={'username': self.auth_user_author.username}
                ): 'posts/group_posts.html',
            # поиск постов / доступ-всем
            reverse('posts:search_posts'): 'posts/search_posts.html',
            # чтение поста без рубрики / доступ-всем
            reverse(
                'posts:post_detail_whithout_group',
                kwargs={'post_id': self.post_one.pk}
                ): 'posts/post_detail.html',
            # чтение поста с рубрикой / доступ-всем
            reverse(
                'posts:post_detail',
                kwargs={'slug': self.group_for_test.slug,
                        'post_id': self.post_two.pk}
                ): 'posts/post_detail.html',
            # редактирование поста / доступ-авторизированному автору поста
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post_two.pk}
                    ): 'posts/create_post.html',
            # создание поста / доступ-авторизированному пользователю
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                # тестируем все страницы, поэтому указываем авторизованного
                # пользователя, автора тестируемого поста (post_two)
                response = self.authorized_client_auth_user_author.get(url)
                self.assertTemplateUsed(response, template)

    def test_pages_exists_at_desired_location(self):
        """
        Тестируем страницы на доступность (СТАТУС)
        для НЕАВТОРИЗОВАННОГО пользователя
        """
        templates_url_names = {
            reverse('posts:index'): STATUS_200,
            # список постов в рубрике / доступ-всем
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group_for_test.slug}
                ): STATUS_200,
            # список постов определённого автора / доступ-всем
            reverse(
                'posts:posts_author',
                kwargs={'username': self.auth_user_author.username}
                ): STATUS_200,
            # поиск постов / доступ-всем
            reverse('posts:search_posts'): STATUS_200,
            # чтение поста без рубрики / доступ-всем
            reverse(
                'posts:post_detail_whithout_group',
                kwargs={'post_id': self.post_one.pk}
                ): STATUS_200,
            # чтение поста с рубрикой / доступ-всем
            reverse(
                'posts:post_detail',
                kwargs={'slug': self.group_for_test.slug,
                        'post_id': self.post_two.pk}
                ): STATUS_200,
        }

        for url, status in templates_url_names.items():
            with self.subTest(url=url):
                # проверка с неавторизованным пользователем
                response = self.quest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_test_redirect_from_edit_page_no_author(self):
        """
        Тестируем доступ к странице редактирования поста.
        Проверяем РЕДИРЕКТ и СТАТУС ответа на странице
        редиректа
        """
        redirect_url = reverse(
            'posts:post_detail_whithout_group', kwargs={
                'post_id': self.post_two.pk})
        edit_url = reverse('posts:post_edit',
                           kwargs={'post_id': self.post_two.pk})
        # запрос от авторизованного пользователя, но не автора поста
        # на страницу редактирования поста - ожидаем редирект
        response = (
            self.authorized_client_auth_user.get(edit_url))
        # ловим ошибку, если редирект произошёл на другую страницу
        self.assertRedirects(response, redirect_url)
        # получаем код ответа редиректа
        self.assertEqual(response.status_code, STATUS_302)

    def test_status_edit_page_only_author(self):
        """
        Тестируем ДОСТУП к странице редактирования поста.
        Доступ должен быть ТОЛЬКО У АВТОРА ПОСТА
        """
        # запрос от авторизованного автора поста
        # (authorized_client_auth_user_author)
        status_response = self.authorized_client_auth_user_author.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post_two.pk}))
        self.assertEqual(status_response.status_code, STATUS_200)

    def test_nonexistent_page(self):
        """
        Тестрируем страницу, которая должна вернуть СТАТУС 404
        """
        nonexistent_url = '/non_404_nonepages/'
        response = self.quest_client.get(nonexistent_url)
        self.assertEqual(response.status_code, STATUS_404)

    def test_redirect_anonymous_to_login_page(self):
        """
        Тестируем РЕДИРЕКТ анонимного пользователя на страницу ЛОГИНА
        там, где требуется авторизация пользователя
        """
        login_url = '/auth/login/'
        redirect_back = '?next='
        url_for_redirect = {
            reverse('posts:post_edit', kwargs={
                'post_id': self.post_two.pk}): STATUS_302,
            reverse('posts:post_create'): STATUS_302
        }
        for url, status in url_for_redirect.items():
            with self.subTest(url=url):
                # проверка с неавторизованным пользователем
                response = self.quest_client.get(url)
                self.assertRedirects(response,
                                     f'{login_url}{redirect_back}{url}')
                self.assertEqual(response.status_code, status)
