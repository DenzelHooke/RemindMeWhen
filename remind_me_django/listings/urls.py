from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='listing-home-page'),
    path('add/', views.listing_add, name='listing-add-page'),
]