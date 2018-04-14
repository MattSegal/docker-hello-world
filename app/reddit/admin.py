from django.contrib import admin

from .models import RedditUser, RedditThread, RedditComment

admin.site.register(RedditUser)
admin.site.register(RedditThread)
admin.site.register(RedditComment)
