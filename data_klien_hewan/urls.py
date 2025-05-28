from django.urls import path
from data_klien_hewan.views import *

app_name = 'listklien' 

urlpatterns = [
    path('', list_klien, name='list_klien'),
    path('detail-klien/<uuid:identitas>/', detail_klien, name='detail_klien'),
]
