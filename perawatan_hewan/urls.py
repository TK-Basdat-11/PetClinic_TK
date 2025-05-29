from django.urls import path
from . import views

app_name = 'perawatan_hewan'

urlpatterns = [
    # List view is the index page
    path('', views.list_treatment, name='list_treatment'),
    
    # Treatment CRUD operations
    path('create/', views.create_treatment, name='create_treatment'),
    path('update/<uuid:id_kunjungan>/<str:kode_perawatan>/', views.update_treatment, name='update_treatment'),
    path('delete/<uuid:id_kunjungan>/<str:kode_perawatan>/', views.delete_treatment, name='delete_treatment'),
    path('rekam_medis/<uuid:id_kunjungan>/', views.rekam_medis, name='rekam_medis'),
    path('create_rekam_medis/<uuid:id_kunjungan>/', views.create_rekam_medis, name='create_rekam_medis'),
    path('update_rekam_medis/<uuid:id_kunjungan>/', views.update_rekam_medis, name='update_rekam_medis'),
    path('rekam_medis_unavailable/<uuid:id_kunjungan>/', views.rekam_medis_unavailable, name='rekam_medis_unavailable'),
    path('list_kunjungan/', views.list_kunjungan, name='list_kunjungan'),
    path('create_kunjungan/', views.create_kunjungan, name='create_kunjungan'),
    path('update_kunjungan/<uuid:id_kunjungan>/', views.update_kunjungan, name='update_kunjungan'),
    path('delete_kunjungan/<uuid:id_kunjungan>/', views.delete_kunjungan, name='delete_kunjungan'),
]