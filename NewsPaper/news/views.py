from django.shortcuts import render
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import Post, Category
from .filters import PostFilter
from .forms import PostForm
from .tasks import send_email


class Search(ListView):
    model = Post
    template_name = 'news/search.html'
    context_object_name = 'news'
    ordering = ['-id']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['categories'] = Category.objects.all()
        return context


class NewsList(ListView):
    model = Post
    template_name = 'news/news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-id')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()  # добавим переменную текущей даты time_now
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        context['categories'] = Category.objects.all()
        return context


class PostDetail(DetailView):
    model = Post  # модель всё та же, но мы хотим получать детали конкретно отдельного товара
    template_name = 'news/post.html'  # название шаблона будет product.html
    context_object_name = 'post'  # название объекта. в нём будет


def subscribe(request, **kwargs):
    category_req=request.POST.get('subs')
    category= Category.objects.get(id=int(category_req))
    current_user = request.user.id
    category.subscribers.add(current_user)
    return render(request, template_name='news/subscribe_message.html')


class PostCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'news/create.html'
    form_class = PostForm
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        form.save()
        post = Post.objects.get(id=form.instance.pk)
        post_url = f'http://127.0.0.1:8000/{form.instance.pk}'
        categories = post.post_category.all()
        cat_id = 0
        for c in categories:
            cat_id = c.id

        get_subscribers = Category.objects.get(id=cat_id)
        subs_list = get_subscribers.subscribers.all()
        for sub in subs_list:
            send_to = sub.email
            send_to_uname = sub.username
            send_email.delay(send_to=send_to, post_url=post_url, post_text=post.post_text, post_title=post.post_title, send_to_uname=send_to_uname)
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'news/create.html'
    form_class = PostForm
    permission_required = ('news.change_post',)

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDeleteView(DeleteView):
    template_name = 'news/delete.html'
    queryset = Post.objects.all()
    success_url = '/'


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')


def get_user(request):
    return request.user
