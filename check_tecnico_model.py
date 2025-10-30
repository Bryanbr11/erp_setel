import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_system.settings')
django.setup()

def check_tecnico_model():
    from tecnicos.models import Tecnico
    from django.db import connection
    
    # Obtener los campos del modelo
    campos_modelo = [f.name for f in Tecnico._meta.get_fields() 
                    if hasattr(f, 'column')]  # Solo campos de base de datos
    
    # Obtener los campos de la tabla directamente de la base de datos
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'tecnicos_tecnico'
        """)
        campos_tabla = [row[0] for row in cursor.fetchall()]
    
    # Mostrar los campos del modelo
    print("\nCampos en el modelo Tecnico:")
    print("-" * 50)
    for campo in sorted(campos_modelo):
        print(f"- {campo}")
    
    # Mostrar los campos en la tabla
    print("\nCampos en la tabla tecnicos_tecnico:")
    print("-" * 50)
    for campo in sorted(campos_tabla):
        print(f"- {campo}")
    
    # Verificar campos importantes
    print("\nVerificación de campos importantes:")
    print("-" * 50)
    campos_importantes = ['nombre', 'apellido', 'email', 'usuario_id']
    for campo in campos_importantes:
        en_modelo = campo in campos_modelo
        en_tabla = campo in campos_tabla
        print(f"{campo}: {'✓' if en_modelo else '✗'} en modelo | {'✓' if en_tabla else '✗'} en tabla")
    
    # Mostrar el primer registro (si existe) para ver los datos
    try:
        primer_tecnico = Tecnico.objects.first()
        if primer_tecnico:
            print("\nPrimer técnico en la base de datos:")
            print(f"- ID: {primer_tecnico.id}")
            print(f"- Nombre: {getattr(primer_tecnico, 'nombre', 'No definido')}")
            print(f"- Apellido: {getattr(primer_tecnico, 'apellido', 'No definido')}")
            print(f"- Email: {getattr(primer_tecnico, 'email', 'No definido')}")
            print(f"- Usuario asociado: {primer_tecnico.usuario if hasattr(primer_tecnico, 'usuario') else 'Ninguno'}")
        else:
            print("\nNo hay técnicos registrados en la base de datos.")
    except Exception as e:
        print(f"\nError al acceder a los datos: {e}")

if __name__ == "__main__":
    check_tecnico_model()
