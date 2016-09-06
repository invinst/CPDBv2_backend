from django.contrib.contenttypes.models import ContentType


def get_model(model):
    """
    Return model class given applabel and model name

    Usage: get_model('story.StoryPage')
    """
    [app_label, model_name] = model.split('.')
    return ContentType.objects.get(app_label=app_label, model=model_name.lower()).model_class()
