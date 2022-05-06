from django.views.generic import CreateView

# Импортируем функцию reverse_lazy, чтобы получить URL по 
# параметрам функции path() 
from django.urls import reverse_lazy

# Импортируем свой класс формы, чтобы сослаться на него
# во view-классе
from .forms import CreationForm

class SignUp(CreateView):
    form_class = CreationForm
    # В случае успешной регистрации, перенаправляем
    # по 'namespace:name'
    success_url = reverse_lazy('post:index')
    template_name = 'users/signup.html'