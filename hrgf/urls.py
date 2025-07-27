from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from hrgf import settings


def root_view(request):
    return HttpResponse(
        """<html>
          <body>
            <h1>Welcome to HRGF API</h1>
            <ul>
                <li>
                  Use the <a href='api/swagger/'>/swagger/</a> endpoint for documentation.
                </li>
                <li>
                  Or the <a href='api/redoc/'>/redoc/</a> endpoint for documentation.
                </li>
              </ul>
          </body>
        </html>"""
    )



urlpatterns = (
    [
        path("", root_view),  # root route "/"
        path("admin/", admin.site.urls),
        # Brickly URLs
        path(
            "api/users/",
            include("user.urls"),
        ),
        path(
            "api/product/",
            include("product.urls"),
        )
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

# Swagger
if settings.DEBUG:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path(
            "api/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]

