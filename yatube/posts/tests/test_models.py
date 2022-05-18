from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """
    Класс для тестирования моделей БД
    """
    @classmethod
    def setUpClass(cls):
        """
        Создаем юзера для последующих тестов
        """
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        # verbose_name заполняем в соответствии с моделью в БД
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый URL',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое содержание поста',
        )

    def test_models_have_correct_name_group(self):
        """
        Проверяем правильность работы __str__ у модели group
        __str__  group_task - это строчка с содержимым group_task.title.
        """
        group_task = PostModelTest.group
        excepted_object_name = group_task.title
        self.assertEqual(excepted_object_name,
                         str(group_task),
                         f'Ошибка в {excepted_object_name=}. '
                         f'Метод выводит не то, что нужно')

    def test_models_have_correct_name_post(self):
        """
        Проверяем правильность работы __str__ у модели group
        __str__  post_task - это строчка с содержимым post_task.text[:15].
        ограничение длины строки - 15 символов. Как в модели
        """
        post_task = PostModelTest.post
        excepted_object_name = post_task.text[:15]
        self.assertEqual(excepted_object_name,
                         str(post_task),
                         f'Ошибка в {excepted_object_name=}. '
                         f'Метод выводит не то, что нужно')

    def test_verbose_name(self):
        """
        verbose_name в полях совпадает с ожидаемым.
        """
        post_verboses_name = PostModelTest.post
        # При изменении полей в модели БД, не забыть поменять и здесь
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        # пишем цикл для тестирования verbose_name с subTest
        for field, expected_value in field_verboses.items():
            # в subTest не забываем указать привязку к полю, иначе не поймем
            # к чему было вызвано исключение
            with self.subTest(field=field):
                self.assertEqual(
                    post_verboses_name._meta.get_field(field).verbose_name,
                    expected_value,
                    'verbose_name оказался не тот, который ожидали')

    def test_help_text(self):
        """
        help_text в полях совпадает с ожидаемым.
        """
        post_help_text = PostModelTest.post
        # При изменении полей в модели БД, не забыть поменять и здесь
        field_help = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        # пишем цикл для тестирования help_text с subTest
        for field, expected_value in field_help.items():
            # в subTest не забываем указать привязку к полю, иначе не поймем
            # к чему было вызвано исключение
            with self.subTest(field=field):
                self.assertEqual(
                    post_help_text._meta.get_field(field).help_text,
                    expected_value,
                    'help_text оказался не тот, который ожидали')
