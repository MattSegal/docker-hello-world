from datetime import datetime, timedelta

import requests
from django.conf import settings
from redis import Redis


def get_reddit_oauth_header():
    """
    Get Reddit OAuth header if we don't have it already
    or if it expired.
    """
    redis = Redis(host=settings.REDIS_HOST)
    token = redis.get(get_auth_key('token')).decode('utf-8')
    created = redis.get(get_auth_key('created')).decode('utf-8')
    valid_seconds = int(redis.get(get_auth_key('valid')).decode('utf-8')) or 0

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
        redis.set(get_auth_key('token'), token)
        redis.set(get_auth_key('valid'), data['expires_in'])
        redis.set(get_auth_key('created'), datetime.now())

    return "bearer {0}".format(token)


def get_auth_key(s):
    return 'auth-token-' + s
