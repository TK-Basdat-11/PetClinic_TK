from django.urls import path
from data_klien_hewan.views import *

app_name = 'listklien' 

urlpatterns = [
    path('', list_klien, name='list_klien'),
    path('detail-perusahaan/', detail_perusahaan, name='detail_perusahaan'),
    path('detail-inidivdu/', detail_individu, name='detail_individu'),
]
