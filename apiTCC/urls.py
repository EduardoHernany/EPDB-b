from django.urls import path, re_path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
   openapi.Info(
      title="API de Docking Molecular",
      default_version='v1',
      description="API para automatização de processos de docking molecular usando AutoDock GPU",
      terms_of_service="https://www.seusite.com/policies/terms/",
      contact=openapi.Contact(email="seuemail@seusite.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Incluir URLs da aplicação
    path('api/', include('epdb.urls')),

    # URLs do Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
