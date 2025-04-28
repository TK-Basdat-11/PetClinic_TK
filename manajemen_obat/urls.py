from django.urls import path
from manajemen_obat.views import (
    list_medicine,
    create_medicine,
    update_medicine,
    update_stock,
    delete_medicine,
    list_treatment,
    create_treatment,
    update_treatment,
    delete_treatment,
    list_prescriptions,
    create_prescription,
    delete_prescription,
    demo_view,
)

app_name = 'manajemen_obat'

urlpatterns = [
    path('', list_medicine, name='list_medicine'),
    path('create/', create_medicine, name='create_medicine'),
    path('update/<str:med_code>/', update_medicine, name='update_medicine'),
    path('stock/', update_stock, name='update_stock'),
    path('delete/<str:med_code>/', delete_medicine, name='delete_medicine'),
    path('treatment/', list_treatment, name='list_treatment'),
    path('treatment/create/', create_treatment, name='create_treatment'),
    path('treatment/update/<str:treatment_code>/', update_treatment, name='update_treatment'),
    path('treatment/delete/<str:treatment_code>/', delete_treatment, name='delete_treatment'),
    path('prescription/', list_prescriptions, name='list_prescriptions'),
    path('prescription/create/', create_prescription, name='create_prescription'),
    path('prescription/delete/<str:treatment_code>/<str:med_code>/', delete_prescription, name='delete_prescription'),
    path('demo/', demo_view, name='demo_view'),
] 