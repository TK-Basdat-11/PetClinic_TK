from django.urls import path
from dashboard.views import *

app_name = 'dashboard' 

urlpatterns = [
    path('dokter/', dashboard_dokter, name='dashboard_dokter'),
    path('front-desk-officer/', dashboard_fdo, name='dashboard_fdo'),
    path('perawat/', dashboard_perawat, name='dashboard_perawat'),
    path('klien/', dashboard_klien, name='dashboard_klien'),
    path('update-password/', update_password, name='update_password'),
    path('update-profile-dokter/', update_profile_dokter, name='update_profile_dokter'),
    path('update-profile-fdo/', update_profile_fdo, name='update_profile_fdo'),
    path('update-profile-perawat/', update_profile_perawat, name='update_profile_perawat'),
    path('update-profile-klien-individu/', update_profile_klien_individu, name='update_profile_klien_individu'),
    path('update-profile-klien-perusahaan/', update_profile_klien_perusahaan, name='update_profile_klien_perusahaan'),
]
