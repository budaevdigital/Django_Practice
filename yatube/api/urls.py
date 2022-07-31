from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from . import views


router = DefaultRouter()
router.register(
     r'posts/(?P<post_id>\d+)/comments',
     views.CommentViewSet,
     basename='comment')
router.register('posts', views.PostViewSet, basename='post')
router.register('groups', views.GroupViewSet, basename='group')
router.register('follows', views.FollowViewSet, basename='follow')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
    path('v1/api-token-auth/',
         TokenObtainPairView.as_view(), name='obtain_auth_token'),
    path('v1/api-token-auth/refresh',
         TokenRefreshView.as_view(), name='refresh_auth_token'),
]
