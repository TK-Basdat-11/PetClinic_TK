from django.urls import path
from .views import show_login,hero_section,user_logout,register,register_individu,register_perusahaan,register_fdo,register_dokter,register_perawat

app_name = 'authentication' 

urlpatterns = [
    path('', hero_section, name='hero'),
    path('login/', show_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
    path('register_individu/', register_individu, name='register_individu'),
    path('register_perusahaan/', register_perusahaan, name='register_perusahaan'),
    path('register_fdo/', register_fdo, name='register_fdo'),
    path('register_dokter/', register_dokter, name='register_dokter'),
    path('register_perawat/', register_perawat, name='register_perawat'),
]
