from django.shortcuts import HttpResponse, render
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns=[
    path('', views.home, name="home"),
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('logout/',LogoutView.as_view(next_page='/'), name="logout"),
    path('post/',views.post_view, name="post"),
    path('analyze/', views.analyze, name='analyze'),
    path('analyze/result', views.result, name='result'),
    path('download_file/', views.download_file, name='download_file'),
    path('delete_file/', views.delete_file, name='delete_file'),
    path('workinprogress/', views.work, name="workinprogress")
]