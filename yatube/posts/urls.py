from django.urls import path
from .views import *

app_name = 'posts'

urlpatterns = [
    # в случаях коллизий с одинаковыми адресами
    # работает правило "кто выше, тот и главный"
    path('', index, name='index'),
    path('group/<slug:slug>/', group_posts, name='group_list'),
    path('search/', search, name='search_posts'),
    path('profile/<str:username>',
         profile, name='profile'),
    path('group/<slug:slug>/<int:post_id>/',
         post_detail, name='post_detail'),
    path('group/<int:post_id>',
         post_detail_whithout_group, name='post_detail_whithout_group'),
    path('group/<int:post_id>/edit/',
         post_edit, name='post_edit'),
    path('create/', post_create, name='post_create'),
    path('posts/<int:post_id>/comment',
         add_comment, name='add_comment'),
    path('follow/', follow_index, name='follow_index'),
    path('profile/<str:username>/follow/',
         profile_follow, name='profile_follow'),
    path('profile/<str:username>/unfollow/',
         profile_unfollow, name="profile_unfollow"),
]
