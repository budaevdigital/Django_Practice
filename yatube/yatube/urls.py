"""yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    # Django проверяет url-адреса сверху вниз,
    # нам нужно, чтобы Django сначала проверял адреса в приложении users
    path('auth/', include('users.urls', namespace='users')),
    # Если какой-то URL не обнаружится в приложении users —
    # Django пойдёт искать его в django.contrib.auth
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('about/', include('about.urls', namespace='about')),
    path('api/', include('api.urls', namespace='api')),
]


handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler403 = 'core.views.permission_denied'

# в режиме разработчика Django не раздаёт картинки, поэтому
# нужно переопределить это поведение Django в режиме DEBUG=True
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
