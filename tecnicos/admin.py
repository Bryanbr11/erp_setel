from django.contrib import admin
from .models import Especialidad, Tecnico, DocumentoTecnico, VacacionesTecnico

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre']

class DocumentoTecnicoInline(admin.TabularInline):
    model = DocumentoTecnico
    extra = 0

class VacacionesTecnicoInline(admin.TabularInline):
    model = VacacionesTecnico
    extra = 0

@admin.register(Tecnico)
class TecnicoAdmin(admin.ModelAdmin):
    list_display = ['codigo_empleado', 'nombre_completo', 'estado', 'fecha_ingreso']
    list_filter = ['estado', 'especialidades', 'fecha_ingreso']
    search_fields = ['codigo_empleado', 'usuario__first_name', 'usuario__last_name', 'usuario__username']
    filter_horizontal = ['especialidades']
    inlines = [DocumentoTecnicoInline, VacacionesTecnicoInline]
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('usuario', 'codigo_empleado', 'telefono', 'direccion', 'fecha_nacimiento')
        }),
        ('Información Laboral', {
            'fields': ('fecha_ingreso', 'estado', 'especialidades')
        }),
        ('Adicional', {
            'fields': ('foto', 'observaciones')
        }),
    )

@admin.register(DocumentoTecnico)
class DocumentoTecnicoAdmin(admin.ModelAdmin):
    list_display = ['tecnico', 'tipo', 'nombre', 'fecha_subida']
    list_filter = ['tipo', 'fecha_subida']
    search_fields = ['tecnico__codigo_empleado', 'nombre']

@admin.register(VacacionesTecnico)
class VacacionesTecnicoAdmin(admin.ModelAdmin):
    list_display = ['tecnico', 'fecha_inicio', 'fecha_fin', 'dias_solicitados', 'estado']
    list_filter = ['estado', 'fecha_inicio']
    search_fields = ['tecnico__codigo_empleado']
    readonly_fields = ['duracion_dias']
