from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/auth/login/',
        redirect_field_name='next'
    ), name='logout'),
    # Registro de usuarios
    path('registro/', views.registro_view, name='registro'),
    
    # URLs de prueba para debugging
    path('test/', views.test_page, name='test_page'),
    path('test-logout/', views.test_logout, name='test_logout'),
]
