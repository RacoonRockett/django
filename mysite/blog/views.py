from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

from .forms import EmailPostForm, CommentForm
from .models import Post, Comment
from taggit.models import Tag


# Create your views here.
def post_list(request, tag_slug=None):
    # posts = Post.published.all()
    # return render(request, 'blog/post/list.html', {'posts': posts})

    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags_in=[tag])

    paginator = Paginator(object_list, 3)  # 3 поста на каждую страницу
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)  # Если страница не цифра, вернуть первую страницу
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)  # Если за границей диапазона, вернуть последнюю
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day
                             )
    # Список активных комментов для этой статьи
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # Пользователь отправил коммент
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаём коммент, но пока не сохраняем в БД
            new_comment = comment_form.save(commit=False)
            # Привязываем коммент к текущей статье
            new_comment.post = post
            # Сохраняем коммент в БД
            new_comment.save()
        else:
            comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    # Извлечение поста по айди.
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Форма была подтверждена
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы прошли проверку
            cd = form.cleaned_data
            # Отправка почты
            post_url = request.build_absolute_url(post.get_absolut_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
        else:
            form = EmailPostForm()
            return render(request, 'blog/post/share.html', {'post': post,
                                                            'form': form,
                                                            'sent': sent})
