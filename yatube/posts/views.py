from django.shortcuts import render, get_object_or_404
from .models import Post, Group

def index(request):
    template = 'posts/index.html'
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'title': 'Последние обновления на сайте',
        'all_posts': posts,
    }
    return render(request, template, context)

def group_posts(request, slug):
    template = 'posts/group_posts.html'
    group = get_object_or_404(Group, slug=slug) 
    # Метод .filter позволяет ограничить поиск по критериям.     
	# Это аналог добавления     
	# условия WHERE group_id = {group_id} 
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10] 
    context = {
        'title': f'Записи сообщества #{group.title}',
        'select_post': posts,
    }      
    return render(request, template, context)

def search(request):
    search_keyword = request.GET.get('search', None)
    template = 'posts/search_posts.html'
    
    if search_keyword:
        search_post = Post.objects.filter(text__contains=search_keyword).select_related('author').select_related('group')
    else:
        search_post = None

    context = {
        'title': 'Поиск статей',
        'posts': search_post,
        'search_key': search_keyword
    }
    return render(request, template, context)
