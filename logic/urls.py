from django.urls import path
from django.conf.urls import url
from logic import views

app_name = 'logic'

urlpatterns = [
    path('', views.index, name='landing'),
    path('index/', views.index, name='index'),
    path('login/', views.login_service, name='login'),
    path('logout/', views.logout_service, name='logout'),
    path('signup/', views.signup_service, name='signup'),
    path('counter/', views.counter_service, name='counter'),
]
