from django.urls import path

from .views import OrderCreateView, OrderPreviewView

urlpatterns = [
    path("orders/preview/", OrderPreviewView.as_view(), name="order-preview"),
    path("orders/", OrderCreateView.as_view(), name="order-create"),
]
