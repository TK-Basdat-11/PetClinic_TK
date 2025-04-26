# from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('vaksin/', include('manajemen_vaksin.urls', namespace='vaksin')),
    path('listklien/', include('data_klien_hewan.urls', namespace='listklien')),
]
