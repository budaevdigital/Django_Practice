# posts/forms.py
from django import forms
from .models import Post, Group
from .validators import validate_not_empty_or_less


class PostForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(),
                                   required=False,
                                   label='Рубрика',
                                   help_text='Из уже существующих')
    text = forms.CharField(widget=forms.Textarea,
                           required=True,
                           label='Текст статьи',
                           help_text='Напишите лучшую статью',
                           validators=[validate_not_empty_or_less])

    class Meta():
        model = Post
        fields = ('group', 'text')
