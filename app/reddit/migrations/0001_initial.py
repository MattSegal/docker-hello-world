# Generated by Django 2.0.4 on 2018-04-14 03:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RedditComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reddit_id', models.CharField(max_length=7, unique=True)),
                ('link_id', models.CharField(max_length=16)),
                ('score', models.IntegerField()),
                ('permalink', models.URLField(max_length=256)),
                ('downs', models.PositiveIntegerField()),
                ('created_utc', models.DateTimeField()),
                ('body_html', models.TextField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RedditThread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reddit_id', models.CharField(max_length=7, unique=True)),
                ('is_self', models.BooleanField()),
                ('score', models.IntegerField()),
                ('num_comments', models.PositiveIntegerField()),
                ('created_utc', models.DateTimeField()),
                ('subreddit', models.CharField(max_length=128)),
                ('permalink', models.URLField(max_length=256)),
                ('title', models.CharField(max_length=512)),
                ('url', models.CharField(max_length=512)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RedditUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, unique=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fetched_at', models.DateTimeField(null=True)),
                ('followers', models.ManyToManyField(related_name='followed_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='redditthread',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='threads_authored', to='reddit.RedditUser'),
        ),
        migrations.AddField(
            model_name='redditthread',
            name='commenters',
            field=models.ManyToManyField(related_name='threads_commented', to='reddit.RedditUser'),
        ),
        migrations.AddField(
            model_name='redditcomment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='reddit.RedditUser'),
        ),
        migrations.AddField(
            model_name='redditcomment',
            name='thread',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='reddit.RedditThread'),
        ),
    ]
