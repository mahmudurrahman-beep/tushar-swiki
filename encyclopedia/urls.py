from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Wiki URLs
    path('', views.index, name='index'),
    path('wiki/<str:title>/', views.entry, name='entry'),
    path('search/', views.search, name='search'),
    path('new/', views.new_page, name='new_page'),
    path('edit/<str:title>/', views.edit_page, name='edit_page'),
    path('random/', views.random_page, name='random_page'),
    path("history/<str:title>/", views.history, name="history"), 
]
