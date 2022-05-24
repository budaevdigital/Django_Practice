# users/tests/test_forms.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


User = get_user_model()


class TaskCorrectCreateUser(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # незарегистрированный пользователь
        cls.quest_client = Client()

    def test_create_user(self):
        """
        Проверяем создание нового пользователя через форму регистрации
        """
        user_count = User.objects.count()
        form_data = {
            'first_name': 'ТестовоеИмя',
            'last_name': 'ТестовоеФамилия',
            'username': 'usert-for-test',
            'email': 'test@mail.ru',
            'password1': 'МойПарольТакойСложный123',
            'password2': 'МойПарольТакойСложный123',
        }
        response = self.quest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), user_count+1)
        self.assertTrue(
            User.objects.filter(
                first_name='ТестовоеИмя',
                last_name='ТестовоеФамилия',
                username='usert-for-test',
                email='test@mail.ru',
            )
        )
