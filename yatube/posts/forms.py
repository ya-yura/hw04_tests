from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': ('Текст'),
            'group': ('Группа'),
        }
        help_texts = {
            'text': ('Напишите же что-нибудь'),
            'group': ('Выберите группу'),
        }
#       Памятка как извещать об ошибках
#        error_messages = {
#            'text': {
#                'max_length': _("Длинноватое название!"),
#            },
#        }
