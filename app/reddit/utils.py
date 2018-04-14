import logging
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.utils import timezone
from redis import Redis

BASE_URI = settings.REDDIT_OAUTH_BASE_URI
logger = logging.getLogger(__name__)


def rate_limit():
    """
    TODO: Respect reddit API rate limit
    """
    pass


def epoch_to_datetime_utc(epoch):
    naive_dt = timezone.datetime.fromtimestamp(epoch)
    return timezone.utc.localize(naive_dt)


def validate_reddit_username(username):
    """
    Return whether a Reddit username is valid, based on Reddit's API
    """
    logger.info('Verifying username %s', username)
    url = BASE_URI + '/api/username_available'
    params = {
        'user': username,
    }
    headers = {
        'Authorization':  get_reddit_oauth_header(),
        'User-Agent': settings.REDDIT_USER_AGENT
    }
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    result = resp.json()
    logger.info('Username %s is available: %s', username, result)
    return not result


def get_reddit_oauth_header():
    """
    Get Reddit OAuth header if we don't have it already
    or if it expired.
    """
    redis = Redis(host=settings.REDIS_HOST)
    token = get_cached_oauth_data('token', redis)
    created = get_cached_oauth_data('created', redis)
    valid_seconds = get_cached_oauth_data('valid', redis)
    valid_seconds = int(valid_seconds) if valid_seconds else 0

    if created:
        created_datetime = datetime.strptime(created, '%Y-%m-%d %H:%M:%S.%f')
        valid_time =  created_datetime + timedelta(seconds=int(valid_seconds))
        is_expired = valid_time < datetime.now()
    else:
        is_expired = True

    if not token or is_expired:
        headers = {
            'Authorization':  settings.REDDIT_BASIC_AUTH,
            'User-Agent': settings.REDDIT_USER_AGENT
        }
        response = requests.post(
            'https://www.reddit.com/api/v1/access_token',
            data={'grant_type': 'client_credentials'},
            headers=headers
        )
        data =  response.json()
        token = data['access_token']
        set_cached_oauth_data('token', token, redis)
        set_cached_oauth_data('valid', data['expires_in'], redis)
        set_cached_oauth_data('created', datetime.now(), redis)

    return "bearer {0}".format(token)


def set_cached_oauth_data(s, val, redis):
    cache_key = 'auth-token-' + s
    redis.set(cache_key, val)


def get_cached_oauth_data(s, redis):
    cache_key = 'auth-token-' + s
    result = redis.get(cache_key)
    if result:
        return result.decode('utf-8')
    else:
        return None
