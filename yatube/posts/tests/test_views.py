# posts/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
import random
from posts.models import Post, Group

# Общее количество постов
POSTS_FOR_RANDOM = 27
# количество постов на странице
COUNT_PAGINATOR_ON_PAGE = 9

# FIRST и SECOND не менять!
COUNT_FIRST_POST_TEST = 0
COUNT_SECOND_POST_TEST = 0

User = get_user_model()


class TaskObjectPagesTests(TestCase):
    """
    Тестируем выводимые объекты на страницах
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
        # 1 пост-без Group(slug-рубрики)
        cls.post_one = Post.objects.create(
            text=('Подумайте перед составлением '
                  'словаря с шаблонами и адресамиии.'),
            author=cls.auth_user
        )
        # 2 пост-с Group(slug-рубрикой)
        cls.post_two = Post.objects.create(
            text=('Подумайте после составлением'
                  ' словаря. Это здорово!'),
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

    def test_pages_show_correct_context(self):
        """
        Тестирование правильности отображаемого контента
        """
        response = self.authorized_client_auth_user.get(reverse('posts:index'))
        page_objects = response.context['page_obj'][0]
        # создадим словарь с ключами, которые в ответ на запрос к странице
        # в значениях ключа - правильное тестируемое значение
        test_page_objects = {
            page_objects.text: self.post_two.text,
            page_objects.group: self.post_two.group,
            page_objects.author: self.post_two.author,
            page_objects.pub_date: self.post_two.pub_date
        }
        # сравниваем со значениями 2-го поста, т.к. он создан последним в тесте
        # во view-функции у нас сортировка по убыванию по дате
        for page_obj, correct_data in test_page_objects.items():
            with self.subTest(page_obj=page_obj):
                self.assertEqual(page_obj, correct_data)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # создаем запись в БД пользователя
        cls.auth_user = User.objects.create_user(
            username='test_user')
        cls.auth_user_second = User.objects.create_user(
            username='test_user_second')
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
        # В цикле создаём нужное количество постов для тестов пагинации
        count_posts = POSTS_FOR_RANDOM
        global COUNT_FIRST_POST_TEST
        global COUNT_SECOND_POST_TEST
        while count_posts > 0:
            if count_posts % 2 == 0:
                name_post = 'post_' + str(count_posts)
                cls.name_post = Post.objects.create(
                    text=(name_post + ' ') * 2,
                    author=cls.auth_user,
                    group=cls.group_for_test)
                COUNT_FIRST_POST_TEST += 1
            else:
                name_post_second = 'post_' + str(count_posts)
                cls.name_post_second = Post.objects.create(
                    text=(name_post_second + ' ') * 2,
                    author=cls.auth_user_second,
                    group=cls.group_for_test_second)
                COUNT_SECOND_POST_TEST += 1
            count_posts -= 1

        # создаём 2 клиентов
        # первый-неавторизованный. Для проверки доступа там,
        # где требуется авторизация
        cls.quest_client = Client()
        # второй-просто авторизованный клиент
        cls.authorized_client_auth_user = Client()
        # Авторизовываем клиентов auth_user
        cls.authorized_client_auth_user.force_login(cls.auth_user)

    def test_first_page_contains_nine_records(self):
        """
        Тестирует (паджинатор) количество постов на странице с учетом пагинации
        """
        if POSTS_FOR_RANDOM < COUNT_PAGINATOR_ON_PAGE:
            posts_count = POSTS_FOR_RANDOM
        else:
            posts_count = COUNT_PAGINATOR_ON_PAGE
        response = self.authorized_client_auth_user.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 9.
        # Такое количество задано во view функции
        self.assertEqual(len(response.context['page_obj']),
                         posts_count)

    def test_last_page_contains_four_records(self):
        """
        Тестирует (паджинатор) количество постов на
        последней странице Всего постов 22
        """
        if POSTS_FOR_RANDOM > COUNT_PAGINATOR_ON_PAGE and (
                POSTS_FOR_RANDOM < COUNT_PAGINATOR_ON_PAGE*2):
            all_pages = 2
            posts_on_last_page = POSTS_FOR_RANDOM - (
                COUNT_PAGINATOR_ON_PAGE)
        elif POSTS_FOR_RANDOM <= COUNT_PAGINATOR_ON_PAGE:
            all_pages = 1
            posts_on_last_page = POSTS_FOR_RANDOM - (
                COUNT_PAGINATOR_ON_PAGE*0)
        else:
            all_pages = int(POSTS_FOR_RANDOM/COUNT_PAGINATOR_ON_PAGE)
            if (POSTS_FOR_RANDOM % COUNT_PAGINATOR_ON_PAGE) == 0:
                posts_on_last_page = COUNT_PAGINATOR_ON_PAGE
            else:
                posts_on_last_page = POSTS_FOR_RANDOM - (
                    COUNT_PAGINATOR_ON_PAGE*all_pages)

        # Проверка: на третьей странице должно быть 4 поста.
        response = self.authorized_client_auth_user.get(
            reverse('posts:index') + f'?page={all_pages + 1}')
        self.assertEqual(len(response.context['page_obj']), posts_on_last_page)

    def test_correct_form_for_create_post(self):
        """
        Тестрируем выводимые поля в форме при создании поста
        """
        response = self.authorized_client_auth_user.get(
            reverse('posts:post_create'))
        forms_field = {
            'group': forms.fields.ChoiceField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField
        }
        for value, excepted in forms_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, excepted)

    def test_correct_form_for_edit_post(self):
        """
        Тестрируем выводимые поля в форме при редактировании поста
        """
        # В зависимости от значения (POSTS_FOR_RANDOM) четн. / нечетн.
        # присваиваем ID для post_id, чтобы автором поста был auth_user
        if POSTS_FOR_RANDOM % 2 == 0:
            post_id = 3
        else:
            post_id = 4
        response = self.authorized_client_auth_user.get(
            reverse('posts:post_edit', kwargs={
                # Количество постов 22. Нужен четный ID (РК) поста
                # auth_user в цикле, явяляется автором именно четных
                # с помощью andom.randrange выбираем рандомно нечетное число
                'post_id': post_id}))
        forms_field = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }
        for value, excepted in forms_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, excepted)

    def test_posts_contains_filter_author(self):
        """
        Тестирует отфильтрованные посты на странице для определённого автора
        """
        # На странице 9 постов, с учетом того, что в response['page_obj']
        # отсчет будет с 0, то для рандома указываем на 1 единицу меньше
        if COUNT_SECOND_POST_TEST >= COUNT_PAGINATOR_ON_PAGE:
            count_posts_on_page_for_random = COUNT_PAGINATOR_ON_PAGE - 2
        else:
            count_posts_on_page_for_random = COUNT_PAGINATOR_ON_PAGE - 3
        response = self.authorized_client_auth_user.get(
            reverse('posts:posts_author', kwargs={
                'username': self.auth_user_second.username
            }))
        select_post_on_page = response.context['page_obj'][random.randint(
            1, count_posts_on_page_for_random)]
        # проверка случайно выбранного поста, что автором является
        # нужный автор
        self.assertEqual(select_post_on_page.author, self.auth_user_second)

    def test_first_page_contains_records_filter_author_post(self):
        """
        Тестирует (паджинатор) количество постов на странице с
        учетом пагинации и отфильтрованных по пользователю
        """
        if COUNT_SECOND_POST_TEST <= COUNT_PAGINATOR_ON_PAGE:
            count_post = COUNT_SECOND_POST_TEST
        else:
            count_post = COUNT_PAGINATOR_ON_PAGE
        response = self.authorized_client_auth_user.get(
            reverse('posts:posts_author', kwargs={
                'username': self.auth_user_second.username
            }))
        # Проверка: количество постов на первой странице равно 9.
        # Такое количество задано во view функции
        self.assertEqual(len(
            response.context['page_obj']), count_post)

    def test_last_page_contains_records_filter_author_post(self):
        """
        Тестирует (паджинатор) количество постов на последней странице
        с учетом пагинации и отфильтрованных по пользователю.
        На последней странице
        """
        if COUNT_SECOND_POST_TEST > COUNT_PAGINATOR_ON_PAGE and (
                COUNT_SECOND_POST_TEST < COUNT_PAGINATOR_ON_PAGE*2):
            all_pages = 2
            posts_on_last_page = COUNT_SECOND_POST_TEST - (
                COUNT_PAGINATOR_ON_PAGE)
        elif COUNT_SECOND_POST_TEST < COUNT_PAGINATOR_ON_PAGE:
            all_pages = 1
            posts_on_last_page = COUNT_SECOND_POST_TEST - (
                COUNT_PAGINATOR_ON_PAGE*0)
        else:
            all_pages = int(COUNT_SECOND_POST_TEST/COUNT_PAGINATOR_ON_PAGE)
            posts_on_last_page = COUNT_SECOND_POST_TEST - (
                COUNT_PAGINATOR_ON_PAGE*all_pages)
        if posts_on_last_page == 0:
            posts_on_last_page = 9
        response = self.authorized_client_auth_user.get(
            reverse('posts:posts_author', kwargs={
                'username': self.auth_user_second.username
            }) + f'?page={all_pages+1}')
        # Всего постов этого автора 11. На первой странице - 9 постов
        # ,а на второй - будет 2 поста
        self.assertEqual(len(
            response.context['page_obj']), posts_on_last_page)

    def test_posts_with_filter_group(self):
        """
        Тестирует пост на странице отфильтрованные по определенной
        рубрике (group/slug) - другой рубрики быть не должно!
        """
        # На странице 9 постов, с учетом того, что в response['page_obj']
        # отсчет будет с 0, то для рандома указываем на 1 единицу меньше
        if COUNT_SECOND_POST_TEST >= COUNT_PAGINATOR_ON_PAGE:
            count_posts_on_page_for_random = COUNT_PAGINATOR_ON_PAGE - 2
        else:
            count_posts_on_page_for_random = COUNT_PAGINATOR_ON_PAGE - 3
        response = self.authorized_client_auth_user.get(
            reverse('posts:group_list', kwargs={
                'slug': self.group_for_test_second.slug}))
        select_post_on_page = response.context['page_obj'][random.randint(
            1, count_posts_on_page_for_random)]
        # проверка группы у случайно выбранного поста
        # <Group: Тестовый заголовок Второй>
        self.assertEqual(select_post_on_page.group,
                         self.group_for_test_second)

    def test_first_page_contains_nine_records_filter_group_post(self):
        """
        Тестирует (паджинатор) на начальной странице выбронной группы (рубрики)
        """
        if COUNT_SECOND_POST_TEST < COUNT_PAGINATOR_ON_PAGE:
            count_posts_on_page = COUNT_SECOND_POST_TEST
        else:
            count_posts_on_page = COUNT_PAGINATOR_ON_PAGE
        # slug='test-slug-second'
        response = self.quest_client.get(
            reverse('posts:group_list', kwargs={
                'slug': self.group_for_test_second.slug}))
        self.assertEqual(len(response.context['page_obj']),
                         count_posts_on_page)

    def test_last_page_contains_records_filter_group_post(self):
        """
        Тестирует (паджинатор) на последней странице выбронной группы (рубрики)
        """
        if COUNT_SECOND_POST_TEST > COUNT_PAGINATOR_ON_PAGE and (
                COUNT_SECOND_POST_TEST < COUNT_PAGINATOR_ON_PAGE*2):
            all_pages = 2
            posts_on_last_page = COUNT_SECOND_POST_TEST - (
                COUNT_PAGINATOR_ON_PAGE)
        elif COUNT_SECOND_POST_TEST < COUNT_PAGINATOR_ON_PAGE:
            all_pages = 1
            posts_on_last_page = COUNT_SECOND_POST_TEST - (
                COUNT_PAGINATOR_ON_PAGE*0)
        else:
            all_pages = int(COUNT_SECOND_POST_TEST/COUNT_PAGINATOR_ON_PAGE)
            posts_on_last_page = COUNT_SECOND_POST_TEST - (
                COUNT_PAGINATOR_ON_PAGE*all_pages)
        if posts_on_last_page == 0:
            posts_on_last_page = 9
        # slug='test-slug-second'
        response = self.quest_client.get(
            reverse('posts:group_list', kwargs={
                'slug': self.group_for_test_second.slug}
                    ) + f'?page={all_pages+1}')
        self.assertEqual(len(response.context['page_obj']),
                         posts_on_last_page)

    def test_page_with_detai_post_context(self):
        """
        Тест данных, которые выводит страница при чтении конкретного поста
        """
        # Сортировка постов на странице выполнена по дате (от новых к старым)
        # а name_post в тесте выполнен в обратном порядке
        count_post = POSTS_FOR_RANDOM
        post_text = 1
        response = self.quest_client.get(
            reverse('posts:post_detail', kwargs={
                'slug': self.group_for_test_second.slug,
                'post_id': count_post}))
        name_post = 'post_' + str(post_text)
        text_post = (name_post + ' ') * 2
        detail_post = response.context['page_obj'][0]
        self.assertEqual(detail_post.text, text_post)
        self.assertEqual(detail_post.author, self.auth_user_second)
        self.assertEqual(detail_post.group, self.group_for_test_second)
