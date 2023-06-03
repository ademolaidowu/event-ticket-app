# IMPORTS #

import requests

from django.conf import settings
from django.shortcuts import redirect
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from api.serializers.order_serializers import (
    UserOrderSerializer,
    OrderSerializer,
    OrderPublicSerializer,
    OrderSummarySerializer,
    PurchasedTicketListSerializer,
    PurchasedTicketDetailSerializer,
)
from api.utils import Util
from core.order.models import (
    Order,
    PurchasedTicket,
)
from core.event.models import(
    Ticket,
    Event,
)




# CREATE ORDER VIEW #

class OrderAPIView(GenericAPIView):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None

    # POST
    def post(self, request, event, *args, **kwargs):
        try:
            event_obj = Event.events.upcoming().get(slug=event)
        except Event.DoesNotExist:
            return Response(
                {'error': 'This event is not available'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(
            data=request.data,
            context={
                "request": request,
                "event_obj": event_obj
            }
        )
        if serializer.is_valid(raise_exception=True):
            user = self.request.user
            if user.is_authenticated:
                serializer.save(
                    user=user,
                    email=user.email,
                    event=event_obj
            )
            else:
                serializer.save(event=event_obj)

            new_order = Order.objects.get(order_id=serializer.data['order_id'])
            pay_info = OrderPublicSerializer(new_order)
            data = pay_info.data
            new_order_id = new_order.order_id

            if float(data['amount']) > 0:
                url = 'https://api.paystack.co/transaction/initialize'
                headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            
                r = requests.post(url, headers=headers, data=data)
                response = r.json()
                print(response)
                new_order.paystack_payment_reference = response['data']['reference']
                new_order.save()
                return Response(new_order_id, status=status.HTTP_200_OK)
            else:
                return Response(new_order_id, status=status.HTTP_200_OK)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


create_order_view = OrderAPIView.as_view()




# ==============================================================================
# ORDER SUMMARY
# ==============================================================================

class OrderSummaryAPIView(GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSummarySerializer
    pagination_class = None

    # GET # 
    def get(self, request, order_id, *args, **kwargs):
        try:
            order_obj = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'This order is not available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(order_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


order_summary_view = OrderSummaryAPIView.as_view()




# ==============================================================================
# ORDER PAYMENT
# ==============================================================================

class VerifyOrderPaymentAPIView(APIView):

    # GET #
    def get(self, request, order_id, reference):
        try:
            order_obj = Order.objects.get(
                order_id=order_id,
                paystack_payment_reference=reference
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'This order is not available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reference = order_obj.paystack_payment_reference

        url = 'https://api.paystack.co/transaction/verify/{}'.format(reference)

        headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

        r = requests.get(url, headers=headers)
        response = r.json()

        payment_status = response['data']['status']

        if payment_status == 'success':
            if order_obj.order_status == payment_status.upper():
                return Response(
                    {'success': 'Your transaction has already been verified'},
                    status=status.HTTP_200_OK
                )
            order_obj.order_status = payment_status.upper()
            order_obj.save()

            current_site=get_current_site(self.request).domain

            for ticket in order_obj.selected_ticket.annotate():
                quantity = 0
                while quantity < ticket.quantity:
                    p_tix = PurchasedTicket.objects.create(
                        order=order_obj,
                        ticket=ticket.item,
                    )

                    qrcode_url = 'http://'+current_site+p_tix.get_absolute_url()
                    data = {
                        'url': qrcode_url,
                        'ticket': p_tix.qrcode_id
                    }
                    Util.generate_qrcode(data)
                    p_tix.save()

                    msg = {
                        'subject': 'Ticket for {}'.format(p_tix.ticket.event.name),
                        'recipient': p_tix.order.email,
                        'ticket': p_tix.qrcode_id
                    }
                    Util.send_email_attach(msg)

                    quantity += 1
                    
            return Response(response, status=status.HTTP_200_OK)

        return Response(response, status=status.HTTP_400_BAD_REQUEST)


order_payment_view = VerifyOrderPaymentAPIView.as_view()




# ==============================================================================
# PURCHASED TICKET LIST
# ==============================================================================

class PurchasedTicketListAPIView(GenericAPIView):
    queryset = PurchasedTicket.objects.all()
    serializer_class = PurchasedTicketListSerializer

    # GET # 
    def get(self, request, event_slug, *args, **kwargs):
        try:
            event_obj = Event.events.published().get(slug=event_slug)
            purchased_tickets = self.queryset.filter(ticket__event=event_obj)
        except Event.DoesNotExist:
            return Response(
                {'error': 'This event is not available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(
            purchased_tickets,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


purchased_ticket_list_view = PurchasedTicketListAPIView.as_view()




# ==============================================================================
# PURCHASED TICKET DETAIL
# ==============================================================================

class PurchasedTicketDetailAPIView(RetrieveUpdateAPIView):
    queryset = PurchasedTicket.objects.all()
    serializer_class = PurchasedTicketDetailSerializer
    lookup_field = 'qrcode_id'

purchased_ticket_detail_view = PurchasedTicketDetailAPIView.as_view()
