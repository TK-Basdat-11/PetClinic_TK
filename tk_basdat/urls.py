# from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('vaksin/', include('manajemen_vaksin.urls', namespace='vaksin')),
    path('listklien/', include('data_klien_hewan.urls', namespace='listklien')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('obat/', include('manajemen_obat.urls', namespace='obat')),
    path('perawatan/', include('perawatan_hewan.urls', namespace='perawatan')),
    path('hewan/', include('hewan.urls', namespace='hewan')),
    path('jenis-hewan/', include('jenis_hewan.urls', namespace='jenis-hewan')),
    path('', include('authentication.urls', namespace='authentication')),
]
