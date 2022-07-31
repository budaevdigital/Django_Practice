# about/test_urls.py
from django.test import Client, TestCase
from http import HTTPStatus
from django.urls import reverse

STATUS_200 = HTTPStatus.OK  # Переход на страницу


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

    def test_about_pages_on_correct_template(self):
        """
        Тестируем страницы "/about/author/" и "/about/tech/"
        на правильный шаблон страницы
        """
        # Шаблоны по адресам
        templates_url_names = {
            # об авторе / доступ-всем
            reverse('about:author'): 'about/about_author.html',
            # итспользуемые инструменты / доступ-всем
            reverse('about:tech'): 'about/about_tech.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.unauth_client.get(url)
                self.assertTemplateUsed(response, template,
                                        f'{response=} шаблон старницы {url} '
                                        f'- не верный!')

    def test_about_pages_on_response_status(self):
        """
        Тестируем страницы "/about/author/" и "/about/tech/"
        на код ответа
        """
        url_status = {
            # об авторе / доступ-всем
            reverse('about:author'): STATUS_200,
            # итспользуемые инструменты / доступ-всем
            reverse('about:tech'): STATUS_200
        }
        # делаем запрос к странице и проверяем статус ответа
        # тестрируем код ответа - тест будет завален, если код != 200
        for url, status in url_status.items():
            with self.subTest(url=url):
                response = self.unauth_client.get(url)
                self.assertEqual(response.status_code, status,
                                 f'{response.status_code=} код ответа сервера.'
                                 f' Страница {url} недоступна!')
