from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Post, Category, Comment
from django.db.models import Q
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from taggit.models import Tag

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(status='published')
        category_slug = self.kwargs.get('category_slug')
        tag_slug = self.kwargs.get('tag_slug')
        search_query = self.request.GET.get('q')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        if tag_slug:
            try:
                tag = Tag.objects.get(slug=tag_slug)
                queryset = queryset.filter(tags=tag)
            except Tag.DoesNotExist:
                try:
                    tag = Tag.objects.get(name=tag_slug)
                    queryset = queryset.filter(tags=tag)
                except Tag.DoesNotExist:
                    queryset = Post.objects.none()

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            try:
                tag = Tag.objects.get(slug=tag_slug)
                context['tag'] = tag
            except Tag.DoesNotExist:
                try:
                    tag = Tag.objects.get(name=tag_slug)
                    context['tag'] = tag
                except Tag.DoesNotExist:
                    pass
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        post = super().get_object()
        post.views += 1
        post.save()
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['comments'] = self.object.comments.filter(active=True)
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'category', 'content', 'featured_image', 'tags', 'status']

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # 确保作者被设置
                form.instance.author = self.request.user
                
                # 确保状态为已发布
                form.instance.status = 'published'
                
                # 如果标题为空，设置一个默认标题
                if not form.instance.title:
                    form.instance.title = f"无标题文章 {timezone.now().strftime('%Y%m%d%H%M%S')}"
                
                # 保存表单
                response = super().form_valid(form)
                messages.success(self.request, '文章创建成功！')
                return response
        except Exception as e:
            messages.error(self.request, f'创建文章失败: {str(e)}')
            return super().form_invalid(form)

    def get_success_url(self):
        """自定义成功后的重定向URL，避免使用post对象的get_absolute_url"""
        return reverse_lazy('blog:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'category', 'content', 'featured_image', 'tags', 'status']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, '文章更新成功！')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '文章删除成功！')
        return super().delete(request, *args, **kwargs)

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'blog/category_form.html'
    fields = ['name', 'description']

    def form_valid(self, form):
        form.instance.slug = None  # Let the model's save method handle slug creation
        messages.success(self.request, '分类创建成功！')
        return super().form_valid(form)

def about(request):
    return render(request, 'blog/about.html')
