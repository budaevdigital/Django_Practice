from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=25)
    description = models.TextField(max_length=500)

    # для нормального отображения в списке
    # без этого метода, будет "Group object"
    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL,
        related_name='group',
        blank=True,
        null=True
    )

    # для нормального отображения в списке
    # без этого метода, будет "Post object"
    def __str__(self):
        return f'{self.text}'


# Создадим свой класс для формы регистрации
# и сделаем его наследником предустановленного
# класса UserCreationForm
class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # укажем модель, с которой связана создаваемая форма
        model = User
        # укажем какие поля должны быть видны в форме и в каком порядке
        fields = ('first_name', 'last_name', 'user_name', 'email')
