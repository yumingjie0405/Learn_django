from django.urls import path
from . import views
from .views import edit_book, CreateBookView, add_book, AnalysisView, delete_book
from django.contrib.auth import views as auth_views
from .views import BookSearchView
urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.user_registration, name='register'),
    path('main/', views.main_page, name='main'),
    path('get_verification_code/', views.get_verification_code, name='get_verification_code'),
    path('logout/', views.user_logout, name='logout'),

    path('create_book/', CreateBookView.as_view(), name='create_book'),
    path('add/', add_book, name='add_book'),
    path('analysis/', AnalysisView.as_view(), name='analysis'),
    path('book_detail/<int:pk>/', views.book_detail, name='book_detail'),
    path('edit_book/<int:pk>/', edit_book, name='edit_book'),
    path('delete_book/<int:pk>/', views.delete_book, name='book_delete'),
    path('chart/', views.chart_view, name='chart'),
    path('search/', BookSearchView.as_view(), name='search'),
]
