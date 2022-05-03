from django.contrib import admin
from .models import Post, Group

class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)

    @admin.display(ordering='text',
                   description='Текст',
                   empty_value='-пусто-')
    def text(self, obj):
        return obj.text

    @admin.display(ordering='pub_date',
                   description='Дата публикации',
                   empty_value='-пусто-')
    def pub_date(self, obj):
        return obj.pub_date

    @admin.display(ordering='author',
                   description='Автор',
                   empty_value='-пусто-')
    def author(self, obj):
        return obj.author        

    @admin.display(ordering='group',
                   description='Группа',
                   empty_value='-пусто-')
    def group(self, obj):
        return obj.group      



class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    search_fields = ('title', 'slug')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)