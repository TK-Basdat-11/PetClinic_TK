from django.urls import path
from . import views

app_name = 'perawatan_hewan'

urlpatterns = [
    # List view is the index page
    path('', views.list_treatment, name='list_treatment'),
    
    # Treatment CRUD operations
    path('create/', views.create_treatment, name='create_treatment'),
    path('update/', views.update_treatment, name='update_treatment'),
    path('delete/', views.delete_treatment, name='delete_treatment'),
    path('rekam_medis/', views.rekam_medis, name='rekam_medis'),
    path('create_rekam_medis/', views.create_rekam_medis, name='create_rekam_medis'),
    path('update_rekam_medis/', views.update_rekam_medis, name='update_rekam_medis'),
    path('list_kunjungan/', views.list_kunjungan, name='list_kunjungan'),
    path('create_kunjungan/', views.create_kunjungan, name='create_kunjungan'),
    path('update_kunjungan/', views.update_kunjungan, name='update_kunjungan'),
    path('delete_kunjungan/', views.delete_kunjungan, name='delete_kunjungan'),
    path('rekam_medis_unavailable/', views.rekam_medis_unavailable, name='rekam_medis_unavailable'),
]