# posts/forms.py
from django import forms
from .models import Post, Group, Comment
from .validators import validate_not_empty_or_less, validate_for_comment


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

    image = forms.ImageField(required=False)

    class Meta():
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea,
                           required=True,
                           label='Комментировать',
                           validators=[validate_for_comment])

    class Meta():
        model = Comment
        fields = ('text',)
