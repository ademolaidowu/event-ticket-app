from django.contrib import admin

from core.event.models import (
    Event,
    EventCategory,
    Ticket,
)




class EventTicketInline(admin.StackedInline):
    model = Ticket

    readonly_fields = ("date_updated",)
    classes = ['collapse']




class EventCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}




class EventAdmin(admin.ModelAdmin):

    fieldsets = (
        ('Event Details', {'fields': (
        'name', 'slug', 'category', 'user', 
        'event_id', 'event_type', 'description',
        'image', 'venue', 'host', 'is_active',
        'publish_status', 'start_date', 'end_date'
        )}),

        ('Socials', {'fields': (
        'website', 'instagram', 'facebook', 'twitter',
        )}),
    )

    list_display = ('name', 'user', 'event_id', 'event_status', 'publish_status')
    list_filter = ('publish_status', 'is_active')
    search_fields = ['name', 'user']
    readonly_fields = ['event_id']
    prepopulated_fields = {"slug": ("name",)}

    inlines = [EventTicketInline]




class EventTicketAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

    readonly_fields = ("date_updated",)




admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Ticket, EventTicketAdmin)
