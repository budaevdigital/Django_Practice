from django.views.generic.base import TemplateView


class AboutAuthorViews(TemplateView):
    template_name = 'about/about_author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Здесь можно произвести какие-то действия для создания контекста
        # Для примера в словарь просто передаются две строки
        context['title'] = 'Обо мне'
        context['description'] = ('<p>Развиваю себя в маркетинге,'
                                  ' аналитике данных и в программировании.'
                                  '<br>В этом блоге пишу о своих увлечениях'
                                  ' и проектах, а также о том, что может '
                                  ' пригодится в работе.</p>')
        return context


class AboutTechViews(TemplateView):
    template_name = 'about/about_tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Здесь можно произвести какие-то действия для создания контекста
        # Для примера в словарь просто передаются две строки
        context['title'] = 'Используемые технологии'
        context['description'] = ('Немного того,  '
                                  'что я сейчас изучаю и использую в работе')
        return context
