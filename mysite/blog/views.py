from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# def post_list(request):
#     posts = Post.published.all()
#     return render(
#         request,
#         'blog/post/list.html',
#         {
#             'posts': posts,
#         }
#     )


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)   # liczba postów na str
    page = request.GET.get('page')          # nr bieżącej str
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # jeśli page nie jest integerem, pobież 1 str
        posts = paginator.page(1)
    except EmptyPage:
        # jesli page > od ost str, wyświetl ost str
        # ost str (paginator.num_pages)
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts})


def post_details(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
        }
    )