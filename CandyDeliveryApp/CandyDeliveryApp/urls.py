from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('openapi/', TemplateView.as_view(template_name='openapi.html'), name='openapi'),
    path('', include('api.urls'))
]
