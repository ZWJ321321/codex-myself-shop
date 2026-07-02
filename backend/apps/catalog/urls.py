from django.urls import path

from .views import CategoryListView, DishListView

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("dishes/", DishListView.as_view(), name="dish-list"),
]
