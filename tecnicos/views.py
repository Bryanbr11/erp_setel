from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Tecnico, VacacionesTecnico, Especialidad, DocumentoTecnico
from .forms import TecnicoForm, VacacionesForm, DocumentoForm


@login_required
def tecnico_list(request):
    # Filtros de búsqueda
    search = request.GET.get('search', '')
    estado = request.GET.get('estado', '')
    especialidad = request.GET.get('especialidad', '')
    departamento = request.GET.get('departamento', '')

    tecnicos = Tecnico.objects.select_related(
        'usuario').prefetch_related('especialidades')

    if search:
        tecnicos = tecnicos.filter(
            usuario__first_name__icontains=search
        ) | tecnicos.filter(
            usuario__last_name__icontains=search
        ) | tecnicos.filter(
            codigo_empleado__icontains=search
        )

    if estado:
        tecnicos = tecnicos.filter(estado=estado)

    if especialidad:
        tecnicos = tecnicos.filter(especialidades__id=especialidad)

    if departamento:
        tecnicos = tecnicos.filter(departamento=departamento)

    tecnicos = tecnicos.order_by('codigo_empleado')

    # Para los filtros
    especialidades = Especialidad.objects.filter(activa=True)
    departamentos = Tecnico.DEPARTAMENTO_CHOICES
    estados = Tecnico.ESTADO_CHOICES

    # Formulario vacío para el modal
    form = TecnicoForm()

    context = {
        'tecnicos': tecnicos,
        'especialidades': especialidades,
        'departamentos': departamentos,
        'estados': estados,
        'search': search,
        'estado_selected': estado,
        'departamento_selected': departamento,
        'especialidad_selected': especialidad,
        'form': form,
    }

    return render(request, 'tecnicos/list.html', context)


@login_required
def tecnico_detail(request, pk):
    tecnico = get_object_or_404(Tecnico, pk=pk)
    documentos = tecnico.documentos.all()
    
    # Manejar filtros de búsqueda
    search_doc = request.GET.get('search_doc', '')
    tipo_doc = request.GET.get('tipo_documento', '')
    
    # Aplicar filtros si existen
    if search_doc:
        from django.db.models import Q
        documentos = documentos.filter(
            Q(nombre__icontains=search_doc) |
            Q(descripcion__icontains=search_doc) |
            Q(archivo__icontains=search_doc)
        )
    
    if tipo_doc:
        documentos = documentos.filter(tipo=tipo_doc)
    
    # Ordenar por fecha de subida (más recientes primero)
    documentos = documentos.order_by('-fecha_subida')
    
    # Obtener las últimas 5 vacaciones
    vacaciones = tecnico.vacaciones.all()[:5]

    # Inicializar el formulario de documento
    documento_form = DocumentoForm()

    # Obtener las opciones de tipo de documento del modelo
    from .models import DocumentoTecnico
    tipos_documento = DocumentoTecnico.TIPO_DOCUMENTO_CHOICES

    context = {
        'tecnico': tecnico,
        'documentos': documentos,
        'vacaciones': vacaciones,
        'form': documento_form,  # Asegurarse de que el formulario esté disponible
        'tipos_documento': tipos_documento,  # Pasar los tipos de documento al template
        'search_doc': search_doc,  # Mantener el valor de búsqueda en el input
        'tipo_doc_selected': tipo_doc,  # Mantener el tipo de documento seleccionado
    }

    # Determinar qué plantilla usar basado en si es una petición AJAX o no
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template_name = 'tecnicos/partials/detalle_tecnico.html'
    else:
        template_name = 'tecnicos/detail.html'

    return render(request, template_name, context)


@login_required
def tecnico_create(request):
    if request.method == 'POST':
        form = TecnicoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Generar nombre de usuario basado en el email si no se proporciona
                    username = form.cleaned_data.get('username')
                    if not username:
                        username = form.cleaned_data['email'].split('@')[0]

                    # Crear usuario
                    user = User.objects.create_user(
                        username=username,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        email=form.cleaned_data['email']
                    )

                    # Crear técnico
                    tecnico = form.save(commit=False)
                    tecnico.usuario = user
                    
                    # Usar el código generado automáticamente por el formulario
                    # (ya se generó en el método __init__ del formulario)

                    # Asegurarse de que el estado tenga un valor por defecto
                    if not hasattr(tecnico, 'estado') or not tecnico.estado:
                        tecnico.estado = 'activo'

                    # Guardar el técnico
                    tecnico.save()

                    # Guardar relaciones many-to-many
                    form.save_m2m()

                    # Mensaje de éxito con HTML para mejor formato
                    success_message = (
                        f'<div class="alert alert-success alert-dismissible fade show" role="alert">'
                        f'<i class="bi bi-check-circle-fill me-2"></i>'
                        f'<strong>¡Técnico creado exitosamente!</strong> {user.get_full_name()} ha sido registrado en el sistema.'
                        f'<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'
                        f'</div>'
                    )
                    messages.success(request, success_message, extra_tags='safe')
                    return redirect('tecnicos:detail', pk=tecnico.pk)

            except Exception as e:
                # Si hay un error, eliminar el usuario creado para evitar usuarios huérfanos
                if 'user' in locals():
                    user.delete()
                
                # Mensaje de error con HTML
                error_message = (
                    f'<div class="alert alert-danger alert-dismissible fade show" role="alert">'
                    f'<i class="bi bi-exclamation-triangle-fill me-2"></i>'
                    f'<strong>Error al crear el técnico:</strong> {str(e)}.'
                    f'<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'
                    f'</div>'
                )
                messages.error(request, error_message, extra_tags='safe')
        else:
            # Mostrar errores de validación del formulario con mejor formato
            error_html = (
                '<div class="alert alert-warning alert-dismissible fade show" role="alert">'
                '<i class="bi bi-exclamation-circle-fill me-2"></i>'
                '<strong>Por favor, corrige los siguientes errores:</strong>'
                '<ul class="mb-0 mt-2">'
            )
            
            for field, errors in form.errors.items():
                field_name = form.fields[field].label if field in form.fields else field
                for error in errors:
                    error_html += f'<li><strong>{field_name}:</strong> {error}</li>'
            
            error_html += (
                '</ul>'
                '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'
                '</div>'
            )
            messages.error(request, error_html, extra_tags='safe')
    else:
        form = TecnicoForm(initial={
            'estado': 'activo',
            'fecha_ingreso': timezone.now().date()
        })

    return render(request, 'tecnicos/form.html', {
        'form': form,
        'title': 'Nuevo Técnico',
        'action': 'Crear'
    })


@login_required
def tecnico_edit(request, pk):
    tecnico = get_object_or_404(Tecnico, pk=pk)
    
    # Si es una petición AJAX, devolvemos solo el formulario
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = TecnicoForm(request.POST, request.FILES, instance=tecnico)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Actualizar usuario
                    user = tecnico.usuario
                    user.first_name = form.cleaned_data['first_name']
                    user.last_name = form.cleaned_data['last_name']
                    user.email = form.cleaned_data['email']
                    user.save()

                    # Actualizar técnico
                    tecnico = form.save()
                    
                    if is_ajax:
                        # Obtener los datos actualizados del técnico
                        from django.template.loader import render_to_string
                        
                        # Obtener los nombres para mostrar de las opciones
                        departamento_display = dict(Tecnico.DEPARTAMENTO_CHOICES).get(
                            tecnico.departamento, tecnico.departamento
                        )
                        estado_display = dict(Tecnico.ESTADO_CHOICES).get(
                            tecnico.estado, tecnico.estado
                        )
                        
                        # Formatear fechas para mostrarlas correctamente
                        from django.utils import formats
                        
                        fecha_nacimiento = ''
                        if tecnico.fecha_nacimiento:
                            # Usar el formato de fecha de Django directamente
                            fecha_nacimiento = tecnico.fecha_nacimiento.strftime('%d/%m/%Y')
                        
                        # Crear el diccionario de respuesta con todos los datos
                        # Crear un diccionario seguro para JSON con los datos del formulario
                        form_data = {}
                        for key, value in form.cleaned_data.items():
                            # Convertir a string los valores que no son serializables
                            if hasattr(value, '_meta'):
                                # Para modelos, obtener el ID o representación en string
                                form_data[key] = str(value)
                            elif hasattr(value, 'all'):  # Para QuerySets
                                form_data[key] = [str(item) for item in value.all()]
                            else:
                                form_data[key] = value
                        
                        # Crear el diccionario de respuesta
                        response_data = {
                            'success': True,
                            'message': 'Los cambios se han guardado correctamente.',
                            'tecnico_id': tecnico.id,
                            'nombre_completo': f"{tecnico.usuario.first_name} {tecnico.usuario.last_name}".strip(),
                            'first_name': tecnico.usuario.first_name,
                            'last_name': tecnico.usuario.last_name,
                            'email': tecnico.usuario.email,
                            'telefono': str(tecnico.telefono) if tecnico.telefono else '',
                            'telefono_emergencia': str(tecnico.telefono_emergencia) if tecnico.telefono_emergencia else '',
                            'rut': tecnico.rut if tecnico.rut else '',
                            'fecha_nacimiento': fecha_nacimiento,
                            'direccion': tecnico.direccion if tecnico.direccion else '',
                            'codigo_empleado': tecnico.codigo_empleado if tecnico.codigo_empleado else '',
                            'departamento': tecnico.departamento,
                            'departamento_display': departamento_display,
                            'estado': tecnico.estado,
                            'estado_display': estado_display,
                            'debug': {
                                'is_ajax': is_ajax,
                                'request_method': request.method,
                                'content_type': request.content_type,
                                'form_fields': list(form.cleaned_data.keys())  # Solo los nombres de los campos
                            }
                        }
                        
                        # Agregar la URL de la foto si existe
                        if tecnico.foto:
                            response_data['foto_url'] = tecnico.foto.url
                        
                        return JsonResponse(response_data, status=200)
                    else:
                        messages.success(request, 
                            f'<div class="alert alert-success alert-dismissible fade show" role="alert">'
                            f'<i class="bi bi-check-circle-fill me-2"></i>'
                            f'<strong>¡Cambios guardados!</strong> La información de {tecnico.nombre_completo} ha sido actualizada correctamente.'
                            f'<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'
                            f'</div>',
                            extra_tags='safe'
                        )
                        return redirect('tecnicos:detail', pk=tecnico.pk)
                        
            except Exception as e:
                error_msg = f'Error al actualizar: {str(e)}.'
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': error_msg
                    }, status=400)
                else:
                    messages.error(request, 
                        f'<div class="alert alert-danger alert-dismissible fade show" role="alert">'
                        f'<i class="bi bi-exclamation-triangle-fill me-2"></i>'
                        f'<strong>{error_msg}</strong>'
                        f'<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'
                        f'</div>',
                        extra_tags='safe'
                    )
        else:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor, corrija los errores del formulario.',
                    'errors': form.errors
                }, status=400)
    else:
        # Inicializar formulario con datos del usuario
        initial_data = {
            'first_name': tecnico.usuario.first_name,
            'last_name': tecnico.usuario.last_name,
            'email': tecnico.usuario.email,
        }

        # Si hay fechas en la instancia, formatearlas correctamente
        if tecnico.fecha_nacimiento:
            initial_data['fecha_nacimiento'] = tecnico.fecha_nacimiento
        if tecnico.fecha_ingreso:
            initial_data['fecha_ingreso'] = tecnico.fecha_ingreso

        form = TecnicoForm(instance=tecnico, initial=initial_data)
        
        # Si es AJAX, devolver solo el formulario
        if is_ajax:
            return render(request, 'tecnicos/partials/tecnico_form_modal.html', {
                'form': form,
                'tecnico': tecnico,
                'action_url': reverse('tecnicos:edit', args=[tecnico.id])
            })

    return render(request, 'tecnicos/form.html', {
        'form': form,
        'tecnico': tecnico,
        'title': f'Editar Técnico - {tecnico.nombre_completo}',
        'action': 'Actualizar'
    })


@login_required
def vacaciones_aprobar_rechazar(request, pk, accion):
    vacacion = get_object_or_404(VacacionesTecnico, pk=pk)

    if vacacion.estado != 'pendiente':
        messages.warning(
            request, 'Esta solicitud ya ha sido procesada anteriormente.')
        return redirect('tecnicos:vacaciones_detail', pk=vacacion.pk)

    if accion == 'aprobar':
        vacacion.estado = 'aprobada'
        mensaje = 'Solicitud de vacaciones aprobada exitosamente.'
    elif accion == 'rechazar':
        vacacion.estado = 'rechazada'
        mensaje = 'Solicitud de vacaciones rechazada.'
    else:
        messages.error(request, 'Acción no válida.')
        return redirect('tecnicos:vacaciones_detail', pk=vacacion.pk)

    vacacion.aprobado_por = request.user
    vacacion.fecha_aprobacion = timezone.now()
    vacacion.save()

    messages.success(request, mensaje)
    return redirect('tecnicos:vacaciones_detail', pk=vacacion.pk)


@login_required
def vacaciones_detail(request, pk):
    vacacion = get_object_or_404(VacacionesTecnico, pk=pk)
    return render(request, 'tecnicos/vacaciones_detail.html', {'vacacion': vacacion})


@login_required
def vacaciones_create(request, tecnico_id):
    tecnico = get_object_or_404(Tecnico, pk=tecnico_id)

    if request.method == 'POST':
        form = VacacionesForm(request.POST)
        if form.is_valid():
            vacacion = form.save(commit=False)
            vacacion.tecnico = tecnico
            vacacion.save()

            messages.success(
                request, 'Solicitud de vacaciones creada exitosamente.')
            return redirect('tecnicos:detail', pk=tecnico.pk)
    else:
        form = VacacionesForm()

    return render(request, 'tecnicos/vacaciones_form.html', {
        'form': form,
        'tecnico': tecnico,
        'title': f'Nueva Solicitud de Vacaciones - {tecnico.nombre_completo}'
    })


@login_required
def tecnico_delete(request, pk):
    tecnico = get_object_or_404(Tecnico, pk=pk)

    if request.method == 'POST':
        try:
            # Eliminar el usuario asociado
            usuario = tecnico.usuario
            nombre_completo = tecnico.nombre_completo

            with transaction.atomic():
                # Primero eliminamos el técnico
                tecnico.delete()
                # Luego eliminamos el usuario
                usuario.delete()

            messages.success(
                request, f'Técnico {nombre_completo} eliminado correctamente.')
            return redirect('tecnicos:list')

        except Exception as e:
            messages.error(request, f'Error al eliminar el técnico: {str(e)}')
            return redirect('tecnicos:detail', pk=pk)

    # Si no es una petición POST, mostrar confirmación
    return render(request, 'tecnicos/delete_confirm.html', {
        'tecnico': tecnico,
        'title': f'Eliminar Técnico - {tecnico.nombre_completo}'
    })


@login_required
def documento_delete(request, pk):
    documento = get_object_or_404(DocumentoTecnico, pk=pk)
    tecnico_id = documento.tecnico.id

    if request.method == 'POST':
        try:
            documento.archivo.delete()  # Elimina el archivo físico
            documento.delete()  # Elimina el registro de la base de datos
            messages.success(request, 'Documento eliminado correctamente.')
            return redirect('tecnicos:detail', pk=tecnico_id)
        except Exception as e:
            messages.error(
                request, f'Error al eliminar el documento: {str(e)}')
            return redirect('tecnicos:detail', pk=tecnico_id)

    return redirect('tecnicos:detail', pk=tecnico_id)


@login_required
def documento_upload(request, tecnico_id):
    tecnico = get_object_or_404(Tecnico, pk=tecnico_id)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                documento = form.save(commit=False)
                documento.tecnico = tecnico
                documento.save()

                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'documento': {
                            'id': documento.id,
                            'nombre': documento.nombre,
                            'url': documento.archivo.url,
                            'fecha_subida': documento.fecha_subida.strftime('%d/%m/%Y %H:%M')
                        }
                    })

                messages.success(request, 'Documento subido exitosamente.')
                return redirect('tecnicos:detail', pk=tecnico.pk)

            except Exception as e:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    }, status=400)
                messages.error(
                    request, f'Error al subir el documento: {str(e)}')
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    }, status=400)
    else:
        form = DocumentoForm()

    # Si es una petición AJAX pero hubo un error en el formulario
    if is_ajax:
        return JsonResponse({
            'success': False,
            'error': 'Formulario inválido',
            'errors': form.errors if form.errors else 'Error desconocido al procesar el formulario'
        }, status=400)

    # Si no es AJAX, renderizar el modal con el formulario
    return render(request, 'tecnicos/partials/documento_upload.html', {
        'form': form,
        'tecnico': tecnico
    })
