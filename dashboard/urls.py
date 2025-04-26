from django.urls import path
from dashboard.views import *

app_name = 'dashboard' 

urlpatterns = [
    path('dokter/', dashboard_dokter, name='dashboard_dokter'),
    path('front-desk-officer/', dashboard_fdo, name='dashboard_fdo'),
    path('perawat/', dashboard_perawat, name='dashboard_perawat'),
    path('klien/', dashboard_klien, name='dashboard_klien'),
    path('update-password/', update_password, name='update_password'),
]
