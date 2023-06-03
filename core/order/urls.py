'''
    This file contains urls for the Order Views
'''

# IMPORTS #
from django.urls import path

from core.order.views import (
    create_order_view,
    order_summary_view,
    order_payment_view,
    purchased_ticket_list_view,
    purchased_ticket_detail_view,
)



app_name = 'core.order'
urlpatterns = [
    path('<slug:event>/buy-ticket/', create_order_view, name='create-order'),
    path('<str:order_id>/summary/', order_summary_view, name='order-summary'),
    path('<str:order_id>/verify-payment/<str:reference>/', order_payment_view, name='payment-order'),
    path('purchased-tickets/<slug:event_slug>/', purchased_ticket_list_view, name='purchased-ticket-list'),
    path('purchased-tickets/<slug:event_slug>/<str:qrcode_id>/', purchased_ticket_detail_view, name='purchased-ticket-detail'),
]