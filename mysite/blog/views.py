from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag


# def post_list(request):
#     posts = Post.published.all()
#     return render(
#         request,
#         'blog/post/list.html',
#         {
#             'posts': posts,
#         }
#     )


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])  # tags__in - bo manager się nazywa tags

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
    return render(
        request,
        'blog/post/list.html',
        {
            'page': page,
            'tag': tag,
            'posts': posts,     # jeśli widok oparty na def, w paginacji
                               # {% include "pagination.html" with page=posts %}
        }
    )


# class PostListView(ListView):
#     # queryset = Post.published.all()   # możemy zostać przy model = Post a Django za nas przygotuje kolecję
#                                         # QuerySet Post.published.all()
#     model = Post
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_details(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    # lista aktywnych komentarzy dla posta wyciągniętego wyżej
    comments = post.comments.filter(active=True)
    new_comment_add = False

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            #  tworzymy nowy komentarz na podstawie wysłanych danych
            #  ale jeszcze go nie zapisujemy do bazy
            new_comment = comment_form.save(commit=False)
            #  przypisujemy go do posta
            new_comment.post = post
            #  zapisuejmy w bazie
            new_comment.save()
            new_comment_add = True
    else:
    # if request.method == 'GET':
        comment_form = CommentForm()
    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
            'new_comment_add': new_comment_add,
        }
    )


def post_share(request, post_id):
    #  pobieranie posta na podst. jego identyfikatora
    post = get_object_or_404(
        Post,
        id=post_id,
        status='published',
    )
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)  # tworzymy formularz na podst. wysłanych danych z request.POST
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = 'według {0} (a to ichni mail{1}) mówi, że "{2}" jest ok'.format(
                cd['name'], cd['email'], post.title
            )
            message = 'Jak coś "{0}" jest tu {1}\n\n{2}\ skomentował tak: {3}'.format(
                post.title, post_url, cd['name'], cd['comments']
            )
            send_mail(subject, message, 'od kogo', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent,
        }
    )
