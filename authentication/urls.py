from django.urls import path
from .views import show_login,hero_section,user_logout

app_name = 'authentication' 

urlpatterns = [
    path('', hero_section, name='hero'),
    path('login/', show_login, name='login'),
    path('logout/', user_logout, name='logout'),
]
