# users/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms


User = get_user_model()


class TaskUserFormTests(TestCase):
    """
    Тестрируем выводимые данные форм регистрации
    """
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.quest_client = Client()

    def test_correct_form_context_on_signup_page(self):
        """
        Проверяем, что на страницу reverse('users:signup')
        в контексте передаётся форма для создания нового пользователя.
        """
        response = self.quest_client.get(
            reverse('users:signup')
        )
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }
        for field_value, contains_field in form_fields.items():
            with self.subTest(field_value=field_value):
                field = response.context.get('form').fields.get(field_value)
                self.assertIsInstance(field, contains_field)
