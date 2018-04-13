import html

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
                'created_utc': data['created_utc'],
                'body_html': html.unescape(data['body_html']),
            }
        )
        thread_ids.add(data['link_id'])
        if created:
            logging.info('Created RedditComment[%s]', reddit_comment.pk)
        else:
            logging.info('Found RedditComment[%s]', reddit_comment.pk)

    # Get threads data for fetched comments
    thread_id_list = ','.join(list(thread_ids))

    fetch_threads.delay(thread_id_list, reddit_user_pk)

    logging.info('Updating RedditUser[%s]', reddit_user_pk)
    reddit_user.fetched_at = timezone.now()
    reddit_user.save()
    logging.info('Done fetching RedditComments for RedditUser[%s]', reddit_user_pk)


@shared_task
def fetch_threads(thread_id_list, reddit_user_pk):
    logging.info('Processing threads from RedditUser[%s]', reddit_user_pk)
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
    for wrapped_data in threads_data:
        data = wrapped_data['data']
        author, _ = RedditUser.objects.get_or_create(username=data['author'])
        reddit_thread, created = RedditThread.objects.update_or_create(
            reddit_id=data['id'],
            defaults={
                'is_self': data['is_self'],
                'score': data['score'],
                'num_comments': data['num_comments'],
                'created_utc': data['created_utc'],
                'author': author,
                'subreddit': data['subreddit'],
                'permalink': data['permalink'],
                'title': data['title'],
                'url': "http://www.reddit.com" + data['permalink'],
            }
        )
        if created:
            logging.info('Created RedditThread[%s]', reddit_thread.pk)
        else:
            logging.info('Fetched RedditThread[%s]', reddit_thread.pk)

        logging.info('Updating RedditComments with link_id %s to use RedditThread[%s]', data['id'], reddit_thread.pk)
        RedditComment.objects.filter(link_id=data['id']).update(thread=reddit_thread)

    logging.info('Done fetching RedditThreads for RedditUser[%s]', reddit_user_pk)
