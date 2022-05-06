# Импортируем из приложения django.contrib.auth нужный view-класс 
from django.contrib.auth.views import LogoutView  
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [     
	path('logout/',       
            # Прямо в описании обработчика укажем шаблон,        
            # который должен применяться для отображения возвращаемой страницы.
            # Да, во view-классах так можно!
            LogoutView.as_view(template_name='users/logged_out.html'),
            name='logout'),
        
    path('signup/',
        # Полный адрес страницы регистрации - auth/signup/,     
	    # но префикс auth/ обрабатывется в головном urls.py 
        views.SignUp.as_view(), name='signup')
]