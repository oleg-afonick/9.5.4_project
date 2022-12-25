from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .filters import PostFilter
from .forms import PostForm
from .models import Post


def home(request):
    return render(request, 'home.html')


class PostsList(ListView):
    model = Post
    ordering = '-date_creation'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next_sale'] = None
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostSearch(ListView):
    model = Post
    template_name = 'post_search.html'
    context_object_name = 'posts'
    ordering = '-date_creation'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['next_sale'] = None
        return context


class PostCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'
    permission_required = ('news.add_post', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_type()
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.method == 'POST':
            path_create = self.request.META['PATH_INFO']
            if path_create == '/news/create/':
                post.post_type = 'NW'
            elif path_create == '/news/articles/create/':
                post.post_type = 'AR'
        post.save()
        return super().form_valid(form)

    def get_type(self):
        path_type = self.request.META['PATH_INFO']
        if path_type == '/news/create/':
            return 'новость'
        elif path_type == '/news/articles/create/':
            return 'статью'


class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = ('news.change_post', )

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.method == 'POST':
            path_edit = self.request.META['PATH_INFO']
            if path_edit == f'/news/{post.pk}/edit/' and post.post_type != 'NW':
                return redirect(self.request.META.get('HTTP_REFERER'))
            elif path_edit == f'/news/articles/{post.pk}/edit/' and post.post_type != 'AR':
                return redirect(self.request.META.get('HTTP_REFERER'))
        post.save()
        return super().form_valid(form)


class PostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    permission_required = ('news.delete_post', )
