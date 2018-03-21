from django.views.generic import TemplateView

from .tasks import echo

class HomeView(TemplateView):
	template_name = 'home.html'

	def get(self, request):
		echo.delay()
		return super().get(request)
