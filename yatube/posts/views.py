from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User
from .forms import PostForm


def index(request):
    template = 'posts/group_posts.html'
    posts = Post.objects.order_by('-pub_date')
    paginator = Paginator(posts, 9)
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
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': f'Записи сообщества: {group.title}',
        'page_obj': page_obj,
    }
    return render(request, template, context)


def posts_author(request, username):
    template = 'posts/group_posts.html'
    posts = get_object_or_404(User, username=username)
    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    author_posts = Post.objects.filter(author=posts).order_by('-pub_date')
    count_author_posts = author_posts.count()
    paginator = Paginator(author_posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': f'Статьи автора {posts.get_full_name()}',
        'page_obj': page_obj,
        'count_posts': count_author_posts,
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
            paginator = Paginator(search_post, 9)
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
        if request.user.pk == posts[0].author.pk:
            is_author = True
        context = {
            'page_obj': posts,
            'is_author': is_author
        }
    else:
        context = None
    return render(request, template, context)


def post_detail_whithout_group(request, post_id):
    is_author = False
    template = 'posts/post_detail.html'
    # post = get_object_or_404(Post, pk=post_id)
    post = Post.objects.filter(pk=post_id)
    if post_id:
        if request.user.pk == post[0].author.pk:
            is_author = True
        context = {
            'page_obj': post,
            'is_author': is_author
        }
    else:
        context = None
    return render(request, template, context)


@login_required()
def user_profile(request, username):
    pass


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
                return redirect('posts:posts_author', username=username)
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
            return redirect('posts:posts_author', username=username)
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
