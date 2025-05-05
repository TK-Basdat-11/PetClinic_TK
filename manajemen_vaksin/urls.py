from django.urls import path
from manajemen_vaksin.views import *

app_name = 'vaksin' 

urlpatterns = [
    path('dokter/', vaksin_dokter, name='vaksin_dokter'),
    path('create-dokter/', create_vaksin_dokter, name='create_vaksin_dokter'),
    path('update-dokter/', update_vaksin_dokter, name='update_vaksin_dokter'),
    path('delete-dokter/', delete_vaksin_dokter, name='delete_vaksin_dokter'),
    path('perawat/', vaksin_perawat, name='vaksin_perawat'),
    path('create-perawat/', create_vaksin_perawat, name='create_vaksin_perawat'),
    path('update-perawat/<str:vaccine_code>', update_vaksin_perawat, name='update_vaksin_perawat'),
    path('update-stok/}', update_stok, name='update_stok'),
    path('delete-perawat/', delete_vaksin_perawat, name='delete_vaksin_perawat'),
]
