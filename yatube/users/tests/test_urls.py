# users/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

STATUS_200 = HTTPStatus.OK  # Переход на страницу
STATUS_404 = HTTPStatus.NOT_FOUND   # страница не найдена
STATUS_302 = HTTPStatus.FOUND   # Редирект

User = get_user_model()


class TaskURLTestsUsers(TestCase):
    """
    Тестируем страницы сайта (регистрации, входа и т.д.)
    на доступность с разным уровнем доступа пользователей
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.credentials = {
            'username': 'auth_user',
            'email': 'dmitry@budaev.digital',
            'password': 'secrets'
        }
        # cls.auth_user = User.objects.create_user(**cls.credentials)
        cls.auth_user = User.objects.create_user(**cls.credentials)

        # неавторизованный. Для проверки доступа там, где требуется авторизация
        cls.quest_client = Client()
        # второй-авторизованный автор стать. Для проверки редактирования поста
        cls.authorized_client = Client()

        # Авторизовываем клиентов auth_user
        cls.authorized_client.force_login(cls.auth_user)

    def test_auth_urls_for_auth_client(self):
        """Тестируем URL на выбранные шаблоны"""
        templates_url_auth = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change_form'): (
                'users/password_change_form.html'),
            reverse('users:password_change_done'): (
                'users/password_change_done.html'),
            reverse('users:password_reset_form'): (
                'users/password_reset_form.html'),
            reverse('users:password_reset_done'): (
                'users/password_reset_done.html')
        }
        for url, template in templates_url_auth.items():
            with self.subTest(url=url):
                # тестируем все страницы, поэтому указываем а
                # вторизованного пользователя
                response = self.authorized_client.get(url)
                print(f'{response} | {template} | {url}')
                self.assertTemplateUsed(response, template)

    def test_status_auth_urls_for_quest_client(self):
        """
        Тестируем страницы на доступность для авторизованного пользователя
        """
        # Шаблоны по адресам
        status_url_auth = {
            reverse('users:signup'): STATUS_200,
            reverse('users:login'): STATUS_200,
            reverse('users:password_reset_form'): STATUS_200,
            reverse('users:password_reset_done'): STATUS_200,
            reverse('users:password_change_form'): STATUS_200,
            reverse('users:password_change_done'): STATUS_200,
        }

        for url, status in status_url_auth.items():
            with self.subTest(url=url):
                # тестируем все страницы, поэтому указываем а
                # вторизованного пользователя
                response = self.authorized_client.get(url)
                print(f'{response} | {status} | {url}')
                self.assertEqual(response.status_code, status)

    def test_redirect_anonymous_to_login_page(self):
        """
        Тестируем редирект анонимного пользователя на страницу логина
        """
        login_url = '/auth/login/'
        redirect_back = '?next='
        url_for_redirect = {
            reverse('users:password_change_form'): STATUS_302,
            reverse('users:password_change_done'): STATUS_302,
        }
        for url, status in url_for_redirect.items():
            with self.subTest(url=url):
                # проверка с неавторизованным пользователем
                response = self.quest_client.get(url)
                self.assertRedirects(response,
                                     f'{login_url}{redirect_back}{url}')
                self.assertEqual(response.status_code, status)

    def test_redirect_auth_user_to_index_page(self):
        """
        Тестируем редирект авторизованного пользователя
        со страницы логина на главную
        """
        redirect = reverse('posts:index')
        url_for_redirect = {
            reverse('users:logged_out'): STATUS_302,
        }
        for url, status in url_for_redirect.items():
            with self.subTest(url=url):
                # проверка с неавторизованным пользователем
                response = self.quest_client.get(url)
                self.assertRedirects(response,
                                     f'{redirect}')
                self.assertEqual(response.status_code, status)

    # TODO - доделать тесты

    # def test_redirect_anonymous_to_login_page(self):
    #     """
    #     Тестируем редирект анонимного пользователя на страницу логина
    #     """
    #     login_url = '/auth/login/'
    #     redirect_back = '?next='
    #     url_for_redirect = {
    #         reverse('users:logged_out'): STATUS_302,
    #     }
    #     for url, status in url_for_redirect.items():
    #         with self.subTest(url=url):
    #             # проверка с неавторизованным пользователем
    #             response = self.quest_client.get(url)
    #             self.assertRedirects(response,
    #                                  f'{login_url}{redirect_back}{url}')
    #             self.assertEqual(response.status_code, status)
