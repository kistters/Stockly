from django.urls import path
from . import views

urlpatterns = [
    path('stock/<str:stock_ticker>/', views.stock_detail, name='stock-detail'),
]