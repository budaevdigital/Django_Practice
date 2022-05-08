from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Post, Group


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.order_by('-pub_date')
    paginator = Paginator(posts, 7)
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
    paginator = Paginator(posts, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': f'Записи сообщества #{group.title}',
        'page_obj': page_obj,
    }
    return render(request, template, context)


def search(request):
    search_keyword = request.GET.get('search', None)
    template = 'posts/search_posts.html'

    if search_keyword:
        search_post = Post.objects.filter(
            text__contains=search_keyword).select_related(
                'author').select_related('group')
        paginator = Paginator(search_post, 7)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None

    context = {
        'title': 'Поиск статей',
        'page_obj': page_obj,
        'search_key': search_keyword
    }
    return render(request, template, context)
