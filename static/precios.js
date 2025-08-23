// ========================================
// SISTEMA DE GESTIÓN DE PRECIOS
// ========================================

console.log('💰 Módulo de Sistema de Precios cargado - Versión 1.0');

// Variables globales para el sistema de precios
let preciosData = [];
let serviciosDataPrecios = [];
let recursosDataPrecios = [];
let clientesDataPrecios = [];

// Funciones de debug para consola del navegador
window.testSistemaPrecios = function() {
    console.log('🧪 Probando sistema de precios...');
    console.log('📊 Precios en memoria:', preciosData.length);
    console.log('🔍 Contenedor encontrado:', !!document.getElementById('preciosContainer'));
    console.log('🎯 Tab de precios encontrada:', !!document.getElementById('precios-tab'));
};

window.forzarCargaPrecios = function() {
    console.log('🚀 Forzando carga de precios...');
    cargarPrecios();
};

window.activarTabPrecios = function() {
    console.log('🎯 Activando tab de precios...');
    const preciosTab = document.getElementById('precios-tab');
    if (preciosTab) {
        preciosTab.click();
    }
};

window.debugPreciosData = function() {
    console.log('📊 Datos de precios:', preciosData);
    console.log('📊 Servicios:', serviciosDataPrecios);
    console.log('📊 Recursos:', recursosDataPrecios);
    console.log('📊 Clientes:', clientesDataPrecios);
};

/**
 * Inicializar el sistema de precios
 */
function initSistemaPrecios() {
    console.log('💰 Inicializando Sistema de Precios...');
    
    // Verificar que los elementos existan
    const preciosTab = document.getElementById('precios-tab');
    console.log('🔍 Tab de precios encontrada:', !!preciosTab);
    
    if (preciosTab) {
        console.log('📝 Configurando event listener para tab de precios...');
        preciosTab.addEventListener('click', function() {
            console.log('🖱️ Tab de precios clickeada');
            
            // ✅ FORZAR activación de la tab
            setTimeout(() => {
                const preciosTabPane = document.getElementById('precios');
                if (preciosTabPane) {
                    preciosTabPane.classList.remove('fade');
                    preciosTabPane.classList.add('show', 'active');
                    console.log('🎯 Tab de precios activada forzadamente');
                }
            }, 100);
            
            if (preciosData.length === 0) {
                console.log('🔄 Cargando precios desde click en tab...');
                cargarPrecios();
                cargarDatosParaPrecios();
            } else {
                console.log('ℹ️ Precios ya cargados, no es necesario recargar');
            }
        });
        
        // También cargar precios automáticamente si la tab está activa
        if (preciosTab.classList.contains('active') || preciosTab.getAttribute('aria-selected') === 'true') {
            console.log('🎯 Tab de precios ya está activa, cargando datos...');
            cargarPrecios();
            cargarDatosParaPrecios();
        }
    } else {
        console.warn('⚠️ No se encontró la tab de precios');
        
        // Si no hay tab, cargar precios directamente (para páginas de test)
        console.log('🔄 Cargando precios directamente...');
        cargarPrecios();
        cargarDatosParaPrecios();
    }
    
    // Configurar eventos para los formularios
    setupPreciosEventListeners();
    
    console.log('✅ Sistema de Precios inicializado correctamente');
}

/**
 * Configurar event listeners para el sistema de precios
 */
function setupPreciosEventListeners() {
    // Actualizar símbolo de moneda cuando cambie la selección
    const nuevoPrecioMoneda = document.getElementById('nuevoPrecioMoneda');
    if (nuevoPrecioMoneda) {
        nuevoPrecioMoneda.addEventListener('change', function() {
            const simbolos = { 'EUR': '€', 'USD': '$', 'GBP': '£' };
            document.getElementById('nuevoPrecioMonedaSymbol').textContent = simbolos[this.value] || '€';
        });
    }
    
    // Auto-completar nombre basado en tipo y servicio/recurso
    const tipoSelect = document.getElementById('nuevoPrecioTipo');
    const servicioSelect = document.getElementById('nuevoPrecioServicio');
    const recursoSelect = document.getElementById('nuevoPrecioRecurso');
    const nombreInput = document.getElementById('nuevoPrecioNombre');
    
    function autoCompletarNombre() {
        if (!tipoSelect || !nombreInput) return;
        
        const tipo = tipoSelect.value;
        const servicio = servicioSelect?.options[servicioSelect.selectedIndex]?.text;
        const recurso = recursoSelect?.options[recursoSelect.selectedIndex]?.text;
        
        if (tipo && (servicio || recurso)) {
            const tipoTexto = {
                'base': 'Precio Base',
                'descuento': 'Descuento',
                'recargo': 'Recargo',
                'hora': 'Precio por Hora',
                'dia': 'Precio por Día',
                'temporada': 'Precio Temporada',
                'grupo': 'Precio Grupo'
            };
            
            const entidad = servicio && servicio !== 'Seleccionar servicio...' ? servicio : 
                          recurso && recurso !== 'Seleccionar recurso...' ? recurso : '';
            
            nombreInput.value = `${tipoTexto[tipo] || tipo} ${entidad}`.trim();
        }
    }
    
    if (tipoSelect) tipoSelect.addEventListener('change', autoCompletarNombre);
    if (servicioSelect) servicioSelect.addEventListener('change', autoCompletarNombre);
    if (recursoSelect) recursoSelect.addEventListener('change', autoCompletarNombre);
}

/**
 * Cargar datos necesarios para el sistema de precios
 */
async function cargarDatosParaPrecios() {
    try {
        console.log('🔄 Cargando datos auxiliares para sistema de precios...');
        
        // ✅ SOLUCIÓN: Solo cargar datos auxiliares (NO precios)
        const [serviciosResponse, recursosResponse, clientesResponse] = await Promise.all([
            fetch('/servicios/'),
            fetch('/recursos/'),
            fetch('/clientes/')
        ]);
        
        serviciosDataPrecios = await serviciosResponse.json();
        recursosDataPrecios = await recursosResponse.json();
        clientesDataPrecios = await clientesResponse.json();
        
        // Poblar los select del formulario
        poblarSelectServicios();
        poblarSelectRecursos();
        poblarSelectClientes();
        
        console.log('✅ Datos auxiliares cargados para sistema de precios');
        
    } catch (error) {
        console.error('❌ Error cargando datos auxiliares:', error);
        mostrarToastPrecios('Error cargando datos auxiliares', 'error');
    }
}

/**
 * Poblar select de servicios
 */
function poblarSelectServicios() {
    const selects = ['nuevoPrecioServicio', 'calcServicio'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select && serviciosDataPrecios.length > 0) {
            // Limpiar opciones existentes excepto la primera
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            serviciosDataPrecios.forEach(servicio => {
                const option = document.createElement('option');
                option.value = servicio.id;
                option.textContent = `${servicio.nombre} (€${servicio.precio_base})`;
                select.appendChild(option);
            });
        }
    });
}

/**
 * Poblar select de recursos
 */
function poblarSelectRecursos() {
    const selects = ['nuevoPrecioRecurso', 'calcRecurso'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select && recursosDataPrecios.length > 0) {
            // Limpiar opciones existentes excepto la primera
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            recursosDataPrecios.forEach(recurso => {
                const option = document.createElement('option');
                option.value = recurso.id;
                option.textContent = `${recurso.nombre} (€${recurso.precio_base}/hora)`;
                select.appendChild(option);
            });
        }
    });
}

/**
 * Poblar select de clientes
 */
function poblarSelectClientes() {
    const select = document.getElementById('calcCliente');
    if (select && clientesDataPrecios.length > 0) {
        // Limpiar opciones existentes excepto la primera
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        clientesDataPrecios.forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente.id;
            option.textContent = `${cliente.nombre} (${cliente.email})`;
            select.appendChild(option);
        });
    }
}

/**
 * Cargar todos los precios del sistema
 */
async function cargarPrecios() {
    try {
        console.log('🔄 Iniciando carga de precios...');
        
        const container = document.getElementById('preciosContainer');
        if (!container) {
            console.error('❌ No se encontró el contenedor de precios');
            return;
        }
        
        // ✅ SOLUCIÓN PERMANENTE: Mover el contenedor fuera del modal si es necesario
        if (container.offsetParent === null) {
            console.log('📦 Contenedor oculto, moviendo fuera del modal...');
            moverContenedorPrecios();
        }
        
        console.log('📦 Contenedor encontrado, mostrando carga...');
        mostrarCargandoPrecios('preciosContainer');
        
        console.log('🌐 Haciendo fetch a /api/precios/...');
        const response = await fetch('/api/precios/');
        console.log('📡 Respuesta recibida:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        console.log('📄 Parseando respuesta JSON...');
        const precios = await response.json();
        console.log('📊 Precios parseados:', precios);
        console.log('📊 Tipo de datos:', typeof precios);
        console.log('📊 Es array?', Array.isArray(precios));
        
        // ✅ SOLUCIÓN: Guardar datos y mostrar inmediatamente
        preciosData = precios;
        console.log('💾 Precios guardados en memoria:', preciosData.length);
        
        console.log('🎨 ANTES de llamar a displayPreciosList...');
        console.log('🎨 precios a pasar:', precios);
        console.log('🎨 container.innerHTML actual:', container.innerHTML);
        
        // Llamar a displayPreciosList
        displayPreciosList(precios);
        
        console.log('🎨 DESPUÉS de llamar a displayPreciosList...');
        console.log('🎨 container.innerHTML después:', container.innerHTML);
        
        console.log('✅ Precios cargados exitosamente:', precios.length);
        
    } catch (error) {
        console.error('❌ Error cargando precios:', error);
        console.error('❌ Stack trace:', error.stack);
        mostrarErrorPrecios('preciosContainer', 'Error al cargar los precios');
    }
}

/**
 * Mover el contenedor de precios fuera del modal si es necesario
 */
function moverContenedorPrecios() {
    const container = document.getElementById('preciosContainer');
    if (!container) return;
    
    // Mover al body si no está ya ahí
    if (container.parentElement !== document.body) {
        document.body.appendChild(container);
        console.log('✅ Contenedor movido al body');
    }
    
    // Aplicar estilos para que se vea bien
    container.style.cssText = `
        position: relative !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        height: auto !important;
        overflow: visible !important;
        z-index: 9999 !important;
        margin: 20px !important;
        padding: 20px !important;
        background: white !important;
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        max-width: 1200px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    `;
    
    console.log('✅ Contenedor estilizado y visible');
}

/**
 * Mostrar la lista de precios en el contenedor
 */
function displayPreciosList(precios) {
    console.log('🎨 Iniciando displayPreciosList con:', precios);
    console.log('🎨 Tipo de precios:', typeof precios);
    console.log('🎨 Es array?', Array.isArray(precios));
    console.log('🎨 Longitud:', precios ? precios.length : 'undefined');
    
    const container = document.getElementById('preciosContainer');
    if (!container) {
        console.error('❌ No se encontró el contenedor preciosContainer');
        return;
    }
    
    console.log('📦 Contenedor encontrado, verificando datos...');
    console.log('📦 Container ID:', container.id);
    console.log('📦 Container actual HTML:', container.innerHTML);
    
    if (!precios || precios.length === 0) {
        console.log('ℹ️ No hay precios para mostrar');
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-tag fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No hay precios configurados</h5>
                <p class="text-muted">Crea tu primer precio usando el botón "Nuevo Precio"</p>
            </div>
        `;
        return;
    }
    
    console.log(`🔄 Generando HTML para ${precios.length} precios...`);
    
    let html = '';
    precios.forEach((precio, index) => {
        console.log(`📝 Procesando precio ${index + 1}:`, precio);
        console.log(`📝 Campos del precio:`, {
            id: precio.id,
            nombre: precio.nombre,
            tipo_precio: precio.tipo_precio,
            precio_base: precio.precio_base,
            moneda: precio.moneda,
            activo: precio.activo,
            prioridad: precio.prioridad
        });
        
        const estadoBadge = precio.activo 
            ? '<span class="badge bg-success">Activo</span>'
            : '<span class="badge bg-secondary">Inactivo</span>';
            
        const tipoBadge = getTipoPrecioBadge(precio.tipo_precio);
        const entidadInfo = getEntidadInfo(precio);
        
        html += `
            <div class="card mb-3 precio-card" data-precio-id="${precio.id}">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <h6 class="mb-1">${precio.nombre}</h6>
                            <small class="text-muted">${entidadInfo}</small>
                        </div>
                        <div class="col-md-2">
                            ${tipoBadge}
                        </div>
                        <div class="col-md-2">
                            <h5 class="mb-0 text-primary">
                                ${formatearMoneda(precio.precio_base, precio.moneda)}
                            </h5>
                        </div>
                        <div class="col-md-2">
                            ${estadoBadge}
                            <div class="small text-muted">Prioridad: ${precio.prioridad}</div>
                        </div>
                        <div class="col-md-3 text-end">
                            <div class="btn-group" role="group">
                                <button class="btn btn-sm btn-outline-info" onclick="verDetallePrecio(${precio.id})" title="Ver detalles">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-primary" onclick="editarPrecio(${precio.id})" title="Editar">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-secondary" onclick="duplicarPrecioFunc(${precio.id})" title="Duplicar">
                                    <i class="fas fa-copy"></i>
                                </button>
                                <button class="btn btn-sm ${precio.activo ? 'btn-outline-warning' : 'btn-outline-success'}" 
                                        onclick="togglePrecioEstado(${precio.id}, ${precio.activo})" 
                                        title="${precio.activo ? 'Desactivar' : 'Activar'}">
                                    <i class="fas fa-${precio.activo ? 'pause' : 'play'}"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="eliminarPrecio(${precio.id})" title="Eliminar">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    ${precio.descripcion ? `<div class="row mt-2"><div class="col-12"><small class="text-muted">${precio.descripcion}</small></div></div>` : ''}
                </div>
            </div>
        `;
    });
    
    console.log('📄 HTML generado, aplicando al contenedor...');
    console.log('📄 HTML generado (primeros 500 chars):', html.substring(0, 500));
    container.innerHTML = html;
    console.log('✅ Lista de precios mostrada correctamente');
    console.log('✅ Container HTML después:', container.innerHTML.substring(0, 500));
}

/**
 * Obtener badge del tipo de precio
 */
function getTipoPrecioBadge(tipo) {
    const badges = {
        'base': '<span class="badge bg-primary">Base</span>',
        'descuento': '<span class="badge bg-success">Descuento</span>',
        'recargo': '<span class="badge bg-warning">Recargo</span>',
        'hora': '<span class="badge bg-info">Por Hora</span>',
        'dia': '<span class="badge bg-secondary">Por Día</span>',
        'temporada': '<span class="badge bg-purple">Temporada</span>',
        'grupo': '<span class="badge bg-orange">Grupo</span>'
    };
    
    return badges[tipo] || `<span class="badge bg-light text-dark">${tipo}</span>`;
}

/**
 * Obtener información de la entidad asociada al precio
 */
function getEntidadInfo(precio) {
    if (precio.servicio_id) {
        return `Servicio ID: ${precio.servicio_id}`;
    } else if (precio.recurso_id) {
        return `Recurso ID: ${precio.recurso_id}`;
    }
    return 'Sin entidad asociada';
}

/**
 * Formatear moneda
 */
function formatearMoneda(monto, moneda = 'EUR') {
    const simbolos = { 'EUR': '€', 'USD': '$', 'GBP': '£' };
    const simbolo = simbolos[moneda] || '€';
    return `${simbolo}${parseFloat(monto).toFixed(2)}`;
}

/**
 * Crear un nuevo precio
 */
async function crearNuevoPrecio() {
    try {
        const form = document.getElementById('nuevoPrecioForm');
        
        // Validar que se haya seleccionado servicio o recurso
        const servicioId = document.getElementById('nuevoPrecioServicio').value;
        const recursoId = document.getElementById('nuevoPrecioRecurso').value;
        
        if (!servicioId && !recursoId) {
            mostrarToastPrecios('Debe seleccionar un servicio o un recurso', 'warning');
            return;
        }
        
        if (servicioId && recursoId) {
            mostrarToastPrecios('No puede seleccionar servicio y recurso al mismo tiempo', 'warning');
            return;
        }
        
        // Preparar datos del precio
        const precioData = {
            servicio_id: servicioId ? parseInt(servicioId) : null,
            recurso_id: recursoId ? parseInt(recursoId) : null,
            tipo_precio: document.getElementById('nuevoPrecioTipo').value,
            nombre: document.getElementById('nuevoPrecioNombre').value,
            descripcion: document.getElementById('nuevoPrecioDescripcion').value || null,
            precio_base: parseFloat(document.getElementById('nuevoPrecioPrecio').value),
            moneda: document.getElementById('nuevoPrecioMoneda').value,
            activo: document.getElementById('nuevoPrecioActivo').checked,
            prioridad: parseInt(document.getElementById('nuevoPrecioPrioridad').value) || 0,
            fecha_inicio: document.getElementById('nuevoPrecioFechaInicio').value || null,
            fecha_fin: document.getElementById('nuevoPrecioFechaFin').value || null,
            cantidad_minima: document.getElementById('nuevoPrecioCantidadMin').value ? parseInt(document.getElementById('nuevoPrecioCantidadMin').value) : null,
            cantidad_maxima: document.getElementById('nuevoPrecioCantidadMax').value ? parseInt(document.getElementById('nuevoPrecioCantidadMax').value) : null,
            hora_inicio: document.getElementById('nuevoPrecioHoraInicio').value || null,
            hora_fin: document.getElementById('nuevoPrecioHoraFin').value || null,
            dias_semana: document.getElementById('nuevoPrecioDiasSemana').value || null
        };
        
        console.log('🔄 Creando precio:', precioData);
        
        const response = await fetch('/api/precios/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(precioData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al crear el precio');
        }
        
        const nuevoPrecio = await response.json();
        
        mostrarToastPrecios('Precio creado exitosamente', 'success');
        cerrarModalPrecios('nuevoPrecioModal');
        form.reset();
        
        // Recargar la lista de precios
        cargarPrecios();
        
    } catch (error) {
        console.error('❌ Error creando precio:', error);
        mostrarToastPrecios(`Error: ${error.message}`, 'error');
    }
}

/**
 * Abrir calculadora de precios
 */
function abrirCalculadoraPrecios() {
    const modal = document.getElementById('calculadoraPreciosModal');
    if (modal) {
        // Limpiar formulario
        document.getElementById('calculadoraPreciosForm').reset();
        document.getElementById('resultadoCalculoPrecio').style.display = 'none';
        
        // Mostrar modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}

/**
 * Calcular precio completo usando la API
 */
async function calcularPrecioCompleto() {
    try {
        const servicioId = document.getElementById('calcServicio').value;
        const recursoId = document.getElementById('calcRecurso').value;
        const fechaInicio = document.getElementById('calcFechaInicio').value;
        const fechaFin = document.getElementById('calcFechaFin').value;
        const cantidad = parseInt(document.getElementById('calcCantidad').value) || 1;
        const clienteId = document.getElementById('calcCliente').value;
        
        // Validaciones
        if (!servicioId && !recursoId) {
            mostrarToastPrecios('Debe seleccionar un servicio o un recurso', 'warning');
            return;
        }
        
        if (!fechaInicio || !fechaFin) {
            mostrarToastPrecios('Debe especificar fecha de inicio y fin', 'warning');
            return;
        }
        
        if (new Date(fechaInicio) >= new Date(fechaFin)) {
            mostrarToastPrecios('La fecha de fin debe ser posterior a la de inicio', 'warning');
            return;
        }
        
        // Preparar datos para el cálculo
        const calculoData = {
            servicio_id: servicioId ? parseInt(servicioId) : null,
            recurso_id: recursoId ? parseInt(recursoId) : null,
            fecha_inicio: fechaInicio,
            fecha_fin: fechaFin,
            cantidad: cantidad,
            cliente_id: clienteId ? parseInt(clienteId) : null
        };
        
        console.log('🔄 Calculando precio:', calculoData);
        
        const response = await fetch('/api/precios/calcular', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(calculoData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al calcular el precio');
        }
        
        const resultado = await response.json();
        
        // Mostrar resultado
        mostrarResultadoCalculo(resultado);
        
    } catch (error) {
        console.error('❌ Error calculando precio:', error);
        mostrarToastPrecios(`Error: ${error.message}`, 'error');
    }
}

/**
 * Mostrar resultado del cálculo de precio
 */
function mostrarResultadoCalculo(resultado) {
    document.getElementById('resultadoPrecioBase').textContent = formatearMoneda(resultado.precio_base);
    document.getElementById('resultadoPrecioFinal').textContent = formatearMoneda(resultado.precio_final);
    
    // Mostrar desglose
    let desgloseHtml = '';
    
    if (resultado.descuentos && resultado.descuentos.length > 0) {
        desgloseHtml += '<h6 class="text-success"><i class="fas fa-arrow-down me-2"></i>Descuentos</h6>';
        resultado.descuentos.forEach(descuento => {
            desgloseHtml += `<div class="d-flex justify-content-between"><span>${descuento.nombre}</span><span class="text-success">-${formatearMoneda(descuento.monto)}</span></div>`;
        });
    }
    
    if (resultado.recargos && resultado.recargos.length > 0) {
        desgloseHtml += '<h6 class="text-warning mt-2"><i class="fas fa-arrow-up me-2"></i>Recargos</h6>';
        resultado.recargos.forEach(recargo => {
            desgloseHtml += `<div class="d-flex justify-content-between"><span>${recargo.nombre}</span><span class="text-warning">+${formatearMoneda(recargo.monto)}</span></div>`;
        });
    }
    
    if (resultado.desglose) {
        desgloseHtml += '<hr><h6><i class="fas fa-info-circle me-2"></i>Información Adicional</h6>';
        desgloseHtml += `<div class="d-flex justify-content-between"><span>Duración</span><span>${resultado.desglose.duracion_horas?.toFixed(2)} horas</span></div>`;
    }
    
    document.getElementById('desgloseCalculoPrecio').innerHTML = desgloseHtml;
    document.getElementById('resultadoCalculoPrecio').style.display = 'block';
    
    mostrarToastPrecios('Precio calculado exitosamente', 'success');
}

/**
 * Cargar estadísticas de precios
 */
async function cargarEstadisticasPrecios() {
    try {
        const response = await fetch('/api/precios/estadisticas/general');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const estadisticas = await response.json();
        mostrarEstadisticasPrecios(estadisticas);
        
    } catch (error) {
        console.error('❌ Error cargando estadísticas:', error);
        mostrarToastPrecios('Error cargando estadísticas', 'error');
    }
}

/**
 * Mostrar estadísticas de precios
 */
function mostrarEstadisticasPrecios(estadisticas) {
    document.getElementById('totalPrecios').textContent = estadisticas.total_precios || 0;
    document.getElementById('preciosActivos').textContent = estadisticas.precios_activos || 0;
    document.getElementById('precioPromedio').textContent = formatearMoneda(estadisticas.precio_promedio || 0);
    
    const rango = estadisticas.precio_maximo && estadisticas.precio_minimo 
        ? `${formatearMoneda(estadisticas.precio_minimo)} - ${formatearMoneda(estadisticas.precio_maximo)}`
        : '-';
    document.getElementById('rangoPrecio').textContent = rango;
    
    // Mostrar el container de estadísticas
    document.getElementById('estadisticasPreciosContainer').style.display = 'block';
    
    mostrarToastPrecios('Estadísticas actualizadas', 'success');
}

/**
 * Aplicar filtros a los precios
 */
function aplicarFiltrosPrecios() {
    const tipo = document.getElementById('filtroTipoPrecio').value;
    const moneda = document.getElementById('filtroMoneda').value;
    const estado = document.getElementById('filtroEstado').value;
    const precioMin = parseFloat(document.getElementById('filtroPrecioMin').value) || null;
    const precioMax = parseFloat(document.getElementById('filtroPrecioMax').value) || null;
    
    let preciosFiltrados = [...preciosData];
    
    if (tipo) {
        preciosFiltrados = preciosFiltrados.filter(p => p.tipo_precio === tipo);
    }
    
    if (moneda) {
        preciosFiltrados = preciosFiltrados.filter(p => p.moneda === moneda);
    }
    
    if (estado !== '') {
        const activo = estado === 'true';
        preciosFiltrados = preciosFiltrados.filter(p => p.activo === activo);
    }
    
    if (precioMin !== null) {
        preciosFiltrados = preciosFiltrados.filter(p => p.precio_base >= precioMin);
    }
    
    if (precioMax !== null) {
        preciosFiltrados = preciosFiltrados.filter(p => p.precio_base <= precioMax);
    }
    
    displayPreciosList(preciosFiltrados);
    
    console.log(`📊 Filtros aplicados: ${preciosFiltrados.length} de ${preciosData.length} precios`);
}

// ========================================
// FUNCIONES AUXILIARES
// ========================================

/**
 * Mostrar indicador de carga
 */
function mostrarCargandoPrecios(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2">Cargando precios...</p>
            </div>
        `;
    }
}

/**
 * Mostrar mensaje de error
 */
function mostrarErrorPrecios(containerId, mensaje) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger text-center" role="alert">
                <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                <h5>Error</h5>
                <p>${mensaje}</p>
                <button class="btn btn-outline-danger" onclick="cargarPrecios()">
                    <i class="fas fa-sync me-2"></i>Reintentar
                </button>
            </div>
        `;
    }
}

/**
 * Mostrar toast de notificación
 */
function mostrarToastPrecios(mensaje, tipo = 'info') {
    // Reutilizar la función existente de la aplicación principal
    if (window.app && window.app.showNotification) {
        window.app.showNotification(mensaje, tipo);
    } else {
        console.log(`${tipo.toUpperCase()}: ${mensaje}`);
        
        // Crear un toast básico si no existe la función principal
        const toastContainer = document.getElementById('toastContainer') || createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${tipo === 'error' ? 'danger' : tipo === 'warning' ? 'warning' : tipo === 'success' ? 'success' : 'info'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${mensaje}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remover el toast después de que se oculte
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
}

/**
 * Crear contenedor de toasts si no existe
 */
function createToastContainer() {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
    }
    return container;
}

/**
 * Cerrar modal
 */
function cerrarModalPrecios(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
    }
}

/**
 * Duplicar precio (funcionalidad avanzada)
 */
async function duplicarPrecioFunc(id) {
    try {
        const response = await fetch(`/api/precios/${id}/duplicar`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Error al duplicar el precio');
        }
        
        mostrarToastPrecios('Precio duplicado exitosamente', 'success');
        cargarPrecios();
        
    } catch (error) {
        console.error('❌ Error duplicando precio:', error);
        mostrarToastPrecios('Error al duplicar el precio', 'error');
    }
}

// ========================================
// FUNCIONES DE GESTIÓN DE PRECIOS
// ========================================

/**
 * Ver detalle completo de un precio
 */
async function verDetallePrecio(id) { 
    try {
        console.log('🔍 Obteniendo detalle del precio:', id);
        
        const response = await fetch(`/api/precios/${id}`);
        if (!response.ok) {
            throw new Error('Error al obtener el precio');
        }
        
        const precio = await response.json();
        
        // Crear modal de detalle
        const modalHtml = `
            <div class="modal fade" id="detallePrecioModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-tag me-2"></i>Detalle del Precio
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Información Básica</h6>
                                    <p><strong>Nombre:</strong> ${precio.nombre}</p>
                                    <p><strong>Descripción:</strong> ${precio.descripcion || 'Sin descripción'}</p>
                                    <p><strong>Tipo:</strong> ${getTipoPrecioBadge(precio.tipo_precio)}</p>
                                    <p><strong>Precio Base:</strong> ${formatearMoneda(precio.precio_base, precio.moneda)}</p>
                                    <p><strong>Moneda:</strong> ${precio.moneda}</p>
                                    <p><strong>Estado:</strong> ${precio.activo ? '<span class="badge bg-success">Activo</span>' : '<span class="badge bg-secondary">Inactivo</span>'}</p>
                                    <p><strong>Prioridad:</strong> ${precio.prioridad}</p>
                                </div>
                                <div class="col-md-6">
                                    <h6>Configuración</h6>
                                    <p><strong>Servicio ID:</strong> ${precio.servicio_id || 'No aplica'}</p>
                                    <p><strong>Recurso ID:</strong> ${precio.recurso_id || 'No aplica'}</p>
                                    <p><strong>Fecha Inicio:</strong> ${precio.fecha_inicio || 'Sin límite'}</p>
                                    <p><strong>Fecha Fin:</strong> ${precio.fecha_fin || 'Sin límite'}</p>
                                    <p><strong>Cantidad Mín:</strong> ${precio.cantidad_minima || 'Sin límite'}</p>
                                    <p><strong>Cantidad Máx:</strong> ${precio.cantidad_maxima || 'Sin límite'}</p>
                                    <p><strong>Días Semana:</strong> ${precio.dias_semana || 'Todos los días'}</p>
                                    <p><strong>Hora Inicio:</strong> ${precio.hora_inicio || 'Todo el día'}</p>
                                    <p><strong>Hora Fin:</strong> ${precio.hora_fin || 'Todo el día'}</p>
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-12">
                                    <h6>Metadatos</h6>
                                    <pre class="bg-light p-2 rounded">${JSON.stringify(precio.metadatos || {}, null, 2)}</pre>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                            <button type="button" class="btn btn-primary" onclick="editarPrecio(${precio.id})">
                                <i class="fas fa-edit me-2"></i>Editar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Agregar modal al DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Mostrar modal
        const modal = document.getElementById('detallePrecioModal');
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Limpiar modal después de cerrar
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
        
        mostrarToastPrecios('Detalle del precio cargado', 'success');
        
    } catch (error) {
        console.error('❌ Error obteniendo detalle:', error);
        mostrarToastPrecios(`Error: ${error.message}`, 'error');
    }
}

/**
 * Editar un precio existente
 */
async function editarPrecio(id) { 
    try {
        console.log('✏️ Editando precio:', id);
        
        // Obtener datos del precio
        const response = await fetch(`/api/precios/${id}`);
        if (!response.ok) {
            throw new Error('Error al obtener el precio');
        }
        
        const precio = await response.json();
        
        // Cerrar modal de detalle si está abierto
        const detalleModal = document.getElementById('detallePrecioModal');
        if (detalleModal) {
            const bsModal = bootstrap.Modal.getInstance(detalleModal);
            if (bsModal) bsModal.hide();
        }
        
        // ✅ Poblar formulario de edición con verificaciones robustas
        const setFieldValue = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = value;
                } else {
                    element.value = value || '';
                }
            } else {
                console.warn(`⚠️ Campo no encontrado: ${id}`);
            }
        };
        
        setFieldValue('nuevoPrecioServicio', precio.servicio_id);
        setFieldValue('nuevoPrecioRecurso', precio.recurso_id);
        setFieldValue('nuevoPrecioTipo', precio.tipo_precio);
        setFieldValue('nuevoPrecioNombre', precio.nombre);
        setFieldValue('nuevoPrecioDescripcion', precio.descripcion);
        setFieldValue('nuevoPrecioPrecio', precio.precio_base);
        setFieldValue('nuevoPrecioMoneda', precio.moneda);
        setFieldValue('nuevoPrecioActivo', precio.activo);
        setFieldValue('nuevoPrecioPrioridad', precio.prioridad);
        setFieldValue('nuevoPrecioFechaInicio', precio.fecha_inicio);
        setFieldValue('nuevoPrecioFechaFin', precio.fecha_fin);
        setFieldValue('nuevoPrecioCantidadMin', precio.cantidad_minima);
        setFieldValue('nuevoPrecioCantidadMax', precio.cantidad_maxima);
        setFieldValue('nuevoPrecioDiasSemana', precio.dias_semana);
        setFieldValue('nuevoPrecioHoraInicio', precio.hora_inicio);
        setFieldValue('nuevoPrecioHoraFin', precio.hora_fin);
        
        // ✅ Cambiar título del modal (con verificación)
        const modalTitle = document.querySelector('#nuevoPrecioModal .modal-title');
        if (modalTitle) {
            modalTitle.innerHTML = '<i class="fas fa-edit me-2"></i>Editar Precio';
        } else {
            console.warn('⚠️ No se encontró el título del modal');
        }
        
        // ✅ Cambiar botones del modal para modo edición
        const modalFooter = document.querySelector('#nuevoPrecioModal .modal-footer');
        if (modalFooter) {
            modalFooter.innerHTML = `
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="fas fa-times me-2"></i>Anular
                </button>
                <button type="button" class="btn btn-primary" onclick="actualizarPrecio(${id})">
                    <i class="fas fa-save me-2"></i>Aceptar Cambios
                </button>
            `;
            
            // ✅ Asegurar que los botones sean visibles
            modalFooter.style.display = 'flex';
            modalFooter.style.justifyContent = 'flex-end';
            modalFooter.style.gap = '0.5rem';
            modalFooter.style.padding = '1rem';
            modalFooter.style.borderTop = '1px solid #dee2e6';
            modalFooter.style.background = '#f8f9fa';
        } else {
            // Fallback: cambiar solo el botón de submit si no hay footer
            const submitBtn = document.querySelector('#nuevoPrecioForm button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Actualizar Precio';
                submitBtn.onclick = (e) => {
                    e.preventDefault();
                    actualizarPrecio(id);
                };
            } else {
                console.warn('⚠️ No se encontró el botón de submit ni el footer');
            }
        }
        
        // ✅ SOLUCIÓN DEFINITIVA: Crear modal dinámico para evitar conflictos
        abrirModalEdicionPrecio(id);
        
    } catch (error) {
        console.error('❌ Error editando precio:', error);
        mostrarToastPrecios(`Error: ${error.message}`, 'error');
    }
}

/**
 * Actualizar un precio existente
 */
async function actualizarPrecio(id) {
    try {
        const form = document.getElementById('nuevoPrecioForm');
        
        // Validar formulario
        const servicioId = document.getElementById('nuevoPrecioServicio').value;
        const recursoId = document.getElementById('nuevoPrecioRecurso').value;
        
        if (!servicioId && !recursoId) {
            mostrarToastPrecios('Debe seleccionar un servicio o un recurso', 'warning');
            return;
        }
        
        if (servicioId && recursoId) {
            mostrarToastPrecios('No puede seleccionar servicio y recurso al mismo tiempo', 'warning');
            return;
        }
        
        // Preparar datos del precio
        const precioData = {
            servicio_id: servicioId ? parseInt(servicioId) : null,
            recurso_id: recursoId ? parseInt(recursoId) : null,
            tipo_precio: document.getElementById('nuevoPrecioTipo').value,
            nombre: document.getElementById('nuevoPrecioNombre').value,
            descripcion: document.getElementById('nuevoPrecioDescripcion').value || null,
            precio_base: parseFloat(document.getElementById('nuevoPrecioPrecio').value),
            moneda: document.getElementById('nuevoPrecioMoneda').value,
            activo: document.getElementById('nuevoPrecioActivo').checked,
            prioridad: parseInt(document.getElementById('nuevoPrecioPrioridad').value) || 0,
            fecha_inicio: document.getElementById('nuevoPrecioFechaInicio').value || null,
            fecha_fin: document.getElementById('nuevoPrecioFechaFin').value || null,
            cantidad_minima: document.getElementById('nuevoPrecioCantidadMin').value ? parseInt(document.getElementById('nuevoPrecioCantidadMin').value) : null,
            cantidad_maxima: document.getElementById('nuevoPrecioCantidadMax').value ? parseInt(document.getElementById('nuevoPrecioCantidadMax').value) : null,
            hora_inicio: document.getElementById('nuevoPrecioHoraInicio').value || null,
            hora_fin: document.getElementById('nuevoPrecioHoraFin').value || null,
            dias_semana: document.getElementById('nuevoPrecioDiasSemana').value || null
        };
        
        console.log('🔄 Actualizando precio:', precioData);
        
        const response = await fetch(`/api/precios/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(precioData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al actualizar el precio');
        }
        
        mostrarToastPrecios('Precio actualizado exitosamente', 'success');
        
        // Cerrar modal
        const modal = document.getElementById('nuevoPrecioModal');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        }
        
        // Recargar la lista de precios
        cargarPrecios();
        
    } catch (error) {
        console.error('❌ Error actualizando precio:', error);
        mostrarToastPrecios(`Error: ${error.message}`, 'error');
    }
}

/**
 * Abrir modal de edición dinámico para evitar conflictos de z-index
 */
function abrirModalEdicionPrecio(id) {
    // ✅ Crear modal dinámico con z-index alto
    const modalHtml = `
        <div class="modal fade show" id="modalEdicionDinamico" style="display: block; z-index: 10000;" aria-modal="true">
            <div class="modal-backdrop fade show" style="z-index: 9999;"></div>
            <div class="modal-dialog modal-lg modal-dialog-centered" style="z-index: 10001;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-edit me-2"></i>Editar Precio
                        </h5>
                        <button type="button" class="btn-close" onclick="cerrarModalEdicionDinamico()"></button>
                    </div>
                    <div class="modal-body">
                        <div id="contenidoEdicion">
                            <div class="d-flex justify-content-center">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Cargando...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="cerrarModalEdicionDinamico()">
                            <i class="fas fa-times me-2"></i>Anular
                        </button>
                        <button type="button" class="btn btn-primary" onclick="guardarEdicionDinamica(${id})">
                            <i class="fas fa-save me-2"></i>Aceptar Cambios
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ✅ Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // ✅ Cargar contenido del formulario
    cargarFormularioEdicion(id);
    
    // ✅ Prevenir scroll del body
    document.body.style.overflow = 'hidden';
}

/**
 * Cerrar modal de edición dinámico
 */
function cerrarModalEdicionDinamico() {
    const modal = document.getElementById('modalEdicionDinamico');
    if (modal) {
        modal.remove();
    }
    
    // ✅ Restaurar scroll del body
    document.body.style.overflow = '';
}

/**
 * Cargar formulario de edición en el modal dinámico
 */
async function cargarFormularioEdicion(id) {
    try {
        console.log('🔄 Cargando datos para edición:', id);
        
        // ✅ Obtener datos del precio
        const response = await fetch(`/api/precios/${id}`);
        if (!response.ok) {
            throw new Error('Error al obtener el precio');
        }
        const precio = await response.json();
        
        // ✅ Generar formulario HTML
        const formularioHtml = `
            <form id="formEdicionDinamico">
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Servicio</label>
                            <select class="form-select" id="editServicio">
                                <option value="">Seleccionar servicio...</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Recurso</label>
                            <select class="form-select" id="editRecurso">
                                <option value="">Seleccionar recurso...</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Tipo de Precio</label>
                            <select class="form-select" id="editTipo">
                                <option value="base">Base</option>
                                <option value="descuento">Descuento</option>
                                <option value="recargo">Recargo</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Moneda</label>
                            <select class="form-select" id="editMoneda">
                                <option value="EUR">EUR</option>
                                <option value="USD">USD</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="mb-3">
                            <label class="form-label">Nombre</label>
                            <input type="text" class="form-control" id="editNombre" value="${precio.nombre || ''}">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Precio Base</label>
                            <input type="number" class="form-control" id="editPrecio" value="${precio.precio_base || ''}" step="0.01">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Prioridad</label>
                            <input type="number" class="form-control" id="editPrioridad" value="${precio.prioridad || 1}">
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="editActivo" ${precio.activo ? 'checked' : ''}>
                                <label class="form-check-label" for="editActivo">
                                    Activo
                                </label>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="mb-3">
                            <label class="form-label">Descripción</label>
                            <textarea class="form-control" id="editDescripcion" rows="3">${precio.descripcion || ''}</textarea>
                        </div>
                    </div>
                </div>
            </form>
        `;
        
        // ✅ Insertar formulario en el modal
        document.getElementById('contenidoEdicion').innerHTML = formularioHtml;
        
        // ✅ Cargar datos auxiliares y preseleccionar valores
        await cargarDatosAuxiliaresEdicion();
        preseleccionarValoresEdicion(precio);
        
        console.log('✅ Formulario de edición cargado');
        
    } catch (error) {
        console.error('❌ Error cargando formulario:', error);
        document.getElementById('contenidoEdicion').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error al cargar los datos: ${error.message}
            </div>
        `;
    }
}

/**
 * Cargar datos auxiliares para selects
 */
async function cargarDatosAuxiliaresEdicion() {
    try {
        const [serviciosResponse, recursosResponse] = await Promise.all([
            fetch('/servicios/'),
            fetch('/recursos/')
        ]);
        
        const servicios = await serviciosResponse.json();
        const recursos = await recursosResponse.json();
        
        // ✅ Poblar select de servicios
        const selectServicio = document.getElementById('editServicio');
        servicios.forEach(servicio => {
            const option = document.createElement('option');
            option.value = servicio.id;
            option.textContent = servicio.nombre;
            selectServicio.appendChild(option);
        });
        
        // ✅ Poblar select de recursos
        const selectRecurso = document.getElementById('editRecurso');
        recursos.forEach(recurso => {
            const option = document.createElement('option');
            option.value = recurso.id;
            option.textContent = recurso.nombre;
            selectRecurso.appendChild(option);
        });
        
    } catch (error) {
        console.error('❌ Error cargando datos auxiliares:', error);
    }
}

/**
 * Preseleccionar valores en el formulario
 */
function preseleccionarValoresEdicion(precio) {
    const setValue = (id, value) => {
        const element = document.getElementById(id);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = value;
            } else {
                element.value = value || '';
            }
        }
    };
    
    setValue('editServicio', precio.servicio_id);
    setValue('editRecurso', precio.recurso_id);
    setValue('editTipo', precio.tipo_precio);
    setValue('editMoneda', precio.moneda);
    setValue('editNombre', precio.nombre);
    setValue('editPrecio', precio.precio_base);
    setValue('editPrioridad', precio.prioridad);
    setValue('editActivo', precio.activo);
    setValue('editDescripcion', precio.descripcion);
}

/**
 * Guardar cambios del modal dinámico
 */
async function guardarEdicionDinamica(id) {
    try {
        console.log('💾 Guardando cambios precio:', id);
        
        // ✅ Recopilar datos del formulario
        const formData = {
            servicio_id: document.getElementById('editServicio')?.value || null,
            recurso_id: document.getElementById('editRecurso')?.value || null,
            tipo_precio: document.getElementById('editTipo')?.value,
            nombre: document.getElementById('editNombre')?.value,
            descripcion: document.getElementById('editDescripcion')?.value || '',
            precio_base: parseFloat(document.getElementById('editPrecio')?.value),
            moneda: document.getElementById('editMoneda')?.value,
            activo: document.getElementById('editActivo')?.checked || false,
            prioridad: parseInt(document.getElementById('editPrioridad')?.value) || 1
        };
        
        // ✅ Limpiar valores vacíos
        Object.keys(formData).forEach(key => {
            if (formData[key] === '' || formData[key] === 'null') {
                formData[key] = null;
            }
        });
        
        console.log('📄 Datos a enviar:', formData);
        
        // ✅ Enviar solicitud PUT
        const response = await fetch(`/api/precios/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al actualizar el precio');
        }
        
        console.log('✅ Precio actualizado exitosamente');
        
        // ✅ Cerrar modal
        cerrarModalEdicionDinamico();
        
        // ✅ Recargar lista de precios
        await cargarPrecios();
        
        mostrarToastPrecios('Precio actualizado exitosamente', 'success');
        
    } catch (error) {
        console.error('❌ Error guardando cambios:', error);
        mostrarToastPrecios(`Error: ${error.message}`, 'error');
    }
}

/**
 * Cambiar estado activo/inactivo de un precio
 */
async function togglePrecioEstado(id, activo) { 
    try {
        console.log('🔄 Cambiando estado del precio:', id, 'de', activo, 'a', !activo);
        
        // Primero obtener el precio actual para hacer un PUT completo
        const getPrecioResponse = await fetch(`/api/precios/${id}`);
        if (!getPrecioResponse.ok) {
            throw new Error('Error al obtener el precio actual');
        }
        const precioActual = await getPrecioResponse.json();
        
        // Actualizar solo el campo activo
        const datosActualizados = {
            ...precioActual,
            activo: !activo
        };
        
        const response = await fetch(`/api/precios/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datosActualizados)
        });
        
        if (!response.ok) {
            throw new Error('Error al cambiar el estado del precio');
        }
        
        const nuevoEstado = !activo ? 'activado' : 'desactivado';
        mostrarToastPrecios(`Precio ${nuevoEstado} exitosamente`, 'success');
        
        // Recargar la lista de precios
        cargarPrecios();
        
    } catch (error) {
        console.error('❌ Error cambiando estado:', error);
        mostrarToastPrecios(`Error: ${error.message}`, 'error');
    }
}

/**
 * Eliminar un precio
 */
async function eliminarPrecio(id) { 
    try {
        console.log('🗑️ Eliminando precio:', id);
        
        if (!confirm('¿Está seguro de que desea eliminar este precio? Esta acción no se puede deshacer.')) {
            return;
        }
        
        const response = await fetch(`/api/precios/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Error al eliminar el precio');
        }
        
        mostrarToastPrecios('Precio eliminado exitosamente', 'success');
        
        // Recargar la lista de precios
        cargarPrecios();
        
    } catch (error) {
        console.error('❌ Error eliminando precio:', error);
        mostrarToastPrecios(`Error: ${error.message}`, 'error');
    }
}

// ========================================
// INICIALIZACIÓN AUTOMÁTICA
// ========================================

// ✅ SOLUCIÓN: Inicialización limpia y única
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM cargado, iniciando sistema de precios...');
    initSistemaPrecios();
});

// También intentar inicializar si ya está cargado
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSistemaPrecios);
} else {
    // DOM ya está cargado
    console.log('🚀 DOM ya cargado, iniciando sistema de precios inmediatamente...');
    initSistemaPrecios();
}

console.log('✅ Módulo de Sistema de Precios completamente cargado');

// ========================================
// FUNCIONES DE PRUEBA PARA DEBUGGING
// ========================================

/**
 * Función de prueba para debuggear desde la consola del navegador
 */
window.testSistemaPrecios = function() {
    console.log('🧪 Iniciando prueba del sistema de precios...');
    
    // Verificar elementos del DOM
    const preciosTab = document.getElementById('precios-tab');
    const preciosContainer = document.getElementById('preciosContainer');
    
    console.log('🔍 Elementos encontrados:');
    console.log('  - Tab de precios:', !!preciosTab);
    console.log('  - Contenedor de precios:', !!preciosContainer);
    
    if (preciosTab) {
        console.log('  - Tab activa:', preciosTab.classList.contains('active'));
        console.log('  - Aria-selected:', preciosTab.getAttribute('aria-selected'));
    }
    
    // Verificar funciones disponibles
    console.log('🔧 Funciones disponibles:');
    console.log('  - cargarPrecios:', typeof cargarPrecios);
    console.log('  - displayPreciosList:', typeof displayPreciosList);
    console.log('  - initSistemaPrecios:', typeof initSistemaPrecios);
    
    // Verificar datos
    console.log('📊 Estado de datos:');
    console.log('  - preciosData:', preciosData);
    console.log('  - serviciosDataPrecios:', serviciosDataPrecios);
    console.log('  - recursosDataPrecios:', recursosDataPrecios);
    
    // Intentar cargar precios
    console.log('🔄 Intentando cargar precios...');
    try {
        cargarPrecios();
    } catch (error) {
        console.error('❌ Error en prueba:', error);
    }
    
    console.log('✅ Prueba completada');
};

/**
 * Función para forzar la carga de precios
 */
window.forzarCargaPrecios = function() {
    console.log('🚀 Forzando carga de precios...');
    cargarPrecios();
};

/**
 * Función para forzar la activación de la tab de precios
 */
window.activarTabPrecios = function() {
    console.log('🎯 Forzando activación de tab de precios...');
    
    // Activar la tab
    const preciosTab = document.getElementById('precios-tab');
    const preciosTabPane = document.getElementById('precios');
    
    if (preciosTab && preciosTabPane) {
        // Remover active de todas las tabs
        document.querySelectorAll('.nav-link').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('show', 'active'));
        
        // Activar la tab de precios
        preciosTab.classList.add('active');
        preciosTab.setAttribute('aria-selected', 'true');
        preciosTabPane.classList.add('show', 'active');
        
        console.log('✅ Tab de precios activada forzadamente');
        
        // ✅ SOLUCIÓN: Solo cargar precios (NO datos auxiliares)
        cargarPrecios();
    } else {
        console.error('❌ No se encontraron elementos de la tab de precios');
    }
};

/**
 * Función para debuggear los datos de precios
 */
window.debugPreciosData = function() {
    console.log('🔍 Debug de datos de precios:');
    console.log('  - preciosData:', preciosData);
    console.log('  - preciosData.length:', preciosData.length);
    
    if (preciosData.length > 0) {
        console.log('  - Primer precio:', preciosData[0]);
        console.log('  - Campos del primer precio:');
        console.log('    * id:', preciosData[0].id);
        console.log('    * nombre:', preciosData[0].nombre);
        console.log('    * tipo_precio:', preciosData[0].tipo_precio);
        console.log('    * precio_base:', preciosData[0].precio_base);
        console.log('    * moneda:', preciosData[0].moneda);
        console.log('    * activo:', preciosData[0].activo);
        console.log('    * prioridad:', preciosData[0].prioridad);
    }
    
    const container = document.getElementById('preciosContainer');
    console.log('  - Contenedor encontrado:', !!container);
    if (container) {
        console.log('  - HTML del contenedor:', container.innerHTML);
    }
};

console.log('🔧 Funciones de prueba disponibles:');
console.log('  - testSistemaPrecios() - Ejecutar prueba completa');
console.log('  - forzarCargaPrecios() - Forzar carga de precios');
console.log('  - activarTabPrecios() - Forzar activación de tab de precios');
console.log('  - debugPreciosData() - Debug de datos de precios');
