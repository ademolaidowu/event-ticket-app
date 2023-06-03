'''
    This file contains urls for the Event Views
'''

# IMPORTS #

from django.urls import path

from core.event.views import (
    event_category_list_view,
    event_listcreate_view,
    event_detail_view,
)



app_name = 'core.event'
urlpatterns = [
    path('category/', event_category_list_view, name='event-category-list'),
    path('', event_listcreate_view, name='event-list-create'),
    path('<slug:slug>/', event_detail_view, name='event-detail'),
]