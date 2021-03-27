from django.urls import path

from .views import (api_couriers, api_couriers_detail, api_orders,
                    api_orders_assign, api_orders_complete)

urlpatterns = [
    path('couriers/', api_couriers, name='couriers'),
    path('couriers/<int:courier_id>/', api_couriers_detail, name='couriers_detail'),
    path('orders/', api_orders, name='orders'),
    path('orders/assign/', api_orders_assign, name='orders_assign'),
    path('orders/complete/', api_orders_complete, name='orders_complete'),
]
