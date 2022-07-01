# posts/views.py
from rest_framework import viewsets, permissions
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .permissions import AuthorPermission
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from .serializers import (PostSerializer,
                          CommentSerializer, GroupSerializer)

POSTS_ON_PAGES = 9

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        AuthorPermission
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, AuthorPermission,)

    # queryset во вьюсете не указываем
    # Нам тут нужны не все комментарии, а только связанные с id
    # Поэтому нужно переопределить метод get_queryset и применить фильтр
    def get_queryset(self):
        # Получаем id из эндпоинта
        id = self.kwargs.get('post_id')
        # И отбираем только нужные комментарии
        post = get_object_or_404(Post, id=id)
        new_queryset = post.comments.all()
        return new_queryset

    def perform_create(self, serializer):
        id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=id)
        serializer.save(author=self.request.user, post=post)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )


# Кешируем страницу раз в 120 секунд
# При прогоне тестов, желательно отключить
@cache_page(60 * 2)
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.order_by('-pub_date')
    paginator = Paginator(posts, POSTS_ON_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Последние обновления на сайте',
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_posts.html'
    group = get_object_or_404(Group, slug=slug)
    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(posts, POSTS_ON_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': f'Записи сообщества: {group.title}',
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    author_posts = Post.objects.filter(author=user).order_by('-pub_date')
    count_author_posts = author_posts.count()
    paginator = Paginator(author_posts, POSTS_ON_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = (request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=user
        ).exists())

    user_is_not_author = request.user != user
    context = {
        'title': f'Профиль пользователя {user.get_full_name()}',
        'page_obj': page_obj,
        'count_posts': count_author_posts,
        'following': following,
        'username': user,
        'user_is_not_author': user_is_not_author
    }
    return render(request, template, context)


def search(request):
    template = 'posts/search_posts.html'
    if request.method == 'GET':
        search_keyword = request.GET.get('search', None)
        if search_keyword:
            search_post = Post.objects.filter(
                text__contains=search_keyword).select_related(
                    'author').select_related('group')
            paginator = Paginator(search_post, POSTS_ON_PAGES)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
        else:
            page_obj = {}
    context = {
        'title': 'Поиск статей',
        'page_obj': page_obj,
        'search': search_keyword
    }
    return render(request, template, context)


def post_detail(request, slug, post_id):
    is_author = False
    if slug is None:
        return redirect('posts:post_detail_whithout_group', post_id=post_id)
    template = 'posts/post_detail.html'
    group = get_object_or_404(Group, slug=slug)
    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    if post_id and slug:
        posts = Post.objects.filter(group=group).filter(pk=post_id)
        comments = Comment.objects.filter(post=post_id).order_by('-created')
        form = CommentForm(request.POST or None)
        if request.user.pk == posts[0].author.pk:
            is_author = True
        context = {
            'page_obj': posts,
            'is_author': is_author,
            'comments': comments,
            'form': form
        }
    else:
        context = None
    return render(request, template, context)


def post_detail_whithout_group(request, post_id):
    is_author = False
    template = 'posts/post_detail.html'
    post = Post.objects.filter(pk=post_id)
    comments = Comment.objects.filter(post=post_id).order_by('-created')
    form = CommentForm(request.POST or None)
    if post_id:
        if request.user.pk == post[0].author.pk:
            is_author = True
        context = {
            'page_obj': post,
            'is_author': is_author,
            'comments': comments,
            'form': form
        }
    else:
        context = None
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    try:
        slug = post.group.slug
        return redirect('posts:post_detail',
                        slug=slug,
                        post_id=post_id)
    # если "AttributeError: 'NoneType' object has no attribute 'slug'"
    # у поста нету slug (group), то отлавливаем NoneType
    # (ошибку AttributeError) и делаем редирект на страницу без slug
    except AttributeError:
        return redirect('posts:post_detail_whithout_group',
                        post_id=post_id)


@login_required()
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    edit_title = 'Редактирование записи'
    post = get_object_or_404(Post, pk=post_id)
    # return render(request, template, {'form': form, 'title':
    # context, 'text': edit_title})
    if request.user.pk == post.author.pk:
        # Если метод POST, то передаем данные формы в класс PostForm (forms.py)
        if request.method == 'POST':
            form = PostForm(
                request.POST or None,
                files=request.FILES or None,
                instance=post
            )
            if form.is_valid():
                # формируем запись для отправки в БД, но не отправляем
                temp = form.save(commit=False)
                # а перед отправкой указываем автора публикации
                # (авторизованный юзер)
                temp.author = request.user
                # вот теперь публикуем
                form.save()
                # Передаём имя пользователя в переменную, чтобы передать
                # при редиректе
                username = request.user.username
                return redirect('posts:profile', username=username)
            context = {
                'form': form,
                'title': edit_title}
            return render(request, template, context)
            # выводим ошибки формы, если данные  не прошли валидацию
        else:
            # Если метод НЕ POST!
            form = PostForm(instance=post)
            context = {
                'form': form,
                'title': edit_title,
                'is_edit': True}

            return render(request, template, context)
    # Если пользователю не принаджлежит пост - делаем редирект
    else:
        try:
            slug = post.group.slug
            return redirect('posts:post_detail',
                            slug=slug,
                            post_id=post_id)
        # если "AttributeError: 'NoneType' object has no attribute 'slug'"
        # у поста нету slug (group), то отлавливаем NoneType
        # (ошибку AttributeError) и делаем редирект на страницу без slug
        except AttributeError:
            return redirect('posts:post_detail_whithout_group',
                            post_id=post_id)


@login_required()
def post_create(request):
    template = 'posts/create_post.html'
    create_title = 'Создание записи'
    # Если метод POST, то передаем данные формы в класс PostForm (forms.py)
    if request.method == 'POST':
        form = PostForm(
                request.POST or None,
                files=request.FILES or None)

        if form.is_valid():
            # формируем запись для отправки в БД, но не отправляем
            temp = form.save(commit=False)
            # а перед отправкой указываем автора
            # публикации (авторизованный юзер)
            temp.author = request.user
            # вот теперь публикуем
            form.save()
            # Передаём имя пользователя в переменную, чтобы
            # передать при редиректе
            username = request.user.username
            return redirect('posts:profile', username=username)
        # выводим ошибки формы, если данные  не прошли валидацию
        context = {
            'form': form,
            'title': create_title}
        return render(request, template, context)

    # Если метод НЕ POST!, то передаем чистую форму
    form = PostForm()
    context = {
            'form': form,
            'title': create_title}
    return render(request, template, context)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    following_post_list = Post.objects.filter(
        author__following__user=request.user).order_by('-pub_date')
    empty_following = not following_post_list.exists()
    paginator = Paginator(following_post_list, POSTS_ON_PAGES)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Последние обновления на сайте',
        'page_obj': page_obj,
        'empty_following': empty_following
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
