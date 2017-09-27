from django.views.generic import TemplateView


class VisualTokenView(TemplateView):
    template_name = 'visual_token/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(VisualTokenView, self).get_context_data(**kwargs)
        context['renderer'] = self.kwargs['renderer']
        return context
