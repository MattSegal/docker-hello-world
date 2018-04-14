import logging

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, View

from .forms import RedditUserForm
from .models import RedditUser, RedditThread, RedditComment
from .tasks import fetch_comments
from .utils import validate_reddit_username

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = 'home.html'

    def get(self, request):
        if self.request.user.is_authenticated:
            self.followed_users = self.request.user.followed_users.all()
            for reddit_user in self.followed_users:
                self.fetch_reddit_user_data(reddit_user)

        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            followed_users_pks = self.followed_users.values_list('pk', flat=True)
            context['form'] = RedditUserForm()
            context['users'] = self.followed_users
            context['threads'] = (
                RedditThread.objects
                .filter(commenters__pk__in=followed_users_pks)
                .order_by('-created_utc')
            )
        return context

    def fetch_reddit_user_data(self, reddit_user):
        """Fetch data for a user if they haven't been fetched recently"""
        half_hour_ago = timezone.now() - timezone.timedelta(minutes=30)
        is_fetched_recently = reddit_user.fetched_at and reddit_user.fetched_at >= half_hour_ago
        if is_fetched_recently:
            logger.info('Skipping RedditUser[%s] - fetched recently', reddit_user.pk)
            return

        if not reddit_user.loading:
            reddit_user.loading = True
            reddit_user.save()

        logger.info('Fetching data for RedditUser[%s]', reddit_user.pk)
        fetch_comments.delay(reddit_user.pk)

class FollowRedditUserView(View):
    http_method_names = ['post']

    def post(self, request):
        user = self.request.user
        form = RedditUserForm(request.POST)
        if form.is_valid() and user.is_authenticated:
            username = form.cleaned_data['username'].strip()
            username_valid = validate_reddit_username(username)
            if username_valid:
                reddit_user, created = RedditUser.objects.get_or_create(username=username)
                reddit_user.followers.add(user)

        return HttpResponseRedirect(reverse('home'))


class UnfollowRedditUserView(View):
    http_method_names = ['post']

    def post(self, request, username):
        user = self.request.user
        if user.is_authenticated:
            try:
                reddit_user = RedditUser.objects.get(username=username)
            except RedditUser.DoesNotExist:
                pass
            else:
                reddit_user.followers.remove(user)

        return HttpResponseRedirect(reverse('home'))
