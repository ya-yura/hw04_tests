from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .forms import PostForm

from core import utils


def index(request):
    template = 'posts/index.html'
    post = Post.objects.select_related('group')
    page_obj = utils.paginator(request=request, post=post)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post = group.posts.all()
    page_obj = utils.paginator(request=request, post=post)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    page_obj = utils.paginator(request=request, post=posts)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.author = request.user
        obj.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form,
        'is_edit': False}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    posts = Post.objects.select_related('group')
    post = get_object_or_404(posts, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect('posts:index')
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)
    return render(request, template, {'form': form, 'is_edit': True})
