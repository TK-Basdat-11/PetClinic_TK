from django.urls import path
from manajemen_obat.views import (
    list_obat,
    create_obat,
    update_obat,
    update_stock,
    delete_obat,
    list_perawatan,
    create_perawatan,
    update_perawatan,
    delete_perawatan,
    list_resep,
    create_resep,
    delete_resep,
    list_resep_klien,
)

app_name = 'manajemen_obat'

urlpatterns = [
    path('', list_obat, name='list_obat'),
    path('create/', create_obat, name='create_obat'),
    path('update/<str:med_code>/', update_obat, name='update_obat'),
    path('stock/', update_stock, name='update_stock'),
    path('delete/<str:med_code>/', delete_obat, name='delete_obat'),
    path('perawatan/', list_perawatan, name='list_perawatan'),
    path('perawatan/create/', create_perawatan, name='create_perawatan'),
    path('perawatan/update/<str:treatment_code>/', update_perawatan, name='update_perawatan'),
    path('perawatan/delete/<str:treatment_code>/', delete_perawatan, name='delete_perawatan'),
    path('resep/', list_resep, name='list_resep'),
    path('resep/create/', create_resep, name='create_resep'),
    path('resep/delete/<str:treatment_code>/<str:med_code>/', delete_resep, name='delete_resep'),
    path('resep/klien/', list_resep_klien, name='list_resep_klien'),
] 