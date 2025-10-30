from django import forms
from django.contrib.auth.models import User
from .models import Tecnico, VacacionesTecnico, DocumentoTecnico, Especialidad


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%d')
        super().__init__(**kwargs)


class TecnicoForm(forms.ModelForm):
    # Campos del usuario
    first_name = forms.CharField(
        max_length=150,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    # Campo fecha_nacimiento con widget personalizado
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_fecha_nacimiento'
            }
        ),
        input_formats=['%Y-%m-%d']
    )
    fecha_ingreso = forms.DateField(
        label='Fecha de Ingreso',
        required=False,
        widget=DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_fecha_ingreso'
            },
            format='%Y-%m-%d'
        )
    )

    class Meta:
        model = Tecnico
        fields = [
            'codigo_empleado', 'rut', 'fecha_nacimiento', 'ubicacion', 'departamento',
            'puesto', 'fecha_ingreso', 'telefono', 'direccion', 'telefono_emergencia',
            'nombre_emergencia', 'linkedin', 'prevision', 'afp',
            'estado', 'especialidades', 'foto', 'postre_favorito', 'observaciones'
        ]

        widgets = {
            'codigo_empleado': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
            'fecha_nacimiento': DateInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'departamento': forms.Select(attrs={'class': 'form-select'}),
            'puesto': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': DateInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telefono_emergencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'nombre_emergencia': forms.TextInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/usuario'}),
            'prevision': forms.Select(attrs={'class': 'form-select'}),
            'afp': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'especialidades': forms.CheckboxSelectMultiple(),
            'foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'postre_favorito': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

        labels = {
            'codigo_empleado': 'Código de Empleado',
            'rut': 'RUT',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'ubicacion': 'Ubicación',
            'departamento': 'Departamento',
            'puesto': 'Puesto',
            'fecha_ingreso': 'Fecha de Ingreso',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'telefono_emergencia': 'Teléfono de Emergencia',
            'nombre_emergencia': 'Contacto de Emergencia',
            'linkedin': 'LinkedIn',
            'prevision': 'Previsión',
            'afp': 'AFP',
            'estado': 'Estado',
            'especialidades': 'Especialidades',
            'foto': 'Foto de Perfil',
            'postre_favorito': 'Postre Favorito',
            'observaciones': 'Observaciones',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['especialidades'].queryset = Especialidad.objects.filter(
            activa=True)
            
        # Asegurarse de que el campo departamento tenga todas las opciones
        from .models import Tecnico
        
        # Obtener las opciones directamente del modelo
        departamento_choices = [('', '---------')] + list(Tecnico.DEPARTAMENTO_CHOICES)
        
        # Actualizar las opciones del campo departamento
        self.fields['departamento'].widget.choices = departamento_choices
        self.fields['departamento'].choices = departamento_choices
        
        # Establecer un valor por defecto si no hay ninguno
        if not self.initial.get('departamento'):
            self.initial['departamento'] = 'operaciones'  # Valor por defecto
            
        # Forzar la actualización del widget
        self.fields['departamento'].widget.attrs.update({'class': 'form-select'})
        
        # Si es un nuevo registro, generar automáticamente el código de empleado
        if not self.instance.pk:
            # Obtener el último código de empleado
            from django.db.models import Max
            ultimo_tecnico = Tecnico.objects.order_by('-id').first()
            
            if ultimo_tecnico and ultimo_tecnico.codigo_empleado and ultimo_tecnico.codigo_empleado.startswith('SE'):
                try:
                    # Extraer la parte numérica del último código
                    ultimo_numero = int(ultimo_tecnico.codigo_empleado[2:])
                    nuevo_numero = ultimo_numero + 1
                except (ValueError, IndexError):
                    # En caso de error, empezar desde 1000
                    nuevo_numero = 1000
            else:
                # Si no hay códigos o el formato no es el esperado, empezar desde 1000
                nuevo_numero = 1000
                
            # Formatear el código con 'SE' al principio y ceros a la izquierda (ej: SE1000, SE1001, etc.)
            self.initial['codigo_empleado'] = f"SE{nuevo_numero:04d}"
            
        # Hacer el campo de solo lectura
        self.fields['codigo_empleado'].widget.attrs.update({
            'readonly': 'readonly',
            'class': 'form-control bg-light'  # Fondo gris para indicar que es de solo lectura
        })

        # Si estamos editando, llenar los campos del usuario
        if self.instance and self.instance.pk:
            if hasattr(self.instance, 'usuario'):
                self.fields['first_name'].initial = self.instance.usuario.first_name
                self.fields['last_name'].initial = self.instance.usuario.last_name
                self.fields['email'].initial = self.instance.usuario.email

            # Asegurarse de que las fechas se muestren en el formato correcto
            if self.instance.fecha_nacimiento:
                # Usar el formato ISO para el valor inicial
                self.initial['fecha_nacimiento'] = self.instance.fecha_nacimiento.isoformat()

            if self.instance.fecha_ingreso:
                # Usar el formato ISO para el valor inicial
                self.initial['fecha_ingreso'] = self.instance.fecha_ingreso.isoformat()
    
    def save(self, commit=True):
        # Primero, guardar el técnico
        tecnico = super().save(commit=commit)
        
        # Obtener los datos del formulario
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')
        
        # Actualizar o crear el usuario
        if hasattr(tecnico, 'usuario') and tecnico.usuario:
            # Actualizar usuario existente
            usuario = tecnico.usuario
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.email = email
            usuario.username = email  # Usar el email como nombre de usuario
            usuario.save()
        else:
            # Crear nuevo usuario
            username = email.split('@')[0] if email else f'user_{tecnico.codigo_empleado}'
            # Asegurarse de que el nombre de usuario sea único
            username_base = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}_{counter}"
                counter += 1
            
            usuario = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='temporal123'  # Contraseña temporal que el usuario deberá cambiar
            )
            tecnico.usuario = usuario
            tecnico.save()
        
        # Actualizar los campos en el modelo Tecnico
        tecnico.nombre = first_name
        tecnico.apellido = last_name
        tecnico.email = email
        
        # Guardar los cambios en el técnico
        if commit:
            tecnico.save()
        
        return tecnico


class VacacionesForm(forms.ModelForm):
    class Meta:
        model = VacacionesTecnico
        fields = ['fecha_inicio', 'fecha_fin', 'dias_solicitados', 'motivo']

        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dias_solicitados': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'dias_solicitados': 'Días Solicitados',
            'motivo': 'Motivo',
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de fin debe ser posterior a la fecha de inicio.')

            # Calcular días automáticamente
            dias_calculados = (fecha_fin - fecha_inicio).days + 1
            cleaned_data['dias_solicitados'] = dias_calculados

        return cleaned_data


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = DocumentoTecnico
        fields = ['tipo', 'nombre', 'archivo', 'descripcion']

        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

        labels = {
            'tipo': 'Tipo de Documento',
            'nombre': 'Nombre del Documento',
            'archivo': 'Archivo',
            'descripcion': 'Descripción',
        }


class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ['nombre', 'descripcion', 'activa']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'nombre': 'Nombre de la Especialidad',
            'descripcion': 'Descripción',
            'activa': 'Activa',
        }
