from django.urls import path
from .views import hewan,create_hewan,update_hewan,delete_hewan,show_hewan_client

app_name = 'hewan' 

urlpatterns = [
    path('', hewan, name='hewan'),
    path('create', create_hewan, name='create-hewan'),
    path('update', update_hewan, name='update-hewan'),
    path("delete", delete_hewan, name="delete-hewan"),
    path("client/", show_hewan_client, name="client"),
]
