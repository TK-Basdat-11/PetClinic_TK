from django.urls import path
from manajemen_vaksin.views import *

app_name = 'vaksin' 

urlpatterns = [
    path('dokter/', vaksin_dokter, name='vaksin_dokter'),
    path('create-dokter/', create_vaksin_dokter, name='create_vaksin_dokter'),
    path('update-dokter/<uuid:kunjungan_id>/', update_vaksin_dokter, name='update_vaksin_dokter'),
    path('update-dokter/', update_vaksin_dokter, name='update_vaksin_dokter_no_id'),
    path('delete-dokter/<uuid:kunjungan_id>/', delete_vaksin_dokter, name='delete_vaksin_dokter'),
    path('delete-dokter/', delete_vaksin_dokter, name='delete_vaksin_dokter_no_id'),
    path('perawat/', vaksin_perawat, name='vaksin_perawat'),
    path('create-perawat/', create_vaksin_perawat, name='create_vaksin_perawat'),
    path('update-perawat/<str:vaccine_code>/', update_vaksin_perawat, name='update_vaksin_perawat'),
    path('update-stok/<str:vaccine_code>/', update_stok, name='update_stok'),
    path('delete-perawat/<str:vaccine_code>/', delete_vaksin_perawat, name='delete_vaksin_perawat'),
    path('delete-perawat/', delete_vaksin_perawat, name='delete_vaksin_perawat_no_id'),
    path('hewan/', vaksinasi_klien, name='vaksinasi_klien'),
]