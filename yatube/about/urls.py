from django.urls import path
from . import views

app_name = 'about'


urlpatterns = [
    # подключаем классы как view функции
    path('author/', views.AboutAuthorViews.as_view(), name='author'),
    path('tech/', views.AboutTechViews.as_view(), name='tech'),
]
