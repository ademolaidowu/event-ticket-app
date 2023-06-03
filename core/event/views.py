# IMPORTS #

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView, ListCreateAPIView,
    RetrieveUpdateDestroyAPIView, GenericAPIView,
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny
)
from rest_framework.parsers import (
    MultiPartParser, FormParser,
    FileUploadParser, JSONParser,
)

from api.serializers.event_serializers import (
    EventCategorySerializer, 
    EventCreateSerializer, 
    EventListSerializer,
    EventDetailSerializer,
)

from core.event.models import (
    Event,
    EventCategory,
)




# EVENT CATEGORY LIST VIEW #

class EventCategoryListAPIView(ListAPIView):
    queryset = EventCategory.objects.filter(is_active=True)
    serializer_class = EventCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    # GET
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


event_category_list_view = EventCategoryListAPIView.as_view()




# EVENT LIST OR CREATE VIEW #

class EventMainAPIView(ListCreateAPIView):
    queryset = Event.events.upcoming()
    serializer_class = EventCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EventListSerializer
        return EventCreateSerializer

    # GET
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    # POST
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        user = self.request.user

        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)  

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


event_listcreate_view = EventMainAPIView.as_view()




# EVENT DETAIL VIEW #

class EventDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Event.events.upcoming()
    serializer_class = EventDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        return self.queryset.filter(publish_status=True)
    


event_detail_view = EventDetailAPIView.as_view()