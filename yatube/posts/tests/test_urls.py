# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus
from posts.models import Group, Post

STATUS_202 = HTTPStatus.OK  # Переход на страницу
STATUS_404 = HTTPStatus.NOT_FOUND   # страница не найдена
STATUS_302 = HTTPStatus.FOUND   # Редирект

User = get_user_model()


class StaticURLTests(TestCase):
    """
    Тестируем главную страницу сайта
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Фикстура класса, чтобы вызвать создание экземпляра класса
        перед запуском всех тестов.
        """
        # Без этой строчки - super(StaticURLTests, ...
        # AttributeError: type object 'StaticURLTests'
        # has no attribute 'cls_atomics'
        super().setUpClass()
        # создадим экземпляр неавториззованного пользователя
        cls.unauth_client = Client()

    def test_homepage(self):
        """
        Тестируем главную страницу сайта на код ответа
        """
        # делаем запрос к странице и проверяем статус ответа
        status_response = self.unauth_client.get('/')
        # тестрируем код ответа - тест будет завален, если код != 200
        self.assertEqual(status_response.status_code, 200,
                         f'{status_response.status_code=} код ответа сервера. '
                         f'Главная страница недоступна!')

    def test_about_authorpage(self):
        """
        Тестируем страницу "/about/author/" сайта на код ответа
        """
        # делаем запрос к странице и проверяем статус ответа
        status_response = self.unauth_client.get('/about/author/')
        # тестрируем код ответа - тест будет завален, если код != 200
        self.assertEqual(status_response.status_code, 200,
                         f'{status_response.status_code=} код ответа сервера. '
                         f'Страница "Обо мне" недоступна!')

    def test_about_techpage(self):
        """
        Тестируем страницу "/about/tech/" сайта на код ответа
        """
        # делаем запрос к странице и проверяем статус ответа
        status_response = self.unauth_client.get('/about/tech/')
        # тестрируем код ответа - тест будет завален, если код != 200
        self.assertEqual(status_response.status_code, 200,
                         f'{status_response.status_code=} код ответа сервера. '
                         f'Страница "Обо мне" недоступна!')


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
        """Тестируем URL-адрес на использование соответствующего шаблона"""
        # Шаблоны по адресам
        templates_url_names = {
            # обязательно соблюдаем слеш "/" как в urls.py
            # главная / доступ-всем
            '': 'posts/group_posts.html',
            # список постов в рубрике / доступ-всем
            f'/group/{self.group_for_test.slug}/': 'posts/group_posts.html',
            # список постов определённого автора / доступ-всем
            (f'/profile/{self.auth_user_author.username}'
             '/posts/'): 'posts/group_posts.html',
            # поиск постов / доступ-всем
            '/search/': 'posts/search_posts.html',
            # чтение поста без рубрики / доступ-всем
            f'/group/{self.post_one.pk}': 'posts/post_detail.html',
            # чтение поста с рубрикой / доступ-всем
            (f'/group/{self.group_for_test.slug}'
             f'/{self.post_two.pk}/'): 'posts/post_detail.html',
            # редактирование поста / доступ-авторизированному автору поста
            f'/group/{self.post_two.pk}/edit/': 'posts/create_post.html',
            # создание поста / доступ-авторизированному пользователю
            '/create/': 'posts/create_post.html',
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                # тестируем все страницы, поэтому указываем авторизованного
                # пользователя, автора тестируемого поста
                response = self.authorized_client_auth_user_author.get(url)
                print(f'{response} | {template} | {url}')
                self.assertTemplateUsed(response, template)

    def test_pages_exists_at_desired_location(self):
        """
        Тестируем страницы на доступность
        для неавторизованного пользователя
        """
        templates_url_names = {
            '': STATUS_202,
            # список постов в рубрике / доступ-всем
            f'/group/{self.group_for_test.slug}/': STATUS_202,
            # список постов определённого автора / доступ-всем
            f'/profile/{self.auth_user_author.username}/posts/': STATUS_202,
            # поиск постов / доступ-всем
            '/search/': STATUS_202,
            # чтение поста без рубрики / доступ-всем
            f'/group/{self.post_one.pk}': STATUS_202,
            # чтение поста с рубрикой / доступ-всем
            (f'/group/{self.group_for_test.slug}'
             f'/{self.post_two.pk}/'): STATUS_202,
        }

        for url, status in templates_url_names.items():
            with self.subTest(url=url):
                # проверка с неавторизованным пользователем
                response = self.quest_client.get(url)
                print(f'{response} | {status} | {url}')
                self.assertEqual(response.status_code, status)

    def test_test_redirect_from_edit_page_no_author(self):
        """
        Тестируем доступ к странице редактирования поста.
        Проверяем редирект и статус ответа на странице
        редиректа
        """
        redirect_url = f'/group/{self.post_two.pk}'
        # запрос от авторизованного пользователя, но не автора поста
        response = self.authorized_client_auth_user.get(
            f'/group/{self.post_two.pk}/edit/')
        self.assertRedirects(response, redirect_url)
        self.assertEqual(response.status_code, STATUS_302)

    def test_status_edit_page_only_author(self):
        """
        Тестируем доступ к странице редактирования поста.
        Доступ должен быть только у автора
        """
        # запрос от авторизованного автора поста
        status_response = self.authorized_client_auth_user_author.get(
            f'/group/{self.post_two.pk}/edit/')
        self.assertEqual(status_response.status_code, STATUS_202)

    def test_nonexistent_page(self):
        """
        Тестрируем страницу, которая должна вернуть 404
        """
        nonexistent_url = '/non_404_nonepages/'
        response = self.quest_client.get(nonexistent_url)
        self.assertEqual(response.status_code, STATUS_404)

    def test_redirect_anonymous_to_login_page(self):
        """
        Тестируем редирект анонимного пользователя на страницу логина
        """
        login_url = '/auth/login/'
        redirect_back = '?next='
        url_for_redirect = {
            f'/group/{self.post_two.pk}/edit/': STATUS_302,
            '/create/': STATUS_302
        }
        for url, status in url_for_redirect.items():
            with self.subTest(url=url):
                # проверка с неавторизованным пользователем
                response = self.quest_client.get(url)
                self.assertRedirects(response,
                                     f'{login_url}{redirect_back}{url}')
                self.assertEqual(response.status_code, status)
