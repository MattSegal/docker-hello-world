import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone

from .models import RedditUser, RedditThread, RedditComment
from .utils import get_reddit_oauth_header

BASE_URI = 'https://oauth.reddit.com'

logging = get_task_logger(__name__)

# TODO: Use Redis to keep under Reddit imposed rate limit


@shared_task
def fetch_comments(reddit_user_pk):
    logging.info('Fetching comments for RedditUser[%s]', reddit_user_pk)
    reddit_user = RedditUser.objects.get(pk=reddit_user_pk)
    logging.info('Found RedditUser with name %s', reddit_user.username)

    # TODO: Bail if user has been fetched recently

    url = '{}/user/{}/comments'.format(BASE_URI, reddit_user.username)
    params = {
        'limit': 25,
    }
    headers = {
        'Authorization':  get_reddit_oauth_header(),
        'User-Agent': settings.REDDIT_USER_AGENT
    }

    logging.info('Fetching comment data from Reddit API endpoint  %s', url)
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    comments_data = resp.json()['data']['children']
    logging.info('Creating comments')
    thread_ids = set()
    for data in comments_data:
        reddit_comment, created = RedditComment.objects.update_or_create(
            reddit_id=data['id'],
            defaults={
                # TODO: Keep track of thread:comment mapping FK somehow
                'author': reddit_user,
                'score': data['score'],
                'downs': data['downs'],
                'created_utc': data['created_utc'],
                'body_html': data['body_html'],
            }
        )
        thread_ids.add(data['link_id'])
        # Logging

    # Kick off thread_ids fetch

    logging.info('Updating RedditUser[%s]', reddit_user_pk)
    reddit_user.fetched_at = timezone.now()
    reddit_user.save()
    logging.info('Done', reddit_user_pk)


@shared_task
def fetch_threads(thread_ids, reddit_user_pk):
    logging.info('Processing threads from RedditUser[%s]', reddit_user_pk)

    thread_id_list = ','.join(list(thread_ids))
    url = '{}/by_id/{}'.format(BASE_URI, thread_id_list)
    params = {
        'limit': 100,
    }
    headers = {
        'Authorization':  get_reddit_oauth_header(),
        'User-Agent': settings.REDDIT_USER_AGENT
    }
    logging.info('Fetching thread data from Reddit API endpoint  %s', url)
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    threads_data = resp.json()['data']['children']
    logging.info('Creating threads')
    for data in threads_data:
        reddit_thread, created = RedditThread.objects.update_or_create(
            reddit_id=data['id'],
            defaults={
                'is_self': data['is_self'],
                'score': data['score'],
                'num_comments': data['num_comments'],
                'created_utc': data['created_utc'],
                'author': data['author'],  # Create author if not in db already
                'subreddit': data['subreddit'],
                'permalink': data['permalink'],
                'title': data['title'],
                'url': "http://www.reddit.com" + data['permalink'],
            }
        )
    logging.info('Done', reddit_user_pk)
