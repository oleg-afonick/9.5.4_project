from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    author_rating = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def update_rating(self):
        author_posts_rating = Post.objects.filter(author_id=self.pk).aggregate(
            posts_rating_sum=Coalesce(Sum('post_rating') * 3, 0))
        author_comments_rating = Comment.objects.filter(user_id=self.user).aggregate(
            comments_rating_sum=Coalesce(Sum('comment_rating'), 0))

        self.author_rating = author_posts_rating['posts_rating_sum'] + author_comments_rating['comments_rating_sum']
        self.save()


class Category(models.Model):
    category_name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.category_name


class Post(models.Model):
    article = 'AR'
    news = 'NW'
    SELECT_POST = [(article, 'Статья'), (news, 'Новость')]
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=SELECT_POST, default=article)
    date_creation = models.DateTimeField(auto_now_add=True)
    post_category = models.ManyToManyField(Category, through='PostCategory')
    post_title = models.CharField(max_length=255)
    post_text = models.TextField()
    post_rating = models.IntegerField(default=0)

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        if len(self.post_text) > 124:
            return f'{self.post_text[:124]}...'
        return self.post_text

    def __str__(self):
        return f'{self.post_title}: {self.post_text}'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()

    def __str__(self):
        return f'{self.user} ({self.comment_text[:30]}...)'
