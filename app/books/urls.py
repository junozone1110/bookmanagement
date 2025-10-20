from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('api/fetch-book-info/', views.fetch_book_info, name='fetch_book_info'),
]

