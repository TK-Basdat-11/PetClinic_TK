from django.urls import path
from manajemen_vaksin.views import vaksin_dokter, create_vaksin_dokter, update_vaksin_dokter, delete_vaksin_dokter

app_name = 'vaksin' 

urlpatterns = [
    path('dokter/', vaksin_dokter, name='vaksin_dokter'),
    path('create-dokter/', create_vaksin_dokter, name='create_vaksin_dokter'),
    path('update-dokter/', update_vaksin_dokter, name='update_vaksin_dokter'),
    path('delete-dokter/', delete_vaksin_dokter, name='delete_vaksin_dokter'),
]
