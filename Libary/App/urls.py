from django.urls import path
from . import views
from .views import edit_book, CreateBookView, add_book, AnalysisView, delete_book
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.user_registration, name='register'),
    path('main/', views.main_page, name='main'),
    path('get_verification_code/', views.get_verification_code, name='get_verification_code'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('add_book/', add_book, name='add_book'),
    # path('delete_book/<int:pk>/', BookDeleteView.as_view(), name='delete_book'),
    path('edit_book/<int:pk>/', edit_book, name='edit_book'),
    path('delete_book/<int:pk>/', delete_book, name='delete_book'),

    # path('search_book/', search_book, name='search_book'),
    path('create_book/', CreateBookView.as_view(), name='create_book'),
    path('add/', add_book, name='add_book'),
    path('analysis/', AnalysisView.as_view(), name='analysis'),
]
