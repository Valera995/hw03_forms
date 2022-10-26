from django.shortcuts import get_object_or_404, render

from django.conf import settings

from .models import Group, Post


def index(request):
    posts = Post.objects.select_related('group')[:settings.POSTS_COUNT]
    template = 'posts/index.html'
    context = {'posts': posts}
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')[:settings.POSTS_COUNT]
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'posts': posts
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    paginator = Paginator(post_list, settings.PAGE_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_number = post_list.count()
    context = {
        'page_obj': page_obj,
        'post_number': post_number,
        'author': user,  # здесь мне нужен этот контекст,
        # не могу к нему обратиться из шаблона
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = get_object_or_404(User, username=post.author)
    post_number = user.posts.filter(author=user).count()
    context = {
        'post': post,
        'post_number': post_number,
        'post_id': post_id,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)

    return render(request, 'posts/create_post.html',
                  {'form': form, 'username': request.user})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id=post_id)

    return render(request, 'posts/create_post.html',
                  {'form': form, 'username': request.user, 'is_edit': True})
