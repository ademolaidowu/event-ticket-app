from django.contrib import admin

from core.order.models import (
    TicketOrder,
    Order,
    PurchasedTicket,
)




class OrderAdmin(admin.ModelAdmin):
    list_display = ('email', 'order_id', 'event', 'date_created', 'order_status')
    list_filter = ('order_status',)
    search_fields = ['email', 'event']




class PurchasedTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'order', 'qrcode_id', 'purchased_date')
    list_filter = ('purchased_date',)
    search_fields = ['order', 'ticket', 'qrcode_id']




admin.site.register(TicketOrder)
admin.site.register(Order, OrderAdmin)
admin.site.register(PurchasedTicket, PurchasedTicketAdmin)

