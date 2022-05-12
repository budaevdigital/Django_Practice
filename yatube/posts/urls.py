from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # в случаях коллизий с одинаковыми адресами
    # работает правило "кто выше, тот и главный"
    path('', views.index, name='index'),
    path('group/<slug:slug>', views.group_posts, name='group_list'),
    path('search/', views.search, name='search_posts'),
    path('profile/<str:username>/', views.user_profile, name='profile'),
    path('profile/<str:username>/posts',
         views.posts_author, name='posts_author'),
    path('group/<slug:slug>/<int:post_id>/',
         views.post_detail, name='post_detail'),
]
