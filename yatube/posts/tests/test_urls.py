# posts/tests/test_urls.py
from django.test import Client, TestCase


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
        super(StaticURLTests, cls).setUpClass()
        # создадим экземпляр неавториззованного пользователя
        cls.unauth_client = Client()

    def test_homepage(self):
        """
        Тестируем главную страницу сайта на код ответа
        """
        # делаем запрос к странице и проверяем статус ответа
        status_response = StaticURLTests.unauth_client.get('/')
        # тестрируем код ответа - тест будет завален, если код != 200
        self.assertEqual(status_response.status_code, 200,
            f'{status_response.status_code=} код ответа сервера. '
            f'Главная страница недоступна!')

    def test_about_authorpage(self):
        """
        Тестируем страницу "/about/author/" сайта на код ответа
        """
        # делаем запрос к странице и проверяем статус ответа
        status_response = StaticURLTests.unauth_client.get('/about/author/')
        # тестрируем код ответа - тест будет завален, если код != 200
        self.assertEqual(status_response.status_code, 200,
            f'{status_response.status_code=} код ответа сервера. '
            f'Страница "Обо мне" недоступна!')

    def test_about_techpage(self):
        """
        Тестируем страницу "/about/tech/" сайта на код ответа
        """
        # делаем запрос к странице и проверяем статус ответа
        status_response = StaticURLTests.unauth_client.get('/about/tech/')
        # тестрируем код ответа - тест будет завален, если код != 200
        self.assertEqual(status_response.status_code, 200,
            f'{status_response.status_code=} код ответа сервера. '
            f'Страница "Обо мне" недоступна!')
