from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm
from django.http import Http404
from .models import *


def post_list(request):
    object_list = Post.published.all()
    paginator   = Paginator(object_list, 5)
    page        = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    return render(request, 'blog/post/list.html', {"page": page,"posts": posts})


class PostListView(ListView):
    queryset            = Post.objects.all()
    context_object_name = 'posts'
    paginate_by         =  5
    template_name       = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    try:
        post = get_object_or_404(Post, slug=post, status="published", publish__year=year,
                                 publish__month=month, publish__day=day)
    except Http404:
        print("Exception occur")
    return render(request, "blog/post/detail.html", {'post': post})


def post_share(request, post_id):
    post        = get_object_or_404(Post, id=post_id, status='published')
    comments    = Comment.objects.filter(active=True)
    sent = False
    if request.method == "POST":
        print("Hi")
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd          = form.cleaned_data
            post_url    = request.build_absolute_uri(post.get_absolute_url())
            subject     = "{} ({}) recommends you reading '{}'".format(cd['name'], cd['email'], post.title)
            message     = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            hey         = cd['email']
            print(hey)
            send_mail(subject, message, hey, [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

