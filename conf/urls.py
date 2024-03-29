from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from apps.account.urls import urlpatterns as account_urls
from apps.contact.urls import urlpatterns as contact_urls
from apps.food.urls import urlpatterns as food_urls
from apps.notification.urls import urlpatterns as notification_urls
from apps.order.urls import urlpatterns as order_urls
from apps.ticket.urls import urlpatterns as ticket_urls

schema_view = get_schema_view(
    openapi.Info(
        title="Kol API",
        default_version="a1",
        description="API For Kol application",
        terms_of_service="https://kl-sa-902.herokuapp.com/terms-of-service/",
        contact=openapi.Contact(email="nihan.dip@gmail.com"),
        license=openapi.License(name="Commercial"),
    ),
    public=False,
    permission_classes=(permissions.IsAdminUser,),
)

# Admin panel changes
admin.site.index_title = _("Kol")
admin.site.site_header = _("Kol Administration")
admin.site.site_title = _("Kol Management")

urlpatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("nested_admin/", include("nested_admin.urls")),
]

urlpatterns += account_urls
urlpatterns += ticket_urls
urlpatterns += contact_urls
urlpatterns += food_urls
urlpatterns += order_urls
urlpatterns += notification_urls


urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls), prefix_default_language=False
)
