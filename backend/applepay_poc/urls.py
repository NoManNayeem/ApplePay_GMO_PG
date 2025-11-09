"""
URL configuration for applepay_poc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from pathlib import Path

def serve_apple_domain_association(request):
    """Serve Apple Pay domain association file"""
    well_known_path = Path(settings.BASE_DIR).parent / '.well-known'
    return serve(
        request,
        'apple-developer-merchantid-domain-association',
        document_root=str(well_known_path)
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/payments/', include('payments.urls')),
    # Apple Pay domain verification - CRITICAL for production
    path('.well-known/apple-developer-merchantid-domain-association',
         serve_apple_domain_association,
         name='apple-domain-association'),
]
