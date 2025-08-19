#!/usr/bin/env python3
"""
Script de Inicialización de Datos de Prueba
Microservicio de Gestión de Reservas

Este script crea datos de prueba para el microservicio:
- 1 Cliente
- 1 Servicio  
- 1 Recurso
- 2 Usuarios (admin y normal)
- 1 Regla de precio
- 1 Reserva de ejemplo

Uso:
    python scripts/init_data.py
"""

import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al path para importar la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, engine
from app.models import Cliente, Servicio, Recurso, Usuario, Precio, Reserva
from app.auth import get_password_hash

def create_test_data():
    """Crear datos de prueba en la base de datos"""
    db = SessionLocal()
    
    try:
        print("🚀 Iniciando creación de datos de prueba...")
        
        # 1. Crear Cliente de prueba
        print("👥 Creando cliente de prueba...")
        cliente = Cliente(
            nombre="María González López",
            email="maria.gonzalez@email.com",
            telefono="+34 600 123 456"
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        print(f"✅ Cliente creado: {cliente.nombre} (ID: {cliente.id})")
        
        # 2. Crear Servicio de prueba
        print("🛠️ Creando servicio de prueba...")
        servicio = Servicio(
            nombre="Consulta Médica General",
            descripcion="Consulta médica general de 30 minutos con revisión completa",
            duracion_minutos=30,
            precio_base=50.00
        )
        db.add(servicio)
        db.commit()
        db.refresh(servicio)
        print(f"✅ Servicio creado: {servicio.nombre} (ID: {servicio.id})")
        
        # 3. Crear Recurso de prueba
        print("🏢 Creando recurso de prueba...")
        recurso = Recurso(
            nombre="Consultorio Principal",
            tipo="consultorio",
            disponible=True
        )
        db.add(recurso)
        db.commit()
        db.refresh(recurso)
        print(f"✅ Recurso creado: {recurso.nombre} (ID: {recurso.id})")
        
        # 4. Crear Usuario Administrador
        print("👑 Creando usuario administrador...")
        admin_user = Usuario(
            username="admin",
            email="admin@reservas.com",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"✅ Usuario admin creado: {admin_user.username} (ID: {admin_user.id})")
        
        # 5. Crear Usuario Normal
        print("👤 Creando usuario normal...")
        normal_user = Usuario(
            username="usuario",
            email="usuario@reservas.com",
            hashed_password=get_password_hash("user123"),
            is_admin=False,
            is_active=True
        )
        db.add(normal_user)
        db.commit()
        db.refresh(normal_user)
        print(f"✅ Usuario normal creado: {normal_user.username} (ID: {normal_user.id})")
        
        # 6. Crear Regla de Precio
        print("💰 Creando regla de precio...")
        precio = Precio(
            servicio_id=servicio.id,
            tipo_regla="fin_de_semana",
            valor=65.00,
            descripcion="Precio especial para fines de semana"
        )
        db.add(precio)
        db.commit()
        db.refresh(precio)
        print(f"✅ Precio creado: {precio.tipo_regla} - €{precio.valor} (ID: {precio.id})")
        
        # 7. Crear Reserva de ejemplo
        print("📅 Creando reserva de ejemplo...")
        # Reserva para mañana a las 10:00 AM
        tomorrow = datetime.now() + timedelta(days=1)
        fecha_inicio = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(minutes=servicio.duracion_minutos)
        
        reserva = Reserva(
            cliente_id=cliente.id,
            servicio_id=servicio.id,
            recurso_id=recurso.id,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            estado="confirmada"
        )
        db.add(reserva)
        db.commit()
        db.refresh(reserva)
        print(f"✅ Reserva creada: {fecha_inicio.strftime('%Y-%m-%d %H:%M')} (ID: {reserva.id})")
        
        print("\n🎉 ¡Datos de prueba creados exitosamente!")
        print("\n📋 RESUMEN DE DATOS CREADOS:")
        print("=" * 50)
        print(f"👥 Cliente: {cliente.nombre} (ID: {cliente.id})")
        print(f"🛠️ Servicio: {servicio.nombre} (ID: {servicio.id})")
        print(f"🏢 Recurso: {recurso.nombre} (ID: {recurso.id})")
        print(f"👑 Admin: {admin_user.username} (ID: {admin_user.id})")
        print(f"👤 Usuario: {normal_user.username} (ID: {normal_user.id})")
        print(f"💰 Precio: {precio.tipo_regla} - €{precio.valor} (ID: {precio.id})")
        print(f"📅 Reserva: {fecha_inicio.strftime('%Y-%m-%d %H:%M')} (ID: {reserva.id})")
        
        print("\n🔑 CREDENCIALES DE ACCESO:")
        print("=" * 50)
        print("👑 Administrador:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@reservas.com")
        print("\n👤 Usuario Normal:")
        print("   Username: usuario")
        print("   Password: user123")
        print("   Email: usuario@reservas.com")
        
        print("\n🌐 Accede a la documentación en:")
        print("   Swagger UI: http://localhost:8000/docs")
        print("   ReDoc: http://localhost:8000/redoc")
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_data():
    """Verificar que los datos se crearon correctamente"""
    db = SessionLocal()
    
    try:
        print("\n🔍 Verificando datos creados...")
        
        # Contar registros
        clientes_count = db.query(Cliente).count()
        servicios_count = db.query(Servicio).count()
        recursos_count = db.query(Recurso).count()
        usuarios_count = db.query(Usuario).count()
        precios_count = db.query(Precio).count()
        reservas_count = db.query(Reserva).count()
        
        print(f"✅ Clientes: {clientes_count}")
        print(f"✅ Servicios: {servicios_count}")
        print(f"✅ Recursos: {recursos_count}")
        print(f"✅ Usuarios: {usuarios_count}")
        print(f"✅ Precios: {precios_count}")
        print(f"✅ Reservas: {reservas_count}")
        
        if all([clientes_count, servicios_count, recursos_count, usuarios_count, precios_count, reservas_count]):
            print("\n🎯 Todos los datos se crearon correctamente!")
        else:
            print("\n⚠️ Algunos datos no se crearon correctamente")
            
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🏥 MICROSERVICIO DE GESTIÓN DE RESERVAS")
    print("=" * 50)
    
    try:
        # Crear datos de prueba
        create_test_data()
        
        # Verificar datos
        verify_data()
        
        print("\n✨ Script de inicialización completado exitosamente!")
        
    except Exception as e:
        print(f"\n💥 Error en el script de inicialización: {e}")
        sys.exit(1)
