from django.urls import path
from . import views

app_name = 'tecnicos'

urlpatterns = [
    path('', views.tecnico_list, name='list'),
    path('nuevo/', views.tecnico_create, name='create'),
    path('<int:pk>/', views.tecnico_detail, name='detail'),
    path('<int:pk>/editar/', views.tecnico_edit, name='edit'),
    path('<int:pk>/eliminar/', views.tecnico_delete, name='delete'),
    path('<int:tecnico_id>/vacaciones/nueva/', views.vacaciones_create, name='vacaciones_create'),
    path('vacaciones/<int:pk>/', views.vacaciones_detail, name='vacaciones_detail'),
    path('vacaciones/<int:pk>/<str:accion>/', views.vacaciones_aprobar_rechazar, name='vacaciones_accion'),
    path('<int:tecnico_id>/documentos/subir/', views.documento_upload, name='documento_upload'),
    path('documentos/<int:pk>/eliminar/', views.documento_delete, name='documento_delete'),
]
