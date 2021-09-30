from django.urls import path
from . import views as listing_views

urlpatterns = [
    path('', listing_views.ProductListView.as_view(), name='listing-home-page'),
    path('add/', listing_views.listing_add, name='listing-add-page'),
    path('product/<int:pk>/delete/', listing_views.ProductDeleteView.as_view(), name='listing-delete'),
    # pk is the primary key of the product in the DB
    path('product/<int:pk>/', listing_views.ProductDetailView.as_view(), name='listing-detail'),
]
