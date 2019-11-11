from django.urls import path
from django.conf.urls import url
from logic import views

app_name = 'logic'

urlpatterns = [
    url('', views.index, name='landing'),
    url('index/', views.index, name='index'),
    url(r'^login/$', views.login_service, name='login'),
    url('logout/', views.logout_service, name='logout'),
    url('signup/', views.signup_service, name='signup'),

]
