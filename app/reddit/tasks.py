import html

import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone

from .models import RedditUser, RedditThread, RedditComment
from .utils import get_reddit_oauth_header, epoch_to_datetime_utc, rate_limit

BASE_URI = settings.REDDIT_OAUTH_BASE_URI
logger = get_task_logger(__name__)


# FIXME: Use INFO for logging not WARNING
@shared_task
def fetch_comments(reddit_user_pk):
    logger.warning('Fetching comments for RedditUser[%s]', reddit_user_pk)
    reddit_user = RedditUser.objects.get(pk=reddit_user_pk)
    logger.warning('Found RedditUser with name %s', reddit_user.username)
    rate_limit()

    url = '{}/user/{}/comments'.format(BASE_URI, reddit_user.username)
    params = {
        'limit': 25,
    }
    headers = {
        'Authorization':  get_reddit_oauth_header(),
        'User-Agent': settings.REDDIT_USER_AGENT
    }

    logger.warning('Fetching comment data from Reddit API endpoint  %s', url)
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    comments_data = resp.json()['data']['children']
    logger.warning('Creating comments')
    thread_ids = set()
    for wrapped_data in comments_data:
        data = wrapped_data['data']
        thread_id = data['link_id'].replace(RedditThread.REDDIT_TYPE + '_', '')
        reddit_comment, created = RedditComment.objects.update_or_create(
            reddit_id=data['id'],
            defaults={
                'author': reddit_user,
                'link_id': thread_id,
                'score': data['score'],
                'downs': data['downs'],
                'permalink': 'https://reddit.com' + data['permalink'],
                'created_utc': epoch_to_datetime_utc(data['created_utc']),
                'body_html': html.unescape(data['body_html']),
            }
        )
        thread_ids.add(data['link_id'])
        if created:
            logger.warning('Created RedditComment[%s]', reddit_comment.pk)
        else:
            logger.warning('Found RedditComment[%s]', reddit_comment.pk)

    # Get threads data for fetched comments
    thread_id_list = ','.join(list(thread_ids))
    fetch_threads.delay(thread_id_list, reddit_user_pk)
    logger.warning('Done fetching RedditComments for RedditUser[%s]', reddit_user_pk)


@shared_task
def fetch_threads(thread_id_list, reddit_user_pk):
    logger.warning('Processing threads from RedditUser[%s]', reddit_user_pk)
    rate_limit()
    url = '{}/by_id/{}'.format(BASE_URI, thread_id_list)
    params = {
        'limit': 100,
    }
    headers = {
        'Authorization':  get_reddit_oauth_header(),
        'User-Agent': settings.REDDIT_USER_AGENT
    }
    logger.warning('Fetching thread data from Reddit API endpoint  %s', url)
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    threads_data = resp.json()['data']['children']
    logger.warning('Creating threads')
    for wrapped_data in threads_data:
        data = wrapped_data['data']
        author, _ = RedditUser.objects.get_or_create(username=data['author'])
        reddit_thread, created = RedditThread.objects.update_or_create(
            reddit_id=data['id'],
            defaults={
                'is_self': data['is_self'],
                'score': data['score'],
                'num_comments': data['num_comments'],
                'created_utc': epoch_to_datetime_utc(data['created_utc']),
                'author': author,
                'subreddit': data['subreddit'],
                'permalink': 'https://reddit.com' + data['permalink'],
                'title': data['title'],
                'url': "http://www.reddit.com" + data['permalink'],
            }
        )
        reddit_thread.commenters.add(reddit_user_pk)
        if created:
            logger.warning('Created RedditThread[%s]', reddit_thread.pk)
        else:
            logger.warning('Fetched RedditThread[%s]', reddit_thread.pk)

        logger.warning('Updating RedditComments with link_id %s to use RedditThread[%s]', data['id'], reddit_thread.pk)
        RedditComment.objects.filter(link_id=data['id']).update(thread=reddit_thread)

    logger.warning('Updating RedditUser[%s]', reddit_user_pk)
    reddit_user = RedditUser.objects.get(pk=reddit_user_pk)
    reddit_user.fetched_at = timezone.now()
    reddit_user.loading = False
    reddit_user.save()
    logger.warning('Done fetching RedditThreads for RedditUser[%s]', reddit_user_pk)
