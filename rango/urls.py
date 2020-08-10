from django.conf.urls import url
from django.urls import path, re_path
from rango import views

urlpatterns = [
    path('', views.imageIndex, name='index'),
    path('about/', views.about, name='about'),
    path('add_category/', views.add_category, name='add_category'),
    re_path('category/(?P<category_name_slug>[\w\-]+)/$', views.show_category, name='show_category'),
    re_path('category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('restricted/', views.restricted, name='restricted'),
    path('logout/', views.user_logout, name='logout'),
]