# users/tests/urls.py
# Импортируем из приложения django.contrib.auth нужный view-класс
from django.contrib.auth.views import (LogoutView, LoginView,
                                       PasswordChangeView,
                                       PasswordChangeDoneView,
                                       PasswordResetView,
                                       PasswordResetDoneView,
                                       PasswordResetConfirmView,
                                       PasswordResetCompleteView)
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('logout/',
         # Прямо в описании обработчика укажем шаблон,
         # который должен применяться для отображения возвращаемой страницы.
         # Да, во view-классах так можно!
         LogoutView.as_view(template_name='users/logged_out.html'),
         name='logged_out'),

    path('signup/',
         # Полный адрес страницы регистрации - auth/signup/,
         # но префикс auth/ обрабатывется в головном urls.py
         views.SignUp.as_view(), name='signup'),

    path('login/',
         LoginView.as_view(
            template_name='users/login.html'), name='login'),


    # Настроим страницы для смены пароля и страницу с подтверждением
    path('password_change/',
         PasswordChangeView.as_view(
            template_name='users/password_change_form.html'),
         name='password_change_form'),

    path('password_change/done/',
         PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'),
         name='password_change_done'),

    # Настроим форму сброса пароля, через email
    path('password_reset/',
         PasswordResetView.as_view(
            template_name='users/password_reset_form.html'),
         name='password_reset_form'),

    # И страницу подтверждения отправки ссылки на емайл
    path('password_reset/done/',
         PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'),
         name='password_reset_done'),

    # Настраиваем страницу подтверждения сброса пароля через почту
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),

    # Настраиваем страницу уведомления о том, что пароль изменён
    path('reset/done/',
         PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]
