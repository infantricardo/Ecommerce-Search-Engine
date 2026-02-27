from django.urls import path
from .views import ProductSearchView, ProductCreateView, ProductMetaDataUpdateView

urlpatterns = [
    path("search/product", ProductSearchView.as_view(), name="search-product"),
    path("create/product", ProductCreateView.as_view(), name="create-product"),
    path("update/product", ProductMetaDataUpdateView.as_view(), name="create-product")]