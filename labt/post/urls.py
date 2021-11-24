from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [

	path('', views.home, name='home'),
	path('create/',views.create, name='create'),
	path('join/postid=<post_id>',views.join, name ='join'),
	path('joinrequest/',views.joinrequest, name ='joinrequest'),
	path('joinapprove/<request_id>',views.joinapprove, name ='joinapprove'),
	path('mrequest/',views.mrequest, name='mrequest'),
	path('approve/<post_id>',views.approve, name='approve')

]