# IMPORTS #
import requests
from django.conf import settings
from rest_framework import serializers

from core.order.models import(
    TicketOrder,
    Order,
    PurchasedTicket,
)
from core.event.models import(
    Ticket
)
from api.utils import Util




class TicketOrderSerializer(serializers.ModelSerializer):

    item = serializers.CharField(source="item.name")

    class Meta:
        model = TicketOrder
        fields = [
            'item',
            'quantity',
        ]




class TicketOrderSummarySerializer(serializers.ModelSerializer):

    item = serializers.CharField(source="item.name")

    total = serializers.CharField(source='get_total_item_price', read_only=True)

    class Meta:
        model = TicketOrder
        fields = [
            'item',
            'quantity',
            'total',
        ]




class OrderPublicSerializer(serializers.Serializer):
    email = serializers.EmailField(
        read_only=True
    )

    amount = serializers.CharField(source='get_total_amount')



# ORDER CREATE SERIALIZER #

class OrderSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=True,
    )

    selected_ticket = TicketOrderSerializer(
        many=True,
    )

    class Meta:
        model = Order
        fields = [
            'email',
            'selected_ticket',
            'order_id',
        ]
        read_only_fields = [
            'order_id',
        ]
        depth = 1

    def create(self, validated_data):
        event_obj = self.context['event_obj']
        selected_tickets = validated_data.pop('selected_ticket', [])
        new_order = Order.objects.create(**validated_data)

        for tix in selected_tickets:
            try:
                tix_obj = Ticket.objects.get(name=tix["item"]["name"], event=event_obj)
            except Ticket.DoesNotExist:
                raise serializers.ValidationError({"error": "This ticket does not exist"})

            try:
                tix_order = TicketOrder.objects.get(item = tix_obj, quantity = tix["quantity"])
            except TicketOrder.DoesNotExist:
                tix_order = TicketOrder.objects.create(item = tix_obj, quantity = tix["quantity"])

            new_order.selected_ticket.add(tix_order)
        
        return new_order




# USER ORDER CREATE SERIALIZER #
class UserOrderSerializer(serializers.ModelSerializer):

    selected_ticket = TicketOrderSerializer(
        many=True,
    )

    class Meta:
        model = Order
        fields = [
            'selected_ticket',
            'order_id',
        ]
        read_only_fields = [
            'order_id',
        ]
        depth = 1

    def create(self, validated_data):
        event_obj = self.context['event_obj'].name
        selected_tickets = validated_data.pop('selected_ticket', [])
        new_order = Order.objects.create(**validated_data)

        for tix in selected_tickets:
            try:
                tix_obj = Ticket.objects.get(name=tix["item"]["name"], event__name=event_obj)
            except Ticket.DoesNotExist:
                raise serializers.ValidationError({"error": "This ticket does not exist"})

            try:
                tix_order = TicketOrder.objects.get(item = tix_obj, quantity = tix["quantity"])
            except TicketOrder.DoesNotExist:
                tix_order = TicketOrder.objects.create(item = tix_obj, quantity = tix["quantity"])

            new_order.selected_ticket.add(tix_order)

        return new_order




# ORDER SUMMARY SERIALIZER #
class OrderSummarySerializer(serializers.ModelSerializer):

    selected_ticket = TicketOrderSummarySerializer(
        many=True,
    )

    total_amount = serializers.CharField(source="get_total_amount", read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_id',
            'selected_ticket',
            'paystack_payment_reference',
            'total_amount',
        ]
        depth = 1




# PURCHASED TICKET LIST SERIALIZER #
class PurchasedTicketListSerializer(serializers.ModelSerializer):

    order = serializers.CharField(source="order.email")

    ticket = serializers.CharField(source="ticket.name")

    #ticket_id = serializers.CharField(source="qrcode_id")

    # url = serializers.HyperlinkedIdentityField(
    #     view_name='core.order:purchased-ticket-detail',
    #     lookup_field='qrcode_id',
    # )

    url = serializers.SerializerMethodField()

    class Meta:
        model = PurchasedTicket
        fields = [
            'order',
            'ticket',
            'qrcode_id',
            'purchased_date',
            'url',
        ]

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.qrcode_id)




# PURCHASED TICKET DETAIL SERIALIZER #
class PurchasedTicketDetailSerializer(serializers.ModelSerializer):

    order = serializers.CharField(source="order.email")

    ticket = serializers.CharField(source="ticket.name")

    #ticket_id = serializers.CharField(source="qrcode_id")

    class Meta:
        model = PurchasedTicket
        fields = [
            'order',
            'ticket',
            'qrcode_id',
            'checkin_status',
            'purchased_date',
        ]

        