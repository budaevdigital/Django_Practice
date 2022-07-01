from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from . import views

app_name = 'posts'
router = DefaultRouter()
router.register('posts', views.PostViewSet, basename='post')
router.register(
     r'posts/(?P<post_id>\d+)/comments',
     views.CommentViewSet,
     basename='comment')
router.register('groups', views.GroupViewSet, basename='group')

urlpatterns = [
    # в случаях коллизий с одинаковыми адресами
    # работает правило "кто выше, тот и главный"
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('search/', views.search, name='search_posts'),
    path('profile/<str:username>',
         views.profile, name='profile'),
    path('group/<slug:slug>/<int:post_id>/',
         views.post_detail, name='post_detail'),
    path('group/<int:post_id>',
         views.post_detail_whithout_group, name='post_detail_whithout_group'),
    path('group/<int:post_id>/edit/',
         views.post_edit, name='post_edit'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/comment',
         views.add_comment, name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path('profile/<str:username>/follow/',
         views.profile_follow, name='profile_follow'),
    path('profile/<str:username>/unfollow/',
         views.profile_unfollow, name="profile_unfollow"),
    path('api/v1/', include(router.urls)),
    path('api/v1/api-token-auth/',
         TokenObtainPairView.as_view(), name='obtain_auth_token'),
    path('api/v1/api-token-auth/refresh',
         TokenRefreshView.as_view(), name='refresh_auth_token'),
]
