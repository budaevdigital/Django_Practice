from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model   

User = get_user_model() 


# Создадим свой класс для формы регистрации
# и сделаем его наследником предустановленного
# класса UserCreationForm
class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # укажем модель, с которой связана создаваемая форма
        model = User
        # укажем какие поля должны быть видны в форме и в каком порядке
        fields = ('first_name', 'last_name', 'user_name', 'email')
