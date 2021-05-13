from django.contrib.auth.models import User
from django.db import models

news = 'N'
article = 'A'
CHOICE = [(news, 'новость'), (article, 'статья')]


class Author(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    author_rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.author}"

    def update_rating(self):
        p_rating = 0
        p = Post.objects.filter(post_author=self)
        for i in p:
            p_rating += i.post_rating * 3

        c_rating = 0
        c = Comment.objects.filter(com_user=self.author)
        for i in c:
            c_rating += i.com_rating

        all_c_rating = 0
        for i in p:
            a = Comment.objects.filter(com_post=i)
            for j in a:
                all_c_rating += j.com_rating

        self.author_rating = p_rating + c_rating + all_c_rating
        self.save()


class Category(models.Model):
    category = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscribers')

    def __str__(self):
        return f"{self.category}"


class Post(models.Model):
    post_author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_choice = models.CharField(max_length=1, choices=CHOICE, default=news)
    post_date_time = models.DateTimeField(auto_now_add=True)
    post_category = models.ManyToManyField(Category, through='PostCategory', related_name='posts')
    post_title = models.CharField(max_length=255)
    post_text = models.TextField()
    post_rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.post_text}"

    def get_absolute_url(self):
        return f'/{self.id}'

    def post_like(self):
        self.post_rating += 1
        self.save()

    def post_dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        return str(self.post_text[:124] + '...')


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    com_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    com_user = models.ForeignKey(User, on_delete=models.CASCADE)
    com_text = models.TextField()
    com_date_time = models.DateTimeField(auto_now_add=True)
    com_rating = models.IntegerField(default=0)

    def com_like(self):
        self.com_rating += 1
        self.save()

    def com_dislike(self):
        self.com_rating -= 1
        self.save()