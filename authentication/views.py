from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import RegistroForm

@login_required
def test_logout(request):
    """Página de prueba para verificar logout"""
    return HttpResponse("Test logout page - Usuario autenticado: " + str(request.user.is_authenticated))

def test_page(request):
    """Página de prueba simple"""
    return HttpResponse("Test page - Servidor funcionando correctamente")

@require_http_methods(["POST"])
def registro_view(request):
    """Vista para el registro de nuevos usuarios"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciar sesión automáticamente después del registro
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': '¡Registro exitoso! Redirigiendo...',
                'redirect_url': '/dashboard/'
            })
        else:
            # Devolver errores de validación
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = field_errors
            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': 'Por favor, corrige los errores en el formulario.'
            }, status=400)
    
    # Si no es una petición AJAX, redirigir a la página de inicio
    return redirect('dashboard:index')
