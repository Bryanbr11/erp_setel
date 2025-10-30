from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Tecnico(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('vacaciones', 'En Vacaciones'),
        ('licencia', 'En Licencia'),
        ('prueba', 'Período de Prueba'),
    ]
    
    UBICACION_CHOICES = [
        ('santiago', 'Santiago'),
        ('valparaiso', 'Valparaíso'),
        ('concepcion', 'Concepción'),
        ('antofagasta', 'Antofagasta'),
        ('temuco', 'Temuco'),
        ('iquique', 'Iquique'),
        ('rancagua', 'Rancagua'),
        ('talca', 'Talca'),
        ('osorno', 'Osorno'),
        ('puerto_montt', 'Puerto Montt'),
        ('punta_arenas', 'Punta Arenas'),
        ('arica', 'Arica'),
    ]
    
    DEPARTAMENTO_CHOICES = [
        ('administracion', 'Administración'),
        ('ventas', 'Ventas'),
        ('operaciones', 'Operaciones'),
        ('soporte', 'Soporte Técnico'),
        ('marketing', 'Marketing'),
        ('rrhh', 'Recursos Humanos'),
        ('finanzas', 'Finanzas'),
        ('logistica', 'Logística'),
        ('ti', 'Tecnologías de la Información'),
        ('calidad', 'Aseguramiento de Calidad'),
    ]
    
    PREVISION_CHOICES = [
        ('fonasa', 'FONASA'),
        ('isapre_banmedica', 'Isapre Banmédica'),
        ('isapre_colmena', 'Isapre Colmena'),
        ('isapre_consalud', 'Isapre Consalud'),
        ('isapre_cruz_blanca', 'Isapre Cruz Blanca'),
        ('isapre_vida_tres', 'Isapre Vida Tres'),
    ]
    
    AFP_CHOICES = [
        ('afp_capital', 'AFP Capital'),
        ('afp_provida', 'AFP Provida'),
        ('afp_habitat', 'AFP Habitat'),
        ('afp_planvital', 'AFP PlanVital'),
        ('afp_cuprum', 'AFP Cuprum'),
        ('afp_modelo', 'AFP Modelo'),
        ('afp_uno', 'AFP Uno'),
    ]
    
    # Información personal
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario del sistema', null=True, blank=True)
    codigo_empleado = models.CharField('Código de Empleado', max_length=20, unique=True, 
                                     help_text='Código único de identificación del empleado')
    rut = models.CharField('RUT', max_length=12, unique=True, 
                          help_text='Formato: 12345678-9')
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    
    # Campos de nombre y correo (duplicados del modelo User para tenerlos en la misma tabla)
    nombre = models.CharField('Nombres', max_length=30, blank=True)
    apellido = models.CharField('Apellidos', max_length=30, blank=True)
    email = models.EmailField('Correo Electrónico', blank=True)
    
    # Ubicación y departamento
    ubicacion = models.CharField('Ubicación', max_length=20, choices=UBICACION_CHOICES, 
                                default='santiago')
    departamento = models.CharField('Departamento', max_length=20, 
                                   choices=DEPARTAMENTO_CHOICES, default='operaciones')
    puesto = models.CharField('Puesto', max_length=100, blank=True, 
                            help_text='Cargo que desempeña el empleado')
    fecha_ingreso = models.DateField('Fecha de Ingreso', default=timezone.now)
    
    # Información de contacto
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    direccion = models.TextField('Dirección', blank=True)
    telefono_emergencia = models.CharField('Teléfono de Emergencia', max_length=20, blank=True)
    nombre_emergencia = models.CharField('Nombre de Contacto de Emergencia', max_length=100, blank=True)
    email_personal = models.EmailField('Correo Personal', blank=True, 
                                     help_text='Correo electrónico personal del empleado')
    linkedin = models.URLField('Perfil de LinkedIn', blank=True)
    
    # Información laboral
    prevision = models.CharField('Previsión', max_length=30, choices=PREVISION_CHOICES, 
                                default='fonasa')
    afp = models.CharField('AFP', max_length=30, choices=AFP_CHOICES, 
                          default='afp_capital')
    dias_vacaciones_anuales = models.PositiveIntegerField('Días de vacaciones anuales', default=15)
    
    # Información adicional
    foto_perfil = models.ImageField('Foto de Perfil', upload_to='tecnicos/fotos/', 
                                  blank=True, null=True,
                                  help_text='Foto del empleado para su perfil')
    postre_favorito = models.CharField('Postre Favorito', max_length=100, blank=True)
    observaciones = models.TextField('Observaciones', blank=True)
    activo = models.BooleanField('Activo', default=True,
                               help_text='Indica si el empleado está actualmente activo en la empresa')
    
    # Auditoría
    creado_el = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    actualizado_el = models.DateTimeField('Última Actualización', auto_now=True)
    
    @property
    def dias_vacaciones_disponibles(self):
        """
        Calcula los días de vacaciones disponibles para el año actual
        """
        from django.utils import timezone
        from django.db.models import Sum, Q
        
        # Obtener el año actual
        year = timezone.now().year
        
        # Obtener el total de días usados en el año actual (solo vacaciones aprobadas o en curso)
        dias_usados = self.vacaciones.filter(
            Q(estado='aprobada') | Q(estado='en_curso'),
            fecha_inicio__year=year
        ).aggregate(
            total=Sum('dias_solicitados')
        )['total'] or 0
        
        # Calcular días restantes
        dias_restantes = self.dias_vacaciones_anuales - dias_usados
        
        # Asegurar que no sea negativo
        return max(0, dias_restantes)
    
    # Estado y especialidades
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    especialidades = models.ManyToManyField(Especialidad, blank=True)
    
    # Información adicional
    foto = models.ImageField(upload_to='tecnicos/fotos/', null=True, blank=True)
    postre_favorito = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['usuario__last_name', 'usuario__first_name']
        permissions = [
            ('view_empleados', 'Puede ver el listado de empleados'),
            ('export_empleados', 'Puede exportar datos de empleados'),
        ]
    
    @property
    def nombre_completo(self):
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        elif self.usuario:
            return self.usuario.get_full_name()
        return "Sin nombre"
        
    def __str__(self):
        nombre = self.nombre_completo
        if not nombre or nombre == ' ':
            nombre = f"Usuario {self.codigo_empleado}"
        return f"{nombre} ({self.rut or 'Sin RUT'})"
        
    def get_edad(self):
        """Calcula la edad del empleado basado en su fecha de nacimiento."""
        if not self.fecha_nacimiento:
            return 0
        today = timezone.now().date()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    @property
    def antiguedad(self):
        """Calcula la antigüedad del empleado en años."""
        if not self.fecha_ingreso:
            return 0
        today = timezone.now().date()
        return today.year - self.fecha_ingreso.year - (
            (today.month, today.day) < (self.fecha_ingreso.month, self.fecha_ingreso.day)
        )
        
    def save(self, *args, **kwargs):
        # Sincronizar con el usuario si existe
        if self.usuario:
            if not self.usuario.username:
                self.usuario.username = self.email or f"user_{self.codigo_empleado}"
            if not self.usuario.email:
                self.usuario.email = self.email
            if not self.usuario.first_name:
                self.usuario.first_name = self.nombre
            if not self.usuario.last_name:
                self.usuario.last_name = self.apellido
            self.usuario.set_unusable_password()  # Requerirá que el usuario establezca una contraseña
            self.usuario.save()
        
        # Si no hay usuario, intentar crearlo
        elif not self.usuario and self.email:
            username = self.email.split('@')[0]
            # Verificar si el username ya existe
            if User.objects.filter(username=username).exists():
                username = f"{username}_{self.codigo_empleado}"
            
            user = User.objects.create_user(
                username=username,
                email=self.email,
                first_name=self.nombre,
                last_name=self.apellido,
                password='temporal123'  # Contraseña temporal que el usuario deberá cambiar
            )
            user.set_unusable_password()
            user.save()
            self.usuario = user
        
        super().save(*args, **kwargs)


class DocumentoTecnico(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('cv', 'Curriculum Vitae'),
        ('contrato', 'Contrato'),
        ('anexo', 'Anexos'),
        ('certificado_vacaciones', 'Certificado de Vacaciones'),
        ('liquidacion_sueldo', 'Liquidación de Sueldo'),
        ('carta_amonestacion', 'Carta de Amonestación'),
        ('informe', 'Informes'),
        ('finiquito', 'Finiquito'),
        ('identificacion', 'Identificación'),
        ('otro', 'Otro'),
    ]
    
    tecnico = models.ForeignKey('Tecnico', on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=25, choices=TIPO_DOCUMENTO_CHOICES)
    nombre = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='tecnicos/documentos/')
    descripcion = models.TextField(blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Documento de Técnico"
        verbose_name_plural = "Documentos de Técnicos"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.tecnico.codigo_empleado} - {self.nombre}"

class VacacionesTecnico(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('en_curso', 'En Curso'),
        ('finalizada', 'Finalizada'),
    ]
    
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE, related_name='vacaciones')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_solicitados = models.PositiveIntegerField()
    motivo = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Aprobación
    aprobado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vacaciones_aprobadas')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    comentarios_aprobacion = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Vacaciones de Técnico"
        verbose_name_plural = "Vacaciones de Técnicos"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Vacaciones de {self.tecnico.nombre_completo} - {self.fecha_inicio} al {self.fecha_fin} ({self.estado})"
        
    def save(self, *args, **kwargs):
        # Asegurarse de que los campos de fecha tengan los atributos necesarios
        if not hasattr(self, 'fecha_inicio') or not hasattr(self, 'fecha_fin'):
            raise ValueError("Las fechas de inicio y fin son requeridas")
        super().save(*args, **kwargs)
    
    @property
    def duracion_dias(self):
        return (self.fecha_fin - self.fecha_inicio).days + 1
        
    def get_dias_restantes(self):
        """
        Calcula los días de vacaciones restantes para el año actual
        """
        from django.utils import timezone
        from django.db.models import Sum
        
        # Obtener el año actual
        year = timezone.now().year
        
        # Obtener el total de días usados en el año actual (solo vacaciones aprobadas)
        dias_usados = self.tecnico.vacaciones.filter(
            estado__in=['aprobada', 'en_curso', 'finalizada'],
            fecha_inicio__year=year
        ).exclude(pk=self.pk).aggregate(
            total=Sum('dias_solicitados')
        )['total'] or 0
        
        # Calcular días restantes
        dias_restantes = self.tecnico.dias_vacaciones_anuales - dias_usados
        
        # Asegurar que no sea negativo
        return max(0, dias_restantes)


# La clase Empleado ha sido eliminada y sus campos se han integrado en el modelo Tecnico
