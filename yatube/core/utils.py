from django.core.paginator import Paginator

POST_COUNTER = 10


def paginator(request, post):
    paginator = Paginator(post, POST_COUNTER)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
