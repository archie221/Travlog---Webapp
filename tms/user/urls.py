from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [

	path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.register, name='signup'),
    path('profile/', views.profile, name='profile')
    # path('upd_profile/', views.update, name='update')

]