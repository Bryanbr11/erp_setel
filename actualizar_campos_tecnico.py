import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_system.settings')
django.setup()

def actualizar_campos_tecnico():
    from tecnicos.models import Tecnico
    from django.db import connection
    
    # Actualizar los registros donde usuario no es nulo
    tecnicos_actualizados = 0
    
    with connection.cursor() as cursor:
        # Consulta para actualizar los campos
        cursor.execute("""
            UPDATE tecnicos_tecnico t
            INNER JOIN auth_user u ON t.usuario_id = u.id
            SET 
                t.nombre = u.first_name,
                t.apellido = u.last_name,
                t.email = u.email
            WHERE 
                t.usuario_id IS NOT NULL
                AND (t.nombre IS NULL OR t.nombre = '' 
                     OR t.apellido IS NULL OR t.apellido = '' 
                     OR t.email IS NULL OR t.email = '')
        """)
        tecnicos_actualizados = cursor.rowcount
    
    return tecnicos_actualizados

if __name__ == "__main__":
    print("Actualizando campos de técnicos...")
    actualizados = actualizar_campos_tecnico()
    print(f"Se actualizaron {actualizados} registros.")
    
    # Mostrar los primeros 5 registros para verificar
    from tecnicos.models import Tecnico
    print("\nPrimeros 5 técnicos:")
    print("-" * 80)
    print(f"{'ID':<5} {'Nombre':<20} {'Apellido':<20} {'Email':<30} {'Usuario'}")
    print("-" * 80)
    
    for t in Tecnico.objects.all()[:5]:
        print(f"{t.id:<5} {t.nombre or 'N/A':<20} {t.apellido or 'N/A':<20} {t.email or 'N/A':<30} {t.usuario.username if t.usuario else 'Ninguno'}")
