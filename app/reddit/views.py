from django.views.generic import TemplateView

from .models import RedditUser, RedditThread, RedditComment
from .tasks import fetch_comments

class HomeView(TemplateView):
    template_name = 'home.html'

    def get(self, request):
        reddit_user, created = RedditUser.objects.get_or_create(username='gwern')
        fetch_comments.delay(reddit_user.pk)
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = RedditUser.objects.all()
        context['threads'] = (
            RedditThread.objects.all()
            .order_by('-created_utc')
        )
        return context
