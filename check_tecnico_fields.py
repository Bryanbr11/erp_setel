import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_system.settings')
django.setup()

from django.db import connection

def check_tecnico_fields():
    with connection.cursor() as cursor:
        # Obtener la descripción de la tabla tecnicos_tecnico
        cursor.execute("PRAGMA table_info(tecnicos_tecnico)")
        columns = cursor.fetchall()
        
        print("\nCampos en la tabla tecnicos_tecnico:")
        print("-" * 50)
        for column in columns:
            # column[1] es el nombre de la columna
            print(f"- {column[1]} ({column[2]})")
        
        # Verificar si los campos críticos existen
        campos_requeridos = ['nombre', 'apellido', 'email']
        campos_encontrados = [col[1] for col in columns]
        
        print("\nVerificación de campos requeridos:")
        print("-" * 50)
        for campo in campos_requeridos:
            if campo in campos_encontrados:
                print(f"✓ {campo} - PRESENTE")
            else:
                print(f"✗ {campo} - AUSENTE")

if __name__ == "__main__":
    check_tecnico_fields()
