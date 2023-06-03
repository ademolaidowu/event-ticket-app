from django.utils import timezone
from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from core.event.models import (
    Event,
    EventCategory,
    Ticket,
)




# TICKET DETAIL SERIALIZER #

class EventTicketPublicSerializer(serializers.Serializer):
    name = serializers.CharField()
    type = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2,
    )




# TICKET CREATE SERIALIZER #

class EventTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = [
            'name', 'type', 'description', 'is_active',
            'stock_type', 'quantity', 'price', 'limit',
            'charges', 'sale_start_date', 'sale_end_date',
        ]

    def validate(self, attrs):
        current_time = timezone.now()
        sale_start_date = attrs.get('sale_start_date')
        sale_end_date = attrs.get('sale_end_date')

        if current_time > sale_start_date:
                raise serializers.ValidationError(
                    {'error': 'Start time for ticket sales cannot be before the current time. Kindly verify'}
                )
        elif current_time > sale_end_date:
                raise serializers.ValidationError(
                    {'error': 'End time for ticket sales cannot be before the current time. Kindly verify'}
                )
        elif sale_start_date > sale_end_date:
                raise serializers.ValidationError(
                    {'error': 'Start time for ticket sales cannot be greater than the end time. Kindly verify'}
                )
        return super().validate(attrs)
    



# EVENT CATEGORY SERIALIZER #

class EventCategoryPublicSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = EventCategory
        fields = ['name',]


class EventCategorySerializer(serializers.ModelSerializer):

    image = VersatileImageFieldSerializer(
        sizes=[('full_size', 'url'),]
    )

    class Meta:
        model = EventCategory
        fields = [
            'name', 'image',
        ]




# EVENT LIST SERIALIZER #

class EventListSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='core.event:event-detail',
        lookup_field='slug',
    )

    event_type = serializers.ChoiceField(
        choices=Event.event_type_choices,
    )

    image = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__100x100'),
        ]
    )

    price = serializers.CharField(source='min_ticket_price')

    #category = EventCategoryPublicSerializer(read_only=True)
    #category = serializers.CharField(source='category.name')
    # event_status = serializers.ChoiceField(
    #     choices=Event.EventStatus,
    # )

    class Meta:
        model = Event

        fields = [
            'url', 'name', 'event_type','image', 
            'venue', 'price', 'start_date',
        ]




# EVENT CREATE SERIALIZER #

class EventCreateSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(
        queryset=EventCategory.objects.all(),
        slug_field='slug',
    )

    event_type = serializers.ChoiceField(
        choices=Event.event_type_choices,
    )

    image = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__100x100'),
        ],
        required=False,
    )

    tickets = EventTicketSerializer(
        required=False, many=True,
    )

    class Meta:
        model = Event
        fields = [
            'name', 'category', 'event_type', 'description', 'image',
            'venue', 'host', 'start_date', 'end_date', 'tickets',
            'website', 'instagram', 'facebook', 'twitter',
        ]

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        current_time = timezone.now()

        if current_time > start_date:
            raise serializers.ValidationError(
                {'error': 'Event start time cannot be before the current time. Kindly verify'}
            )
        elif current_time > end_date:
            raise serializers.ValidationError(
                {'error': 'Event end time cannot be before the current time. Kindly verify'}
            )
        elif start_date > end_date:
            raise serializers.ValidationError(
                {'error': 'Start time of the event cannot be greater than the end time. Kindly verify'}
            )
        return super().validate(attrs)
    

    def create(self, validated_data):
        created_tickets = validated_data.pop('tickets', [])
        new_event = Event.objects.create(**validated_data)

        for tix in created_tickets:
            try:
                tix_obj = Ticket.objects.get(name=tix["name"], event__slug=new_event.slug)
            except Ticket.DoesNotExist:
                tix_obj = Ticket.objects.create(
                    event=new_event,
                    name=tix['name'],
                    type=tix['type'],
                    description=tix['description'],
                    is_active=tix['is_active'],
                    stock_type=tix['stock_type'],
                    quantity=tix['quantity'],
                    price=tix['price'],
                    limit=tix['limit'],
                    charges=tix['charges'],
                    sale_start_date=tix['sale_start_date'],
                    sale_end_date=tix['sale_end_date'],
                )
            else:
                raise serializers.ValidationError({"ticket": "This ticket exists already"})

            new_event.tickets.add(tix_obj)

        return new_event




# EVENT DETAIL SERIALIZER #

class EventDetailSerializer(serializers.ModelSerializer):

    category = serializers.CharField(source='category.name')

    event_type = serializers.ChoiceField(
        choices=Event.event_type_choices,
    )

    image = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url'),
            #('thumbnail', 'thumbnail__100x100'),
        ]
    )

    tickets = EventTicketPublicSerializer(
        read_only=True, many=True,
    )

    class Meta:
        model = Event

        fields = [
            'name', 'category', 'event_type', 'description',
            'image', 'venue', 'host', 'tickets', 
            'publish_status', 'start_date', 'end_date', 'website',
            'instagram', 'facebook', 'twitter',
        ]