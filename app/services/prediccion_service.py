from sqlalchemy.orm import Session
from sqlalchemy import and_, func as sql_func
from fastapi import HTTPException
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
import math
import statistics
from ..models.reserva import Reserva
from ..models.servicio import Servicio
from ..models.recurso import Recurso

class PrediccionService:
    """Servicio especializado en algoritmos de predicción avanzados"""
    
    @staticmethod
    def prediccion_arima_simple(db: Session, servicio_id: int, dias_futuros: int = 30) -> Dict[str, Any]:
        """Predicción usando modelo ARIMA simple (promedio móvil)"""
        # Obtener datos históricos de los últimos 120 días
        inicio_historico = datetime.now() - timedelta(days=120)
        
        # Obtener reservas diarias para el servicio
        reservas_diarias = db.query(
            sql_func.date(Reserva.fecha_hora_inicio).label('fecha'),
            sql_func.count(Reserva.id).label('total')
        ).filter(
            and_(
                Reserva.servicio_id == servicio_id,
                Reserva.fecha_hora_inicio >= inicio_historico,
                Reserva.estado != "cancelada"
            )
        ).group_by(sql_func.date(Reserva.fecha_hora_inicio)).order_by(
            sql_func.date(Reserva.fecha_hora_inicio)
        ).all()
        
        if len(reservas_diarias) < 30:
            raise HTTPException(status_code=400, detail="Datos insuficientes para predicción ARIMA")
        
        # Convertir a lista de valores
        valores = [r.total for r in reservas_diarias]
        
        # Calcular promedio móvil (ventana de 7 días)
        ventana = 7
        promedios_moviles = []
        for i in range(ventana, len(valores)):
            promedio = sum(valores[i-ventana:i]) / ventana
            promedios_moviles.append(promedio)
        
        # Calcular tendencia lineal
        if len(promedios_moviles) > 1:
            x = list(range(len(promedios_moviles)))
            y = promedios_moviles
            
            # Regresión lineal simple
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            pendiente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            intercepto = (sum_y - pendiente * sum_x) / n
        else:
            pendiente = 0
            intercepto = statistics.mean(valores) if valores else 0
        
        # Generar predicciones
        predicciones = []
        ultimo_promedio = promedios_moviles[-1] if promedios_moviles else statistics.mean(valores)
        
        for i in range(dias_futuros):
            # Predicción = último promedio + tendencia + estacionalidad
            prediccion_base = ultimo_promedio + (pendiente * i)
            
            # Factor estacional (día de la semana)
            fecha_prediccion = date.today() + timedelta(days=i)
            dia_semana = fecha_prediccion.weekday()
            
            # Calcular factor estacional promedio para este día
            factor_estacional = PrediccionService._calcular_factor_estacional(db, servicio_id, dia_semana)
            
            prediccion_final = max(0, round(prediccion_base * factor_estacional, 2))
            
            predicciones.append({
                "fecha": fecha_prediccion.strftime("%Y-%m-%d"),
                "dia_semana": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][dia_semana],
                "prediccion": prediccion_final,
                "tendencia": round(pendiente, 4),
                "factor_estacional": round(factor_estacional, 3)
            })
        
        return {
            "algoritmo": "ARIMA Simple",
            "servicio_id": servicio_id,
            "datos_historicos": {
                "dias_analizados": len(reservas_diarias),
                "total_reservas": sum(valores),
                "promedio_diario": round(statistics.mean(valores), 2),
                "desviacion_estandar": round(statistics.stdev(valores), 2) if len(valores) > 1 else 0
            },
            "parametros_modelo": {
                "ventana_promedio_movil": ventana,
                "pendiente_tendencia": round(pendiente, 4),
                "intercepto": round(intercepto, 2)
            },
            "predicciones": predicciones,
            "fecha_generacion": datetime.now().isoformat()
        }
    
    @staticmethod
    def prediccion_estacional_avanzada(db: Session, servicio_id: int, dias_futuros: int = 30) -> Dict[str, Any]:
        """Predicción usando análisis estacional avanzado"""
        # Obtener datos de los últimos 365 días
        inicio_historico = datetime.now() - timedelta(days=365)
        
        # Obtener reservas por mes y día de la semana
        reservas_por_mes_dia = db.query(
            sql_func.extract('month', Reserva.fecha_hora_inicio).label('mes'),
            sql_func.extract('dow', Reserva.fecha_hora_inicio).label('dia_semana'),
            sql_func.count(Reserva.id).label('total')
        ).filter(
            and_(
                Reserva.servicio_id == servicio_id,
                Reserva.fecha_hora_inicio >= inicio_historico,
                Reserva.estado != "cancelada"
            )
        ).group_by(
            sql_func.extract('month', Reserva.fecha_hora_inicio),
            sql_func.extract('dow', Reserva.fecha_hora_inicio)
        ).all()
        
        # Crear matriz de patrones estacionales
        patrones_estacionales = {}
        for mes in range(1, 13):
            patrones_estacionales[mes] = {}
            for dia in range(7):
                patrones_estacionales[mes][dia] = 0
        
        # Poblar patrones
        for r in reservas_por_mes_dia:
            mes = int(r.mes)
            dia = int(r.dia_semana)
            patrones_estacionales[mes][dia] = r.total
        
        # Calcular factores de estacionalidad
        factores_estacionales = {}
        for mes in range(1, 13):
            factores_estacionales[mes] = {}
            for dia in range(7):
                # Factor = valor / promedio del mes
                valores_mes = [patrones_estacionales[mes][d] for d in range(7)]
                promedio_mes = statistics.mean(valores_mes) if valores_mes else 1
                factor = patrones_estacionales[mes][dia] / promedio_mes if promedio_mes > 0 else 1
                factores_estacionales[mes][dia] = factor
        
        # Calcular tendencia general
        reservas_totales = db.query(Reserva).filter(
            and_(
                Reserva.servicio_id == servicio_id,
                Reserva.fecha_hora_inicio >= inicio_historico,
                Reserva.estado != "cancelada"
            )
        ).count()
        
        promedio_diario_historico = reservas_totales / 365
        
        # Generar predicciones
        predicciones = []
        for i in range(dias_futuros):
            fecha_prediccion = date.today() + timedelta(days=i)
            mes = fecha_prediccion.month
            dia_semana = fecha_prediccion.weekday()
            
            # Predicción = promedio histórico * factor estacional * ajuste temporal
            factor_estacional = factores_estacionales[mes][dia_semana]
            
            # Ajuste temporal (crecimiento gradual)
            factor_crecimiento = 1 + (i * 0.001)  # 0.1% de crecimiento diario
            
            prediccion = promedio_diario_historico * factor_estacional * factor_crecimiento
            prediccion = max(0, round(prediccion, 2))
            
            predicciones.append({
                "fecha": fecha_prediccion.strftime("%Y-%m-%d"),
                "dia_semana": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][dia_semana],
                "prediccion": prediccion,
                "factor_estacional": round(factor_estacional, 3),
                "factor_crecimiento": round(factor_crecimiento, 4)
            })
        
        return {
            "algoritmo": "Estacional Avanzado",
            "servicio_id": servicio_id,
            "datos_historicos": {
                "dias_analizados": 365,
                "total_reservas": reservas_totales,
                "promedio_diario": round(promedio_diario_historico, 2)
            },
            "patrones_estacionales": {
                "meses": {str(mes): {str(dia): patrones_estacionales[mes][dia] for dia in range(7)} for mes in range(1, 13)},
                "factores": {str(mes): {str(dia): round(factores_estacionales[mes][dia], 3) for dia in range(7)} for mes in range(1, 13)}
            },
            "predicciones": predicciones,
            "fecha_generacion": datetime.now().isoformat()
        }
    
    @staticmethod
    def prediccion_machine_learning_simple(db: Session, servicio_id: int, dias_futuros: int = 30) -> Dict[str, Any]:
        """Predicción usando algoritmo de ML simple (regresión polinomial)"""
        # Obtener datos de los últimos 180 días
        inicio_historico = datetime.now() - timedelta(days=180)
        
        # Obtener reservas diarias
        reservas_diarias = db.query(
            sql_func.date(Reserva.fecha_hora_inicio).label('fecha'),
            sql_func.count(Reserva.id).label('total')
        ).filter(
            and_(
                Reserva.servicio_id == servicio_id,
                Reserva.fecha_hora_inicio >= inicio_historico,
                Reserva.estado != "cancelada"
            )
        ).group_by(sql_func.date(Reserva.fecha_hora_inicio)).order_by(
            sql_func.date(Reserva.fecha_hora_inicio)
        ).all()
        
        if len(reservas_diarias) < 60:
            raise HTTPException(status_code=400, detail="Datos insuficientes para ML")
        
        # Preparar datos para regresión
        x = list(range(len(reservas_diarias)))
        y = [r.total for r in reservas_diarias]
        
        # Regresión polinomial de grado 2 (cuadrática)
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_x3 = sum(x[i] ** 3 for i in range(n))
        sum_x4 = sum(x[i] ** 4 for i in range(n))
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2y = sum(x[i] ** 2 * y[i] for i in range(n))
        
        # Resolver sistema de ecuaciones para coeficientes a, b, c
        # y = ax² + bx + c
        det = n * sum_x2 * sum_x4 + 2 * sum_x * sum_x2 * sum_x3 - sum_x2 ** 3 - n * sum_x3 ** 2 - sum_x ** 2 * sum_x4
        
        if abs(det) < 1e-10:
            # Si el determinante es muy pequeño, usar regresión lineal
            a, b, c = 0, 0, statistics.mean(y)
        else:
            a = (n * sum_x2y * sum_x2 + sum_x * sum_xy * sum_x3 + sum_y * sum_x2 * sum_x3 - 
                 sum_x2 ** 2 * sum_y - n * sum_xy * sum_x4 - sum_x ** 2 * sum_x2y) / det
            
            b = (n * sum_xy * sum_x4 + sum_x * sum_x2y * sum_x2 + sum_y * sum_x3 * sum_x2 - 
                 sum_x2 ** 2 * sum_x2y - n * sum_x3 * sum_xy - sum_x ** 2 * sum_x4) / det
            
            c = (sum_x2 * sum_x2y * sum_x4 + sum_x3 * sum_xy * sum_x3 + sum_x * sum_x2 * sum_x2y - 
                 sum_x2 ** 3 - sum_x3 ** 2 * sum_x2y - sum_x ** 2 * sum_x4) / det
        
        # Generar predicciones
        predicciones = []
        for i in range(dias_futuros):
            x_pred = len(x) + i
            prediccion = a * (x_pred ** 2) + b * x_pred + c
            prediccion = max(0, round(prediccion, 2))
            
            predicciones.append({
                "fecha": (date.today() + timedelta(days=i)).strftime("%Y-%m-%d"),
                "prediccion": prediccion,
                "coeficientes": {
                    "a": round(a, 6),
                    "b": round(b, 6),
                    "c": round(c, 6)
                }
            })
        
        # Calcular métricas de calidad del modelo
        predicciones_entrenamiento = []
        for i, x_val in enumerate(x):
            pred = a * (x_val ** 2) + b * x_val + c
            predicciones_entrenamiento.append(pred)
        
        # Error cuadrático medio
        mse = sum((y[i] - predicciones_entrenamiento[i]) ** 2 for i in range(n)) / n
        rmse = math.sqrt(mse)
        
        # Coeficiente de determinación R²
        y_mean = statistics.mean(y)
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        ss_res = sum((y[i] - predicciones_entrenamiento[i]) ** 2 for i in range(n))
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            "algoritmo": "Machine Learning Simple (Regresión Polinomial)",
            "servicio_id": servicio_id,
            "datos_entrenamiento": {
                "dias_analizados": n,
                "total_reservas": sum(y),
                "promedio_diario": round(statistics.mean(y), 2)
            },
            "modelo": {
                "ecuacion": f"y = {round(a, 6)}x² + {round(b, 6)}x + {round(c, 6)}",
                "coeficientes": {
                    "a": round(a, 6),
                    "b": round(b, 6),
                    "c": round(c, 6)
                }
            },
            "metricas_calidad": {
                "mse": round(mse, 4),
                "rmse": round(rmse, 4),
                "r2": round(r2, 4)
            },
            "predicciones": predicciones,
            "fecha_generacion": datetime.now().isoformat()
        }
    
    @staticmethod
    def _calcular_factor_estacional(db: Session, servicio_id: int, dia_semana: int) -> float:
        """Calcular factor estacional para un día específico de la semana"""
        # Obtener datos de los últimos 90 días
        inicio_historico = datetime.now() - timedelta(days=90)
        
        # Obtener reservas para este día de la semana
        reservas_dia = db.query(Reserva).filter(
            and_(
                Reserva.servicio_id == servicio_id,
                Reserva.fecha_hora_inicio >= inicio_historico,
                sql_func.extract('dow', Reserva.fecha_hora_inicio) == dia_semana,
                Reserva.estado != "cancelada"
            )
        ).count()
        
        # Obtener total de reservas en el período
        total_reservas = db.query(Reserva).filter(
            and_(
                Reserva.servicio_id == servicio_id,
                Reserva.fecha_hora_inicio >= inicio_historico,
                Reserva.estado != "cancelada"
            )
        ).count()
        
        # Calcular factor estacional
        if total_reservas > 0:
            # Factor = (reservas del día / total) / (1/7)
            factor = (reservas_dia / total_reservas) / (1/7)
            return factor
        else:
            return 1.0

