from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..db_sqlite_clean import get_db
from ..services.pago_service import PagoService, FacturaService, ReembolsoService, ResumenPagosService
from ..schemas.pago import (
    PagoCreate, PagoUpdate, PagoResponse, PagoCompletoResponse,
    FacturaCreate, FacturaUpdate, FacturaResponse,
    ReembolsoCreate, ReembolsoUpdate, ReembolsoResponse,
    ResumenPagosResponse
)

router = APIRouter(prefix="/api/pagos", tags=["pagos"])

# ============================================================================
# RUTAS PARA PAGOS
# ============================================================================

@router.get("/", response_model=List[PagoResponse])
def listar_pagos(
    skip: int = 0, 
    limit: int = 100, 
    estado: Optional[str] = None,
    metodo_pago: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar todos los pagos con filtros opcionales"""
    try:
        pagos = PagoService.listar_pagos(db, skip=skip, limit=limit, estado=estado, metodo_pago=metodo_pago)
        return pagos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al listar pagos: {str(e)}"
        )

@router.post("/", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def crear_pago(pago_data: PagoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo pago"""
    try:
        pago = PagoService.crear_pago(db, pago_data)
        return pago
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear pago: {str(e)}"
        )

@router.get("/{pago_id}", response_model=PagoResponse)
def obtener_pago(pago_id: int, db: Session = Depends(get_db)):
    """Obtener un pago por ID"""
    pago = PagoService.obtener_pago(db, pago_id)
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    return pago

@router.get("/reserva/{reserva_id}", response_model=List[PagoResponse])
def obtener_pagos_por_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """Obtener todos los pagos de una reserva"""
    pagos = PagoService.obtener_pagos_por_reserva(db, reserva_id)
    return pagos

@router.get("/cliente/{cliente_id}", response_model=List[PagoResponse])
def obtener_pagos_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtener todos los pagos de un cliente"""
    pagos = PagoService.obtener_pagos_por_cliente(db, cliente_id)
    return pagos

@router.put("/{pago_id}", response_model=PagoResponse)
def actualizar_pago(pago_id: int, pago_data: PagoUpdate, db: Session = Depends(get_db)):
    """Actualizar un pago existente"""
    pago = PagoService.actualizar_pago(db, pago_id, pago_data)
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    return pago

@router.post("/{pago_id}/stripe", response_model=PagoResponse)
def procesar_pago_stripe(pago_id: int, stripe_payment_intent_id: str, db: Session = Depends(get_db)):
    """Procesar pago con Stripe"""
    pago = PagoService.procesar_pago_stripe(db, pago_id, stripe_payment_intent_id)
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    return pago

@router.post("/{pago_id}/paypal", response_model=PagoResponse)
def procesar_pago_paypal(pago_id: int, paypal_order_id: str, db: Session = Depends(get_db)):
    """Procesar pago con PayPal"""
    pago = PagoService.procesar_pago_paypal(db, pago_id, paypal_order_id)
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    return pago

@router.post("/{pago_id}/cancelar")
def cancelar_pago(pago_id: int, motivo: str, db: Session = Depends(get_db)):
    """Cancelar un pago"""
    try:
        pago = PagoService.cancelar_pago(db, pago_id, motivo)
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado"
            )
        return {"mensaje": "Pago cancelado exitosamente", "pago_id": pago_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{pago_id}/completo", response_model=PagoCompletoResponse)
def obtener_pago_completo(pago_id: int, db: Session = Depends(get_db)):
    """Obtener pago con factura y reembolsos"""
    pago = PagoService.obtener_pago(db, pago_id)
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    
    # Obtener factura si existe
    factura = None
    if pago.factura_generada:
        factura = FacturaService.obtener_factura(db, pago.id)
    
    # Obtener reembolsos si existen
    reembolsos = []
    if pago.estado.value == "reembolsado":
        # Aquí podrías implementar un método para obtener reembolsos por pago
        pass
    
    return PagoCompletoResponse(
        **pago.__dict__,
        factura=factura,
        reembolsos=reembolsos
    )

# ============================================================================
# RUTAS PARA FACTURAS
# ============================================================================

@router.post("/{pago_id}/factura", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
def generar_factura(pago_id: int, db: Session = Depends(get_db)):
    """Generar factura para un pago"""
    factura = FacturaService.generar_factura(db, pago_id)
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede generar factura para este pago"
        )
    return factura

@router.get("/facturas/{factura_id}", response_model=FacturaResponse)
def obtener_factura(factura_id: int, db: Session = Depends(get_db)):
    """Obtener una factura por ID"""
    factura = FacturaService.obtener_factura(db, factura_id)
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    return factura

@router.get("/facturas/cliente/{cliente_id}", response_model=List[FacturaResponse])
def obtener_facturas_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtener todas las facturas de un cliente"""
    facturas = FacturaService.obtener_facturas_por_cliente(db, cliente_id)
    return facturas

@router.put("/facturas/{factura_id}/marcar-pagada", response_model=FacturaResponse)
def marcar_factura_pagada(factura_id: int, db: Session = Depends(get_db)):
    """Marcar una factura como pagada"""
    factura = FacturaService.marcar_factura_pagada(db, factura_id)
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    return factura

# ============================================================================
# RUTAS PARA REEMBOLSOS
# ============================================================================

@router.post("/{pago_id}/reembolso", response_model=ReembolsoResponse, status_code=status.HTTP_201_CREATED)
def solicitar_reembolso(pago_id: int, reembolso_data: ReembolsoCreate, db: Session = Depends(get_db)):
    """Solicitar un reembolso"""
    try:
        # Asegurar que el pago_id en los datos coincida con la URL
        reembolso_data.pago_id = pago_id
        reembolso = ReembolsoService.solicitar_reembolso(db, reembolso_data)
        return reembolso
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/reembolsos/{reembolso_id}", response_model=ReembolsoResponse)
def obtener_reembolso(reembolso_id: int, db: Session = Depends(get_db)):
    """Obtener un reembolso por ID"""
    # Implementar método para obtener reembolso por ID
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Método no implementado aún"
    )

@router.put("/reembolsos/{reembolso_id}/aprobar", response_model=ReembolsoResponse)
def aprobar_reembolso(reembolso_id: int, usuario_id: int, db: Session = Depends(get_db)):
    """Aprobar un reembolso"""
    try:
        reembolso = ReembolsoService.aprobar_reembolso(db, reembolso_id, usuario_id)
        if not reembolso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reembolso no encontrado"
            )
        return reembolso
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/reembolsos/{reembolso_id}/procesar", response_model=ReembolsoResponse)
def procesar_reembolso(reembolso_id: int, transaccion_id: str, db: Session = Depends(get_db)):
    """Procesar un reembolso aprobado"""
    try:
        reembolso = ReembolsoService.procesar_reembolso(db, reembolso_id, transaccion_id)
        if not reembolso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reembolso no encontrado"
            )
        return reembolso
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ============================================================================
# RUTAS PARA ESTADÍSTICAS Y RESUMENES
# ============================================================================

@router.get("/resumen/general", response_model=ResumenPagosResponse)
def obtener_resumen_pagos(db: Session = Depends(get_db)):
    """Obtener resumen general de pagos"""
    resumen = ResumenPagosService.obtener_resumen_pagos(db)
    return resumen

@router.get("/estadisticas/mensual/{año}/{mes}")
def obtener_estadisticas_mensuales(año: int, mes: int, db: Session = Depends(get_db)):
    """Obtener estadísticas de pagos por mes"""
    if mes < 1 or mes > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mes debe estar entre 1 y 12"
        )
    
    if año < 2020 or año > 2030:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Año debe estar entre 2020 y 2030"
        )
    
    estadisticas = ResumenPagosService.obtener_estadisticas_mensuales(db, año, mes)
    return estadisticas

# ============================================================================
# RUTAS PARA WEBHOOKS DE PAGOS
# ============================================================================

@router.post("/webhook/stripe")
def webhook_stripe(db: Session = Depends(get_db)):
    """Webhook para recibir notificaciones de Stripe"""
    # En un entorno real, aquí se verificaría la firma de Stripe
    # y se procesarían los eventos de pago
    return {"mensaje": "Webhook de Stripe recibido", "status": "success"}

@router.post("/webhook/paypal")
def webhook_paypal(db: Session = Depends(get_db)):
    """Webhook para recibir notificaciones de PayPal"""
    # En un entorno real, aquí se verificaría la autenticidad de PayPal
    # y se procesarían los eventos de pago
    return {"mensaje": "Webhook de PayPal recibido", "status": "success"}
