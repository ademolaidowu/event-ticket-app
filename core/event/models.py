'''
    This model contains Event and Ticket Models
'''

# IMPORTS #

import uuid

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db import models
from django.urls import reverse

from versatileimagefield.fields import VersatileImageField
from ckeditor_uploader.fields import RichTextUploadingField

from core.user.models import User
from api.utils import Util




# MODEL FUNCTIONS #

def generate_event_id():
    code = str(uuid.uuid4()).split("-")[-1] #generate unique event id

    try:
        qs_exists = Event.objects.filter(event_id=code).exists()
        if qs_exists:
            return generate_event_id()
        else:
            return code
    except:
        return code




# EVENT CATEGORY MODEL #

class EventCategory(models.Model):

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Category name',
        help_text='Enter the new category',
    )

    slug = models.SlugField(
        max_length=50,
        unique=True,
    )

    image = VersatileImageField(
        upload_to='events/category/',
        default='events/category/default.jpg',
        verbose_name='Category Image',
        help_text='Upload Category Image',
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Select to make category active',
    )

    class Meta:
        verbose_name = "Event Category"
        verbose_name_plural = "Event Categories"
        ordering = ['name']

    def __str__(self):
        return self.name




# EVENT MODEL #

class Event(models.Model):

    class EventManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_active=True)
        def published(self):
            return super().get_queryset().filter(is_active=True, publish_status=True)
        def upcoming(self):
            return super().get_queryset().filter(
                is_active=True, publish_status=True).exclude(end_date__lt=timezone.now())

    # CHOICES
    event_type_choices = (
        ('single', 'Single'), 
        ('recurring', 'Recurring'),
    )

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name='Event name',
        help_text='Enter the name of Event',
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        null=False,
        help_text='Click on the title field to populate this field',
    )

    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='events'
    )

    event_id = models.CharField(
        db_index=True,
        max_length=15,
        blank=False,
        null=False,
        default=generate_event_id,
        verbose_name='Event UUID',
        editable=False,
    )

    event_type = models.CharField(
        max_length=10,
        choices=event_type_choices,
        default='single',
        blank=False,
        null=False,
        verbose_name='Event Type',
    )

    description = RichTextUploadingField(
        blank=False,
        null=False,
    )

    image = VersatileImageField(
        upload_to='events/cover/',
        default='events/cover/default.jpg',
        verbose_name='Event Image',
        help_text='Upload Event Image',
        blank=True,
        null=True,
    )

    venue = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name='Event Venue',
        help_text='Enter the location of the Event',
    )

    host = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name='Event Host/Organizer',
        help_text='Enter the Host of the Event',
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Status',
    )

    publish_status = models.BooleanField(
        default=False,
        help_text='Select to Publish Event',
        verbose_name='Publish Status',
    )

    start_date = models.DateTimeField(
        blank=False,
        null=False,
        verbose_name='Event Start Date',
    )

    end_date = models.DateTimeField(
        blank=False,
        null=False,
        verbose_name='Event End Date',
    )

    website = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Website',
        help_text='Optional',
    )

    instagram = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Instagram Page',
        help_text='Optional',
    )

    facebook = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Facebook Page',
        help_text='Optional',
    )

    twitter = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Twitter Page',
        help_text='Optional',
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
    )

    date_updated = models.DateTimeField(
        default=timezone.now,
    )

    objects = models.Manager()
    events = EventManager()


    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['-date_created']

    def __str__(self):
        return self.name

    @property
    def event_status(self):
        current_time = timezone.now()
        if current_time < self.start_date:
            return 'SCHEDULED'
        elif current_time > self.end_date:
            return 'ENDED'
        elif self.start_date < current_time < self.end_date:
            return 'LIVE'

    def min_ticket_price(self):
        tix = self.tickets
        tix_price = tix.annotate().aggregate(price=models.Min('price'))
        return tix_price['price']

    def get_absolute_url(self):
        return reverse("core.event:event-detail", kwargs={'slug': self.slug})

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("The start time for the event cannot be greater than the end time, Please verify")
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            if Event.objects.filter(name=self.name).exists():
                extra = Util.random_digit_generator(size=4)
                self.slug = slugify(self.name) + "-" + extra
            else:
                self.slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)




# TICKET MODEL #

class Ticket(models.Model):

    # CHOICES
    ticket_type_choices = (
        ('free', 'Free'), 
        ('paid', 'Paid'), 
    )

    stock_type_choices = (
        ('limited', 'Limited'), 
        ('unlimited', 'Unlimited'), 
    )

    charge_type_choices = (
        ('host', 'Host'), 
        ('guest', 'Guest'),
    )


    name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name='Ticket name',
        help_text='Enter Ticket name',
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='tickets',
    )

    ticket_id = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        editable=False,
    )

    slug = models.SlugField(
        max_length=50,
        help_text='Click on the title field to populate this field',
    )

    type = models.CharField(
        max_length=50,
        choices=ticket_type_choices,
        default='free',
        blank=False,
        null=False,
        verbose_name='Ticket Type',
    )

    description = models.TextField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name='Ticket Description',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Ticket Status',
        help_text='Select to make ticket active',
    )

    stock_type = models.CharField(
        max_length=50,
        choices=stock_type_choices,
        default='unlimited',
        blank=False,
        null=False,
        verbose_name='Stock Type',
    )

    quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Stock Quantity',
    )

    price = models.DecimalField(
        default=0.00,
        blank=False,
        null=False,
        max_digits=10,
        decimal_places=2,
        verbose_name='Ticket Price',
    )

    limit = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        default=5,
        verbose_name='Purchase Limit',
        help_text='Max number of tickets purchasable by one person',
    )

    charges = models.CharField(
        max_length=50,
        choices=charge_type_choices,
        default='host',
        blank=False,
        null=False,
        verbose_name='Service charges',
        help_text='Select who bears the charges',
    )

    sale_start_date = models.DateTimeField(
        blank=False,
        null=False,
        default=timezone.now,
        verbose_name='Ticket Sale Start Date',
    )

    sale_end_date = models.DateTimeField(
        blank=False,
        null=False,
        verbose_name='Ticket Sale End Date',
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
    )

    date_updated = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        unique_together = ('name', 'event')

    def __str__(self):
        return "{} - {}".format(self.event.name, self.name)

    def get_ticket_price(self):
        return self.price

    def clean(self):
        if self.sale_start_date > self.sale_end_date:
            raise ValidationError("The start time for the ticket sale cannot be greater than the end time, Kindly verify")
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            self.slug = slugify(self.name)
        super(Ticket, self).save(*args, **kwargs)