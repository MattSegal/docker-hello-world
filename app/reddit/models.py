from django.db import models
from django.contrib.auth.models import User


class RedditUser(models.Model):
    username = models.CharField(max_length=20, unique=True)
    followers = models.ManyToManyField(User, related_name='followed_users')
    updated_at = models.DateTimeField(auto_now=True)
    fetched_at = models.DateTimeField(null=True)

    def __str__(self):
        return '<RedditUser: {}>'.format(self.username)


class RedditThread(models.Model):
    REDDIT_TYPE ='t3'
    reddit_id = models.CharField(max_length=6, unique=True)
    is_self = models.BooleanField()
    score = models.IntegerField()
    num_comments = models.PositiveIntegerField()
    created_utc = models.BigIntegerField()
    author = models.CharField(max_length=50)
    subreddit = models.CharField(max_length=100)
    permalink = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    url = models.CharField(max_length=500)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '<RedditThread: {} - {} - {}>'.format(self.author,self.subreddit, self.created_utc)


class RedditComment(models.Model):
    reddit_id = models.CharField(max_length=6, unique=True)
    thread = models.ForeignKey(RedditThread, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(RedditUser, related_name='comments', on_delete=models.CASCADE)
    score = models.IntegerField()
    downs = models.PositiveIntegerField()
    created_utc = models.BigIntegerField()
    body_html = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '<RedditComment: {0} - {1}>'.format(self.author,self.reddit_id)
