from django.urls import path
from . import views

app_name = 'notif'

urlpatterns = [

	path('', views.notify, name='notify')
]