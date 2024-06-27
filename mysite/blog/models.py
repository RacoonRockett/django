from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User  # Аутентификация пользователя
from django.urls import reverse
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')

    
# Create your models here.
class Post(models.Model):
    # Выбираем состояние публикации: черновик или опубликовано
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)  # Заголовок статьи
    slug = models.SlugField(max_length=250, unique_for_date='publish')  # URL статьи
    # используя уникальную дату публикации
    author = models.ForeignKey(User, on_delete=models.CASCADE,  # Внешний ключ один ко многим
                               related_name='blog_posts')
    body = models.TextField()  # Содержание статьи
    publish = models.DateTimeField(default=timezone.now)  # Дата публикации
    created = models.DateTimeField(auto_now_add=True)  # Дата создания статьи
    updated = models.DateTimeField(auto_now=True)  # Дата и период редактирования
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')  # Статус статьи

    objects = models.Manager()  # Менеджер по умолчанию
    published = PublishedManager()  # Наш менеджер(кастомный)
    tags = TaggableManager()

    class Meta:  # Метаданные в порядке убывания ( префикс -)
        ordering = ('-publish', )

    def __str__(self):
        return self.title  # Возвращает отображение, понятное для человека

    def get_absolut_url(self):
        return reverse('blog: post.detail', args=[self.publish.year,
                                                  self.publish.month,
                                                  self.publish.day,
                                                  self.slug])


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created', )
