from django.contrib import admin
from django.urls import path, include, re_path

from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path('oauth/', include('social_django.urls', namespace='social')),
    path('admin/', admin.site.urls),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    path('', views.HomeView.as_view(), name='home'),
    path(
    	'user/follow/',
    	views.FollowRedditUserView.as_view(),
    	name='follow'
    ),
    path(
    	'user/unfollow/<str:username>/',
    	views.UnfollowRedditUserView.as_view(),
    	name='unfollow'
    ),
]
