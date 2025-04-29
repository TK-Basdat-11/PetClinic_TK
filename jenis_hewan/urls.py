from django.urls import path
from .views import jenis_hewan

app_name = 'jenis_hewan' 

urlpatterns = [
    path('', jenis_hewan, name='jenis-hewan'),
    
]
