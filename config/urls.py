'''
    This file contains the URL configuration
'''


from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .settings import base

admin.site.site_header = base.DJANGO_ADMIN_HEADER
admin.site.index_title = base.DJANGO_ADMIN_TITLE
admin.site.site_title = base.COMPANY_NAME


# SWAGGER SCHEMA VIEW #

schema_view = get_schema_view(
    openapi.Info(
        title="Tikwey API",
        default_version='v1',
        description="Tikwey API Documentation",
        terms_of_service="https://www.entar.com/policies/terms/",
        contact=openapi.Contact(email="contact@entar.local"),
        license=openapi.License(name="Test License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)




# GENERAL URL CONFIGURATIONS #

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/',
        include([
            path('ckeditor', include('ckeditor_uploader.urls')),
            path('user/', include('core.user.urls', namespace='user')),
            path('event/', include('core.event.urls', namespace='event')),
            path('user/wallet/', include('core.wallet.urls', namespace='wallet')),
            path('order/', include('core.order.urls', namespace='order')),

            path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
        ])
    ),
]

urlpatterns += static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)

if base.CONFIG_ENVIRONMENT == "local" or base.CONFIG_ENVIRONMENT == "test":
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        path('api/endpoints/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
