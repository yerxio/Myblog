from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('home/', views.PostListView.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('test-article/', views.test_article, name='test_article'),
    path('category/new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<slug:category_slug>/', views.PostListView.as_view(), name='post_list_by_category'),
    path('tag/<str:tag_slug>/', views.PostListView.as_view(), name='post_list_by_tag'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
] 