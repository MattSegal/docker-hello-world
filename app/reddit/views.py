from django.views.generic import TemplateView

from .models import Counter
from .tasks import count

class HomeView(TemplateView):
	template_name = 'home.html'

	def get(self, request):
		# count.delay()
		return super().get(request)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		if Counter.objects.count() == 0:
			counter = Counter.objects.create(count=0)
		else:
			counter = Counter.objects.last()
		context['counter'] = counter
		return context
