from django.urls import path

from .views import OrderCreateView, OrderPreviewView

urlpatterns = [
    path("order-previews", OrderPreviewView.as_view(), name="order-preview"),
    path("orders", OrderCreateView.as_view(), name="order-create"),
]
