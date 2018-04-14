from django.db import models
from django.contrib.auth.models import User


class RedditUser(models.Model):
    username = models.CharField(max_length=32, unique=True)
    followers = models.ManyToManyField(User, related_name='followed_users')
    updated_at = models.DateTimeField(auto_now=True)
    fetched_at = models.DateTimeField(null=True)
    loading = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class RedditThread(models.Model):
    REDDIT_TYPE ='t3'
    reddit_id = models.CharField(max_length=7, unique=True)
    is_self = models.BooleanField()
    score = models.IntegerField()
    num_comments = models.PositiveIntegerField()
    created_utc = models.DateTimeField()
    author = models.ForeignKey(RedditUser, related_name='threads_authored', on_delete=models.CASCADE)
    commenters = models.ManyToManyField(RedditUser, related_name='threads_commented')
    subreddit = models.CharField(max_length=128)
    permalink = models.URLField(max_length=256)
    title = models.CharField(max_length=512)
    url = models.CharField(max_length=512)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reddit_id


class RedditComment(models.Model):
    reddit_id = models.CharField(max_length=7, unique=True)
    link_id = models.CharField(max_length=16)
    thread = models.ForeignKey(RedditThread, null=True, related_name='comments', on_delete=models.SET_NULL)
    author = models.ForeignKey(RedditUser, related_name='comments', on_delete=models.CASCADE)
    score = models.IntegerField()
    permalink = models.URLField(max_length=256)
    downs = models.PositiveIntegerField()
    created_utc = models.DateTimeField()
    body_html = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reddit_id
