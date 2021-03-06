# posts/tests/test_views.py
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import random
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Post, Group, Comment

# Общее количество постов
POSTS_FOR_RANDOM = 27
# количество постов на странице
COUNT_PAGINATOR_ON_PAGE = 9

# FIRST и SECOND не менять!
COUNT_FIRST_POST_TEST = 0
COUNT_SECOND_POST_TEST = 0

# Создаем временную папку для медиа-файлов
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)

User = get_user_model()


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        # создадим пост в модели Post для проведения тестов
        # 1 пост-без Group(slug-рубрики)
        cls.post_one = Post.objects.create(
            text=('Подумайте перед составлением '
                  'словаря с шаблонами и адресамиии.'),
            author=cls.auth_user,
            image=uploaded
        )
        # 2 пост-с Group(slug-рубрикой)
        cls.post_two = Post.objects.create(
            text=('Подумайте после составлением'
                  ' словаря. Это здорово!'),
            author=cls.auth_user,
            group=cls.group_for_test,
            image=uploaded
        )

    def setUp(self):
        # создаём 2 клиентов
        # первый-неавторизованный. Для проверки доступа там,
        # где требуется авторизация
        self.quest_client = Client()
        # второй-просто авторизованный клиент
        self.authorized_client_auth_user = Client()
        # Авторизовываем клиентов auth_user
        self.authorized_client_auth_user.force_login(self.auth_user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)       

    def test_index_page_show_correct_context(self):
        """
        Тестирование правильности отображаемого контента на главной странице
        """
        response = self.authorized_client_auth_user.get(reverse('posts:index'))
        page_objects = response.context['page_obj'][0]
        # создадим словарь с ключами, которые в ответ на запрос к странице
        # в значениях ключа - правильное тестируемое значение
        test_page_objects = {
            page_objects.text: self.post_two.text,
            page_objects.group: self.post_two.group,
            page_objects.author: self.post_two.author,
            page_objects.pub_date: self.post_two.pub_date,
            page_objects.image: self.post_two.image
        }
        # сравниваем со значениями 2-го поста, т.к. он создан последним в тесте
        # во view-функции у нас сортировка по убыванию по дате
        for page_obj, correct_data in test_page_objects.items():
            with self.subTest(page_obj=page_obj):
                self.assertEqual(page_obj, correct_data)

    def test_page_with_detail_post_context(self):
        """
        Тест данных, которые выводит страница при чтении конкретного поста
        """
        # Сортировка постов на странице выполнена по дате (от новых к старым)
        post_id = self.post_two.pk
        response = self.quest_client.get(
            reverse('posts:post_detail', kwargs={
                'slug': self.group_for_test.slug,
                'post_id': post_id}))
        detail_post = response.context['page_obj'][0]
        self.assertEqual(detail_post.text, self.post_two.text)
        self.assertEqual(detail_post.author, self.auth_user)
        self.assertEqual(detail_post.group, self.group_for_test)
        self.assertEqual(detail_post.image, self.post_two.image)

    def test_group_page_show_correct_context(self):
        """
        Тестирование правильности отображаемого контента на странице рубрики
        """
        response = self.authorized_client_auth_user.get(reverse(
            'posts:group_list',
            kwargs={
                'slug': self.group_for_test.slug})
        )
        page_objects = response.context['page_obj'][0]
        # создадим словарь с ключами, которые в ответ на запрос к странице
        # в значениях ключа - правильное тестируемое значение
        test_page_objects = {
            page_objects.text: self.post_two.text,
            page_objects.group: self.post_two.group,
            page_objects.author: self.post_two.author,
            page_objects.pub_date: self.post_two.pub_date,
            page_objects.image: self.post_two.image
        }
        # сравниваем со значениями 2-го поста, т.к. он создан последним в тесте
        # во view-функции у нас сортировка по убыванию по дате
        for page_obj, correct_data in test_page_objects.items():
            with self.subTest(page_obj=page_obj):
                self.assertEqual(page_obj, correct_data)

    def test_author_page_show_correct_context(self):
        """
        Тестирование правильности отображаемого контента
        на странице пользователя
        """
        response = self.authorized_client_auth_user.get(reverse(
            'posts:profile',
            kwargs={
                'username': self.auth_user.username})
        )
        page_objects = response.context['page_obj'][0]
        # создадим словарь с ключами, которые в ответ на запрос к странице
        # в значениях ключа - правильное тестируемое значение
        test_page_objects = {
            page_objects.text: self.post_two.text,
            page_objects.group: self.post_two.group,
            page_objects.author: self.post_two.author,
            page_objects.pub_date: self.post_two.pub_date,
            page_objects.image: self.post_two.image
        }
        # сравниваем со значениями 2-го поста, т.к. он создан последним в тесте
        # во view-функции у нас сортировка по убыванию по дате
        for page_obj, correct_data in test_page_objects.items():
            with self.subTest(page_obj=page_obj):
                self.assertEqual(page_obj, correct_data)

    def test_cach_on_index_page(self):
        """
        Проверяем работает ли кеширование на главной странице
        """
        self.post_for_cach_test = Post.objects.create(
            text=('1111Подумайте перед задолго до pсоставлением '
                  'словаря с шаблонами и адресамиии.'),
            author=self.auth_user,
            group=self.group_for_test,
        )
        post_created = Post.objects.filter(id=self.post_for_cach_test.pk)
        # делаем запрос к странице до удаления поста с БД
        response_before = self.quest_client.get(reverse('posts:index'))
        Post.objects.filter(id=self.post_for_cach_test.pk).delete()
        post_empty = Post.objects.filter(id=self.post_for_cach_test.pk)
        # делаем запрос к странице уже после удаления поста
        response_after = self.quest_client.get(reverse('posts:index'))
        self.assertTrue(response_before.content, response_after.content)
        self.assertFalse(post_created, post_empty)


class PaginatorObjectsViewsTest(TestCase):
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

    def test_index_page_contains_nine_records(self):
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
            reverse('posts:profile', kwargs={
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
            reverse('posts:profile', kwargs={
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
            reverse('posts:profile', kwargs={
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
        # slug=test-slug-second - url второй'
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


class CommentsViewsTest(TestCase):
    """
    Проверяем, что:
    ---------------
    - Комментировать посты может только авторизованный пользователь;
    - После успешной отправки комментарий появляется на странице поста.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.user = User.objects.create(
            username='test-user'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post_one = Post.objects.create(
            text=('В базе данных проекта Yatube уже хранится информация'
                  'об авторах и их постах. Дадим пользователям '
                  'возможность комментировать записи друг друга.'),
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.quest_user = Client()
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)

    def test_create_comment_only_auth_user(self):
        """
        Тестирование комментирования поста - только авторизованные
        """
        comments_count_first = Comment.objects.count()
        text_comment = {
            'text': 'Первый комментарий, к этому чудесному тесту',
            'post': self.post_one,
            'author': self.user}
        response = self.auth_user.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post_one.pk}),
            data=text_comment,
            follow=True)
        comments_count_second = Comment.objects.count()
        self.assertTrue(comments_count_second, (comments_count_first+1))
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={
                'slug': self.group.slug,
                'post_id': self.post_one.pk
            }))

    def test_comment_on_page(self):
        self.comment_on_page = Comment.objects.create(
            text='Первый комментарий, к этому чудесному тесту',
            post=self.post_one,
            author=self.user
        )
        response = self.quest_user.get(reverse(
            'posts:post_detail',
            kwargs={
                'slug': self.group.slug,
                'post_id': self.post_one.pk
            }))
        page_objects = response.context['page_obj'][0]
        self.assertTrue(page_objects.comments, self.comment_on_page.text)


class FollowingViewsTest(TestCase):
    """
    Проверяем, что:
    ---------------
    - Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок.
    - Новая запись пользователя появляется в ленте тех, кто на него
        подписан.
    """
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_1 = User.objects.create(
            username='test-user'
        )
        cls.user_2 = User.objects.create(
            username='test-user-2'
        )
        cls.user_3 = User.objects.create(
            username='test-user-3'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post_one = Post.objects.create(
            text=('Yatube уже хранится информация'
                  'об авторах и их постах. Дадим пользователям '
                  'возможность комментировать записи друг друга.'),
            author=cls.user_1,
            group=cls.group
        )
        cls.post_two = Post.objects.create(
            text=('базе данных проекта Yatube уже хранится информация'
                  'об авторах и их постах. Дадим пользователям '
                  'возможность друга.'),
            author=cls.user_2,
            group=cls.group
        )
        cls.post_three = Post.objects.create(
            text=('данных проекта хранится информация'
                  'об авторах и их постах. Дадим пользователям '
                  'возможность комментировать записи друг друга.'),
            author=cls.user_3,
            group=cls.group
        )
        cls.auth_user_one = Client()
        cls.auth_user_one.force_login(cls.user_1)
        cls.auth_user_two = Client()
        cls.auth_user_two.force_login(cls.user_2)
        cls.client_user_three = Client()

    def test_follow_other_author(self):
        """
        Тестируем подписку "user_1" на "user_3"
        """
        # будет False
        is_follow_firsttime = Follow.objects.filter(
            author=self.user_3, user=self.user_1).exists()
        response = self.auth_user_one.get(
            reverse('posts:profile_follow',
                    kwargs={
                        'username': self.user_3.username,
                    }))
        # будет True
        is_follow_secondtime = Follow.objects.filter(
            author=self.user_3, user=self.user_1).exists()
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user_3.username, }))
        self.assertEqual(is_follow_firsttime, False)
        self.assertEqual(is_follow_secondtime, True)

    def test_unfollow_other_author(self):
        """
        Тестируем удаление из подписок ("user_1" удаляет подписку на "user_3")
        """
        pass
        self.start_following = Follow.objects.create(
            author=self.user_3, user=self.user_1)
        # "is_follow_firsttime" должна быть True
        is_follow_firsttime = Follow.objects.filter(
            author=self.user_3, user=self.user_1).exists()
        response = self.auth_user_one.get(
            reverse('posts:profile_unfollow',
                    kwargs={
                        'username': self.user_3.username,
                    }))
        # будет False
        is_follow_secondtime = Follow.objects.filter(
            author=self.user_3, user=self.user_1).exists()
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user_3.username, }))
        self.assertEqual(is_follow_firsttime, True)
        self.assertEqual(is_follow_secondtime, False)

    def test_posts_on_follow_user(self):
        """
        Тестируем видимость постов в ленте подписчика (у "user_1" в ленте
        должны появиться посты "user_3")
        """
        self.start_following = Follow.objects.create(
            author=self.user_3, user=self.user_1)
        response = self.auth_user_one.get(
            reverse('posts:follow_index'))
        # берём текст первого поста, автора, на которого подписались
        text_post_user_3 = response.context['page_obj'][0].text
        author_post_user_3 = response.context['page_obj'][0].author
        # и сравниваем с текстом автора "user_3"
        self.assertEqual(text_post_user_3, self.post_three.text)
        self.assertEqual(author_post_user_3, self.user_3)
