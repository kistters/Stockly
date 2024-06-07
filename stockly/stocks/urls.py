# myproject/stocks/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('stock/<str:stock_symbol>/', views.stock_detail, name='stock-detail'),
]