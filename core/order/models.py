'''
    This model contains all Order Models
'''

# IMPORTS #

import uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone
from versatileimagefield.fields import VersatileImageField

from core.event.models import (
    Event,
    Ticket,
)
from core.user.models import User




# MODEL FUNCTIONS #

def generate_order_id():
    code = str(uuid.uuid4()).split("-")[-2]  #generate unique order id
    time = timezone.now().strftime('%Y%m%d%H%M%S')
    ucode = code + time
    try:
        qs_exists = Order.objects.filter(order_id=ucode).exists()
        if qs_exists:
            return generate_order_id()
        else:
            return ucode
    except:
        return ucode


def generate_sold_ticket_id():
    code = str(uuid.uuid4()).split("-")[-1]  #generate unique ticket id
    try:
        qs_exists = PurchasedTicket.objects.filter(qrcode_id=code).exists()
        if qs_exists:
            return generate_sold_ticket_id
        else:
            return 't'+code
    except:
        return 't'+code




# ORDER ITEM MODEL #

class TicketOrder(models.Model):

    item = models.ForeignKey(
        Ticket,
        on_delete=models.SET_DEFAULT,
        default='Deleted Ticket',
        blank=False,
        null=False,
    )

    quantity = models.PositiveIntegerField(
        default=1,
        blank=False,
        null=False, 
    )


    def __str__(self):
       return "{}({})".format(self.item, self.quantity)

    def get_total_item_price(self):
        return self.item.get_ticket_price() * self.quantity




# ORDER MODEL #

class Order(models.Model):

    order_status_choices = (
        ('pending', 'Pending'), 
        ('success', 'Success'), 
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='orders'
    )
    
    email = models.EmailField(
        max_length=100,
        null=False,
        blank=False,
    )

    order_id = models.CharField(
        db_index=True,
        max_length=25,
        default=generate_order_id,
        #editable=False,
    )

    selected_ticket = models.ManyToManyField(
        TicketOrder,
    )

    order_status = models.CharField(
        max_length=25,
        choices=order_status_choices,
        default='pending',
        blank=False,
        null=False,
        verbose_name='Order Status',
    )

    paystack_payment_reference = models.CharField(
        max_length=100,
        verbose_name="Paystack Ref No."
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        #editable=False,
    )

    date_updated = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        return "{} - {}".format(self.order_id, self.email)

    def get_total_amount(self):
        total = 0
        for tix in self.selected_ticket.all():
            total += tix.get_total_item_price()
        return total




# PURCHASED TICKET MODEL #

class PurchasedTicket(models.Model):

    status_choices = (
        ('new', 'New'), 
        ('in', 'In'), 
        ('out', 'Out'),
    )

    order = models.ForeignKey(
        "Order",
        db_index=True,
        blank=False,
        null=False,
        related_name="sold_ticket",
        on_delete=models.CASCADE,
        #editable=False,
    )

    ticket = models.ForeignKey(
        Ticket,
        blank=False,
        null=False,
        related_name="sold_ticket",
        on_delete=models.CASCADE
    )

    qrcode_id = models.CharField(
        db_index=True,
        max_length=25,
        default=generate_sold_ticket_id,
        #editable=False,
    )

    image = VersatileImageField(
        upload_to='events/ticket/',
        verbose_name='Ticket QR Code',
        blank=True,
        null=True,
    )

    purchased_date = models.DateTimeField(
        auto_now_add=True,
    )

    checkin_status = models.CharField(
        max_length=5,
        choices=status_choices,
        default='new',
        blank=False,
        null=False,
        verbose_name='Check-in Status',
    )

#expired as function

    class Meta:
        verbose_name = "Purchased Ticket"
        verbose_name_plural = "Purchased Tickets"
        ordering = ['-purchased_date']

    def __str__(self):
        return "{} - {}({})".format(self.order.email, self.order.event.name, self.ticket.name)

    def get_absolute_url(self):
        return reverse("core.order:purchased-ticket-detail", kwargs={
            'qrcode_id': self.qrcode_id,
            'event_slug': self.ticket.event.slug
        })

    def save(self, *args, **kwargs):
        if not self.image:
            pass
        super(PurchasedTicket, self).save(*args, **kwargs)