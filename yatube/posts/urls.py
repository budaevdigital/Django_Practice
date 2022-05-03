from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # в случаях коллизий с одинаковыми адресами
    # работает правило "кто выше, тот и главный"
    path('', views.index, name='index'),
    path('group/<slug:slug>', views.group_posts, name='group_list'),
    path('search/', views.search, name='search_posts'),
]