from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
from django.utils.text import slugify

class CustomUser(AbstractUser):
    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:post_list_by_category', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
    )
    
    title = models.CharField('标题', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name='作者'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='分类'
    )
    content = RichTextField('内容')
    featured_image = models.ImageField(
        '特色图片',
        upload_to='blog_images/%Y/%m/%d/',
        blank=True,
        null=True
    )
    tags = TaggableManager('标签')
    status = models.CharField(
        '状态',
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)
    views = models.PositiveIntegerField('浏览量', default=0)

    class Meta:
        ordering = ['-created']
        verbose_name = '文章'
        verbose_name_plural = '文章'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        # 如果标题为空，设置一个默认标题
        if not self.title:
            from django.utils import timezone
            self.title = f"无标题文章 {timezone.now().strftime('%Y%m%d%H%M%S')}"
            
        # 生成 slug
        if not self.slug:
            # 确保标题可以被slugify
            slug_base = self.title if self.title else 'post'
            self.slug = slugify(slug_base)
            if not self.slug:  # 如果 slugify 后为空（例如全是中文字符）
                from django.utils import timezone
                self.slug = f"post-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            # 确保 slug 唯一
            orig_slug = self.slug
            counter = 1
            # 查询时排除当前实例（对于更新操作）
            existing_slug_qs = Post.objects.filter(slug=self.slug)
            if self.pk:
                existing_slug_qs = existing_slug_qs.exclude(pk=self.pk)
                
            while existing_slug_qs.exists():
                self.slug = f"{orig_slug}-{counter}"
                counter += 1
                if self.pk:
                    existing_slug_qs = Post.objects.filter(slug=self.slug).exclude(pk=self.pk)
                else:
                    existing_slug_qs = Post.objects.filter(slug=self.slug)
        
        super().save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='文章'
    )
    name = models.CharField('名字', max_length=80)
    email = models.EmailField('邮箱')
    body = models.TextField('评论内容')
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)
    active = models.BooleanField('是否可见', default=True)

    class Meta:
        ordering = ['created']
        verbose_name = '评论'
        verbose_name_plural = '评论'

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
