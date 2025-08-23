// Cliente Web para Sistema de Precios Dinámicos
class PreciosDinamicosApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentData = { services: [], resources: [], rules: [], clientes: [] };
        this.calculationHistory = [];
        this.maxHistoryItems = 10;
        this.notificationSettings = {
            confirmations: true,
            reminders: true,
            systemAlerts: true,
            autoDismiss: 5000
        };
        this.pendingReminders = [];
        this.tabsLoaded = {
            dashboard: false,
            calculator: false,
            history: false,
            quickRules: false,
            notifications: false,
            services: false,
            resources: false,
            reservas: false,
            calendario: false
        };
        
        // Propiedades del calendario
        this.calendario = {
            fechaActual: new Date(),
            vistaActual: 'mensual', // mensual, semanal, diaria
            reservas: [],
            filtros: {
                servicio: '',
                recurso: ''
            }
        };
        this.init();
    }

    async init() {
        try {
            console.log('🚀 Inicializando aplicación...');
            await this.checkApiConnection();
            this.setDefaultDates();
            await this.loadInitialData();
            this.populateSelectors();
            this.setupEventListeners();
            await this.loadDashboard();
            this.loadHistoryFromStorage();
            this.loadNotificationSettings();
            this.startNotificationSystem();
            
            // Cargar lista de reglas si estamos en la pestaña de gestión
            if (document.getElementById('rulesListContainer')) {
                await this.refreshRulesList();
            }
            
            // Verificar que los contenedores existan
            console.log('🔍 Verificando contenedores en init...');
            const servicesContainer = document.getElementById('servicesContainer');
            const resourcesContainer = document.getElementById('resourcesContainer');
            console.log('🔍 servicesContainer encontrado:', servicesContainer);
            console.log('🔍 resourcesContainer encontrado:', resourcesContainer);
            
            // Cargar servicios y recursos solo cuando se haga clic en las pestañas
            // const services = await this.apiCall('/servicios/');
            // const resources = await this.apiCall('/recursos/');
            
            // this.displayServicesList(services);
            // this.displayResourcesList(resources);
            
            // Configurar eventos de pestañas
            this.setupTabEvents();
            
            console.log('✅ Aplicación inicializada completamente');
        } catch (err) {
            console.error("Error inicializando app:", err);
        }
    }

    setupTabEvents() {
        console.log('🔧 Configurando eventos de pestañas...');
        
        // Estado para evitar cargar datos múltiples veces
        this.tabsLoaded = {
            services: false,
            resources: false,
            reservas: false
        };
        
        console.log('🔍 Estado inicial de tabsLoaded:', this.tabsLoaded);
        
        // Verificar el estado inicial de las pestañas
        const servicesPane = document.getElementById('services');
        const resourcesPane = document.getElementById('resources');
        console.log('🔍 Estado inicial de pestañas:');
        console.log('  - services pane:', servicesPane?.classList.toString());
        console.log('  - resources pane:', resourcesPane?.classList.toString());
        
        // Evento para pestaña de servicios
        const servicesTab = document.getElementById('services-tab');
        console.log('🔍 Pestaña de servicios encontrada:', servicesTab);
        if (servicesTab) {
            servicesTab.addEventListener('click', async (e) => {
                console.log('📋 Pestaña de servicios activada');
                console.log('🔍 Estado actual de tabsLoaded:', this.tabsLoaded);
                console.log('🔍 Evento de clic en pestaña de servicios:', e);
                
                // Cargar datos si no se han cargado antes
                if (!this.tabsLoaded.services) {
                    console.log('🔄 Cargando servicios...');
                    await this.refreshServicesList();
                    this.tabsLoaded.services = true;
                    console.log('✅ Servicios cargados y marcados como cargados');
                } else {
                    console.log('ℹ️ Servicios ya cargados, no se recargan');
                }
                
                // Verificar el estado de la pestaña después del clic
                setTimeout(() => {
                    const servicesPane = document.getElementById('services');
                    const resourcesPane = document.getElementById('resources');
                    console.log('🔍 Estado de pestañas después del clic:');
                    console.log('  - services pane:', servicesPane?.classList.toString());
                    console.log('  - resources pane:', resourcesPane?.classList.toString());
                }, 100);
            });
        } else {
            console.error('❌ No se encontró la pestaña de servicios');
        }
        
        // Evento para pestaña de recursos
        const resourcesTab = document.getElementById('resources-tab');
        console.log('🔍 Pestaña de recursos encontrada:', resourcesTab);
        if (resourcesTab) {
            resourcesTab.addEventListener('click', async (e) => {
                console.log('🏢 Pestaña de recursos activada');
                console.log('🔍 Estado actual de tabsLoaded:', this.tabsLoaded);
                console.log('🔍 Evento de clic en pestaña de recursos:', e);
                
                // Cargar datos si no se han cargado antes
                if (!this.tabsLoaded.resources) {
                    console.log('🔄 Cargando recursos...');
                    await this.refreshResourcesList();
                    this.tabsLoaded.resources = true;
                    console.log('✅ Recursos cargados y marcados como cargados');
                } else {
                    console.log('ℹ️ Recursos ya cargados, no se recargan');
                }
                
                // Verificar el estado de la pestaña después del clic
                setTimeout(() => {
                    const servicesPane = document.getElementById('services');
                    const resourcesPane = document.getElementById('resources');
                    console.log('🔍 Estado de pestañas después del clic:');
                    console.log('  - services pane:', servicesPane?.classList.toString());
                    console.log('  - resources pane:', resourcesPane?.classList.toString());
                }, 100);
            });
        } else {
            console.error('❌ No se encontró la pestaña de recursos');
        }

        // Evento para pestaña de reservas
        document.getElementById('reservas-tab')?.addEventListener('click', () => {
            if (!this.tabsLoaded.reservas) {
                this.refreshReservasList();
                this.tabsLoaded.reservas = true;
            }
        });

        // Evento para la pestaña del calendario
        document.getElementById('calendario-tab')?.addEventListener('click', () => {
            if (!this.tabsLoaded.calendario) {
                this.inicializarCalendario();
                this.tabsLoaded.calendario = true;
            }
        });

        // Evento para pestaña de notificaciones
        const notificationsTab = document.getElementById('notifications-tab');
        console.log('🔍 Pestaña de notificaciones encontrada:', notificationsTab);
        if (notificationsTab) {
            notificationsTab.addEventListener('click', async (e) => {
                console.log('🔔 Pestaña de notificaciones activada');
                
                // Cargar datos si no se han cargado antes
                if (!this.tabsLoaded.notifications) {
                    await this.refreshNotificationSettings();
                    this.tabsLoaded.notifications = true;
                }
            });
        } else {
            console.error('❌ No se encontró la pestaña de notificaciones');
        }
        
        console.log('✅ Eventos de pestañas configurados');
    }

    async checkApiConnection() {
        try {
            const response = await this.apiCall('/health');
            if (response.status === 'healthy') {
                document.getElementById('apiStatus').innerHTML = 
                    '<span class="text-success">✅ Conectado a la API</span>';
            } else {
                document.getElementById('apiStatus').innerHTML = 
                    '<span class="text-warning">⚠️ API respondiendo pero con problemas</span>';
            }
        } catch (error) {
            document.getElementById('apiStatus').innerHTML = 
                '<span class="text-danger">❌ No se puede conectar a la API</span>';
        }
    }

    setDefaultDates() {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        document.getElementById('calcDate').value = tomorrow.toISOString().split('T')[0];
        document.getElementById('calcTime').value = '10:00';
    }

    async loadInitialData() {
        try {
            // Cargar servicios
            const serviciosResponse = await this.apiCall('/servicios/');
            this.currentData.services = serviciosResponse || [];

            // Cargar recursos
            const recursosResponse = await this.apiCall('/recursos/');
            this.currentData.resources = recursosResponse || [];

            // Cargar clientes
            const clientesResponse = await this.apiCall('/clientes/');
            this.currentData.clientes = clientesResponse || [];

            // Cargar reglas
            const reglasResponse = await this.apiCall('/precios-dinamicos/reglas');
            this.currentData.rules = reglasResponse || [];

        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
            this.showAlert('Error cargando datos iniciales', 'danger');
        }
    }

    populateSelectors() {
        console.log('🔍 populateSelectors llamado');
        console.log('🔍 Servicios disponibles:', this.currentData.services.length);
        console.log('🔍 Recursos disponibles:', this.currentData.resources.length);
        
        // Poblar selector de servicios
        const serviceSelect = document.getElementById('calcService');
        if (!serviceSelect) {
            console.error('❌ No se encontró el selector de servicios');
            return;
        }
        
        // Limpiar completamente el selector antes de poblar
        serviceSelect.innerHTML = '';
        
        // Agregar opción por defecto
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Seleccionar servicio...';
        serviceSelect.appendChild(defaultOption);
        
        // Agregar servicios
        this.currentData.services.forEach(service => {
            const option = document.createElement('option');
            option.value = service.id;
            option.textContent = `${service.nombre} - ${this.formatCurrency(service.precio_base)}`;
            serviceSelect.appendChild(option);
        });
        
        console.log('🔍 Selector de servicios poblado con', serviceSelect.children.length, 'opciones');

        // Poblar selector de recursos
        const resourceSelect = document.getElementById('calcResource');
        if (!resourceSelect) {
            console.error('❌ No se encontró el selector de recursos');
            return;
        }
        
        // Limpiar completamente el selector antes de poblar
        resourceSelect.innerHTML = '';
        
        // Agregar opción por defecto
        const defaultResourceOption = document.createElement('option');
        defaultResourceOption.value = '';
        defaultResourceOption.textContent = 'Seleccionar recurso...';
        resourceSelect.appendChild(defaultResourceOption);
        
        // Agregar recursos
        this.currentData.resources.forEach(resource => {
            const option = document.createElement('option');
            option.value = resource.id;
            option.textContent = `${resource.nombre} (${resource.tipo})`;
            resourceSelect.appendChild(option);
        });
        
        console.log('🔍 Selector de recursos poblado con', resourceSelect.children.length, 'opciones');
    }

    setupEventListeners() {
        // Calculadora de precios
        document.getElementById('priceCalculatorForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculatePrice();
        });

        // Reglas rápidas
        document.getElementById('horaPicoForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createHoraPicoRule();
        });

        document.getElementById('anticipacionForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createAnticipacionRule();
        });

        document.getElementById('finSemanaForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createFinSemanaRule();
        });

        // Formularios de servicios y recursos
        document.getElementById('newServiceForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createNewService();
        });

        document.getElementById('newResourceForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createNewResource();
        });

        // Configuración de notificaciones
        document.getElementById('generalNotificationsForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveNotificationSettings();
        });

                 // Formulario de nueva reserva
         document.getElementById('newReservaForm')?.addEventListener('submit', (e) => {
             e.preventDefault();
             this.updateExistingReserva();
         });

        // Botón de filtrar reservas
        document.getElementById('btnFiltrarReservas')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.filterReservas();
        });

        // Cambiar duración según el servicio seleccionado
        document.getElementById('calcService').addEventListener('change', (e) => {
            this.updateDurationUnit(e.target.value);
        });
        
        // Validar duración en tiempo real para habitaciones
        document.getElementById('calcDuration').addEventListener('input', (e) => {
            const unit = document.getElementById('calcDurationUnit').value;
            if (unit === 'nights') {
                const value = parseFloat(e.target.value);
                if (value % 1 !== 0) {
                    // Mostrar advertencia pero permitir escribir
                    const helpText = document.getElementById('durationHelp');
                    if (helpText) {
                        helpText.textContent = '⚠️ Las habitaciones solo se alquilan por noches completas';
                        helpText.className = 'form-text text-warning';
                    }
                } else {
                    // Restaurar texto normal
                    const helpText = document.getElementById('durationHelp');
                    if (helpText) {
                        helpText.textContent = 'Habitaciones se alquilan por noches completas (1-30 noches)';
                        helpText.className = 'form-text text-muted';
                    }
                }
            }
        });

        // Event listeners para configuración de notificaciones
        this.setupNotificationEventListeners();
        
        // Event listeners para limpiar mensajes en el formulario de reservas
        this.setupReservaFormEventListeners();
    }

    setupNotificationEventListeners() {
        // Cambios en tiempo real en la configuración
        document.getElementById('confirmationsEnabled')?.addEventListener('change', (e) => {
            this.updateNotificationSettings({ confirmations: e.target.checked });
        });

        document.getElementById('remindersEnabled')?.addEventListener('change', (e) => {
            this.updateNotificationSettings({ reminders: e.target.checked });
        });

        document.getElementById('systemAlertsEnabled')?.addEventListener('change', (e) => {
            this.updateNotificationSettings({ systemAlerts: e.target.checked });
        });

        document.getElementById('autoDismissTime')?.addEventListener('change', (e) => {
            this.updateNotificationSettings({ autoDismiss: parseInt(e.target.value) });
        });

        // Configuración avanzada
        document.getElementById('soundEnabled')?.addEventListener('change', (e) => {
            this.updateNotificationSettings({ sound: e.target.checked });
        });

        document.getElementById('desktopNotificationsEnabled')?.addEventListener('change', (e) => {
            this.updateNotificationSettings({ desktopNotifications: e.target.checked });
        });

        document.getElementById('priorityNotificationsEnabled')?.addEventListener('change', (e) => {
            this.updateNotificationSettings({ priorityNotifications: e.target.checked });
        });
    }

    setupReservaFormEventListeners() {
        // Limpiar mensajes cuando se cambien los campos del formulario
        const reservaFields = [
            'newReservaCliente',
            'newReservaServicio', 
            'newReservaRecurso',
            'newReservaFechaInicio',
            'newReservaFechaFin',
            'newReservaEstado'
        ];
        
        reservaFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('change', () => {
                    this.clearReservaMessage();
                });
                
                field.addEventListener('input', () => {
                    this.clearReservaMessage();
                });
            }
        });
    }

    updateDurationUnit(serviceId) {
        const service = this.currentData.services.find(s => s.id == serviceId);
        const durationUnitSelect = document.getElementById('calcDurationUnit');
        const durationInput = document.getElementById('calcDuration');
        const durationHelp = document.getElementById('durationHelp');
        const participantsSelect = document.getElementById('calcParticipants');
        
        if (service) {
            if (service.nombre.toLowerCase().includes('habitación') || 
                service.nombre.toLowerCase().includes('alquiler')) {
                // Para servicios de habitación, usar noches
                durationUnitSelect.value = 'nights';
                durationInput.max = '30'; // Máximo 30 noches
                durationInput.step = '1'; // Solo números enteros
                durationInput.min = '1';  // Mínimo 1 noche
                durationInput.value = '1';
                
                if (durationHelp) {
                    durationHelp.textContent = 'Habitaciones se alquilan por noches completas (1-30 noches)';
                }
                
                // Ajustar participantes según el tipo de habitación
                if (service.nombre.toLowerCase().includes('individual')) {
                    // Habitación individual: máximo 1 persona
                    if (participantsSelect) {
                        participantsSelect.value = '1';
                        // Deshabilitar opción de 2 participantes
                        const option2 = participantsSelect.querySelector('option[value="2"]');
                        if (option2) {
                            option2.disabled = true;
                            option2.textContent = '2 (No disponible para habitación individual)';
                        }
                    }
                } else if (service.nombre.toLowerCase().includes('doble')) {
                    // Habitación doble: máximo 2 personas
                    if (participantsSelect) {
                        // Habilitar opción de 2 participantes
                        const option2 = participantsSelect.querySelector('option[value="2"]');
                        if (option2) {
                            option2.disabled = false;
                            option2.textContent = '2';
                        }
                    }
                }
            } else {
                // Para otros servicios, usar horas
                durationUnitSelect.value = 'hours';
                durationInput.max = '168'; // Máximo 1 semana
                durationInput.step = '0.5'; // Permite medias horas
                durationInput.min = '0.5';  // Mínimo 30 minutos
                durationInput.value = '1';
                
                if (durationHelp) {
                    durationHelp.textContent = 'Servicios por horas (0.5-168 horas)';
                }
                
                // Habilitar todas las opciones de participantes para otros servicios
                if (participantsSelect) {
                    const option2 = participantsSelect.querySelector('option[value="2"]');
                    if (option2) {
                        option2.disabled = false;
                        option2.textContent = '2';
                    }
                }
            }
        } else {
            // Servicio no seleccionado
            if (durationHelp) {
                durationHelp.textContent = 'Selecciona un servicio para ver las opciones de duración';
            }
            
            // Habilitar todas las opciones de participantes
            if (participantsSelect) {
                const option2 = participantsSelect.querySelector('option[value="2"]');
                if (option2) {
                    option2.disabled = false;
                    option2.textContent = '2';
                }
            }
        }
    }

    async loadDashboard() {
        try {
            const stats = await this.apiCall('/precios-dinamicos/estadisticas/reglas');
            this.updateDashboardStats(stats);
            
            const recentRules = await this.apiCall('/precios-dinamicos/reglas');
            this.updateRecentRulesList(recentRules);
        } catch (error) {
            console.error('Error cargando dashboard:', error);
        }
    }

    updateDashboardStats(stats) {
        if (stats) {
            document.getElementById('totalRules').textContent = stats.total_reglas || 0;
            document.getElementById('activeRules').textContent = stats.reglas_activas || 0;
            document.getElementById('totalServices').textContent = this.currentData.services.length;
            document.getElementById('totalResources').textContent = this.currentData.resources.length;
        }
    }

    updateRecentRulesList(rules) {
        const container = document.getElementById('recentRulesList');
        
        if (!rules || rules.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-info-circle fa-2x mb-3"></i>
                    <p>No hay reglas de precio creadas aún</p>
                </div>
            `;
            return;
        }

        container.innerHTML = rules.slice(0, 5).map(rule => `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">${rule.nombre}</h6>
                    <small class="text-muted">${rule.tipo_regla} - ${rule.tipo_modificador}</small>
                </div>
                <span class="badge bg-${rule.activa ? 'success' : 'secondary'} rounded-pill">
                    ${rule.activa ? 'Activa' : 'Inactiva'}
                </span>
            </div>
        `).join('');
    }

    async calculatePrice() {
        try {
            // Validar que se hayan seleccionado servicio y recurso
            const servicioId = document.getElementById('calcService').value;
            const recursoId = document.getElementById('calcResource').value;
            
            if (!servicioId || !recursoId) {
                this.showAlert('Por favor selecciona un servicio y un recurso', 'warning');
                return;
            }
            
            // Validar que la fecha sea válida
            const fecha = document.getElementById('calcDate').value;
            if (!fecha) {
                this.showAlert('Por favor selecciona una fecha válida', 'warning');
                return;
            }
            
            // Validar que la hora sea válida
            const hora = document.getElementById('calcTime').value;
            if (!hora) {
                this.showAlert('Por favor selecciona una hora válida', 'warning');
                return;
            }
            
            // Validar que la duración sea válida
            const duracion = this.getDurationInHours();
            if (duracion <= 0 || isNaN(duracion)) {
                this.showAlert('La duración debe ser un número válido mayor a 0', 'warning');
                return;
            }
            
            // Validar que los participantes sean válidos
            const participantes = parseInt(document.getElementById('calcParticipants').value);
            if (participantes <= 0 || isNaN(participantes)) {
                this.showAlert('El número de participantes debe ser un número válido mayor a 0', 'warning');
                return;
            }
            
            // Validar compatibilidad entre tipo de habitación y número de participantes
            const servicio = this.currentData.services.find(s => s.id == servicioId);
            const recurso = this.currentData.resources.find(r => r.id == recursoId);
            
            if (servicio && recurso) {
                // Verificar si es una habitación individual
                if (servicio.nombre.toLowerCase().includes('individual') || 
                    recurso.nombre.toLowerCase().includes('individual')) {
                    if (participantes > 1) {
                        this.showAlert('❌ No se puede reservar una habitación individual para más de 1 persona', 'warning');
                        return;
                    }
                }
                
                // Verificar si es una habitación doble
                if (servicio.nombre.toLowerCase().includes('doble') || 
                    recurso.nombre.toLowerCase().includes('doble')) {
                    if (participantes > 2) {
                        this.showAlert('❌ No se puede reservar una habitación doble para más de 2 personas', 'warning');
                        return;
                    }
                }
                
                // Verificar si es una habitación individual pero se seleccionó 2 participantes
                if ((servicio.nombre.toLowerCase().includes('individual') || 
                     recurso.nombre.toLowerCase().includes('individual')) && 
                    participantes === 2) {
                    this.showAlert('❌ Una habitación individual solo puede alojar 1 persona', 'warning');
                    return;
                }
            }
            
            // Crear fecha y hora de inicio
            const fechaHoraInicio = new Date(`${fecha}T${hora}`);
            
            // Crear fecha y hora de fin (sumando la duración)
            const fechaHoraFin = new Date(fechaHoraInicio.getTime() + (duracion * 60 * 60 * 1000));
            
            const formData = {
                servicio_id: parseInt(servicioId),
                recurso_id: parseInt(recursoId),
                fecha_hora_inicio: fechaHoraInicio.toISOString(),
                fecha_hora_fin: fechaHoraFin.toISOString(),
                participantes: participantes,
                tipo_cliente: document.getElementById('calcClientType').value
            };
            
            console.log('🔍 Datos que se envían a la API:', formData);
            console.log('🔍 Tipos de datos:', {
                servicio_id: typeof formData.servicio_id,
                recurso_id: typeof formData.recurso_id,
                fecha_hora_inicio: typeof formData.fecha_hora_inicio,
                fecha_hora_fin: typeof formData.fecha_hora_fin,
                participantes: typeof formData.participantes,
                tipo_cliente: typeof formData.tipo_cliente
            });
            
            // Validación final antes del envío
            if (formData.servicio_id <= 0 || formData.recurso_id <= 0) {
                this.showAlert('Error: IDs de servicio o recurso inválidos', 'danger');
                return;
            }
            
            console.log('🚀 Enviando petición a la API con datos:', formData);
            
            const result = await this.apiCall('/precios-dinamicos/calcular', 'POST', formData);
            
            console.log('📥 Respuesta recibida de la API:', result);
            console.log('🔍 Comparando datos:');
            console.log('   - Precio base enviado (calculado):', this.calculateBasePrice(formData));
            console.log('   - Precio base recibido:', result.precio_base);
            console.log('   - Precio final recibido:', result.precio_final);
            console.log('   - Reglas aplicadas:', result.reglas_aplicadas?.length || 0);
            
            // Agregar al historial
            this.addToHistory(formData, result);
            
            this.displayCalculationResult(result);
            
        } catch (error) {
            console.error('❌ Error calculando precio:', error);
            
            // Mostrar mensaje de error más específico
            let errorMessage = 'Error calculando precio';
            if (error.message.includes('422')) {
                errorMessage = 'Error en los datos enviados. Verifica que todos los campos sean válidos.';
                console.error('🔍 Error 422 - Datos enviados:', {
                    servicio_id: document.getElementById('calcService').value,
                    recurso_id: document.getElementById('calcResource').value,
                    fecha: document.getElementById('calcDate').value,
                    hora: document.getElementById('calcTime').value,
                    duracion_horas: this.getDurationInHours(),
                    participantes: document.getElementById('calcParticipants').value,
                    tipo_cliente: document.getElementById('calcClientType').value
                });
            } else if (error.message.includes('500')) {
                errorMessage = 'Error interno del servidor. Intenta más tarde.';
            } else if (error.message.includes('404')) {
                errorMessage = 'Servicio no encontrado. Verifica la conexión.';
            }
            
            this.showAlert(errorMessage, 'danger');
        }
    }

    calculateBasePrice(formData) {
        try {
            const servicio = this.currentData.services.find(s => s.id == formData.servicio_id);
            if (servicio) {
                const duracionHoras = formData.duracion_horas || this.getDurationInHours();
                
                // Para servicios de habitación, el precio base es por noche
                if (servicio.nombre.toLowerCase().includes('habitación') || servicio.nombre.toLowerCase().includes('alquiler')) {
                    const precioPorNoche = servicio.precio_base;
                    const noches = duracionHoras / 24;
                    return precioPorNoche * noches;
                }
                
                // Para otros servicios, el precio base es por hora
                return servicio.precio_base * duracionHoras;
            }
            return 0;
        } catch (error) {
            console.error('❌ Error calculando precio base:', error);
            return 0;
        }
    }

    getDurationInHours() {
        try {
            const durationInput = document.getElementById('calcDuration');
            const duration = parseFloat(durationInput.value);
            const unit = document.getElementById('calcDurationUnit').value;
            
            // Validar que la duración sea un número válido
            if (isNaN(duration) || duration <= 0) {
                console.error('❌ Duración inválida:', durationInput.value);
                return 0;
            }
            
            // Validar que para habitaciones solo se permitan números enteros
            if (unit === 'nights') {
                if (duration % 1 !== 0) {
                    this.showAlert('Las habitaciones solo se pueden alquilar por noches completas', 'warning');
                    // Redondear hacia arriba
                    const roundedDuration = Math.ceil(duration);
                    durationInput.value = roundedDuration;
                    console.log('🔄 Duración redondeada a noches completas:', roundedDuration);
                    return roundedDuration * 24;
                }
            }
            
            let result = 0;
            switch (unit) {
                case 'days':
                    result = duration * 24;
                    break;
                case 'nights':
                    result = duration * 24;
                    break;
                case 'hours':
                default:
                    result = duration;
                    break;
            }
            
            console.log(`🔍 Duración convertida: ${duration} ${unit} = ${result} horas`);
            return result;
            
        } catch (error) {
            console.error('❌ Error en getDurationInHours:', error);
            return 0;
        }
    }

    displayCalculationResult(result) {
        console.log('🔍 displayCalculationResult llamado con:', result);
        
        const container = document.getElementById('calculationResult');
        console.log('🔍 Contenedor encontrado:', container);
        
        if (!result) {
            console.log('❌ No hay resultado para mostrar');
            container.innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                    <p>Error en el cálculo</p>
                </div>
            `;
            return;
        }

        const precioBase = result.precio_base || 0;
        const precioFinal = result.precio_final || 0;
        const reglasAplicadas = result.reglas_aplicadas || [];
        const diferencia = precioFinal - precioBase;
        const porcentajeCambio = precioBase > 0 ? ((diferencia / precioBase) * 100) : 0;

        console.log('🔍 Datos procesados:', {
            precioBase,
            precioFinal,
            reglasAplicadas: reglasAplicadas.length,
            diferencia,
            porcentajeCambio
        });

        // Mostrar notificación si se aplicaron reglas
        if (reglasAplicadas.length > 0) {
            console.log('🔍 Mostrando notificación de reglas aplicadas');
            console.log('🔍 Reglas aplicadas detalladas:', reglasAplicadas);
            
            // Verificar si hay reglas de anticipación
            const reglasAnticipacion = reglasAplicadas.filter(r => r.tipo_regla === 'anticipacion');
            if (reglasAnticipacion.length > 0) {
                console.log('🎉 ¡DESCUENTOS DE ANTICIPACIÓN ENCONTRADOS!', reglasAnticipacion);
            } else {
                console.log('❌ No se encontraron descuentos de anticipación');
            }
            
            this.showNotification(`Se aplicaron ${reglasAplicadas.length} regla${reglasAplicadas.length > 1 ? 's' : ''} de precio`, 'success');
        } else {
            console.log('🔍 No hay reglas aplicadas para mostrar');
        }

        const htmlContent = `
            <div class="text-center mb-4">
                <h3 class="text-primary">${this.formatCurrency(precioFinal)}</h3>
                <p class="text-muted">Precio final</p>
            </div>
            
            <div class="row mb-3">
                <div class="col-6">
                    <div class="text-center">
                        <h6 class="text-muted">Precio Base</h6>
                        <p class="h5">${this.formatCurrency(precioBase)}</p>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center">
                        <h6 class="text-${diferencia >= 0 ? 'success' : 'danger'}">Cambio</h6>
                        <p class="h5 text-${diferencia >= 0 ? 'success' : 'danger'}">
                            ${diferencia >= 0 ? '+' : ''}${this.formatCurrency(diferencia)}
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="mb-3 calculation-rules">
                <h6>Reglas Aplicadas:</h6>
                ${reglasAplicadas.length > 0 ? 
                    reglasAplicadas.map(regla => `
                        <div class="card mb-2">
                            <div class="card-body p-2">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <strong>${regla.nombre}</strong>
                                        <br>
                                        <small class="text-muted">
                                            Tipo: ${regla.tipo_regla || 'N/A'} | 
                                            Modificador: ${regla.tipo_modificador || 'N/A'}
                                        </small>
                                    </div>
                                    <div class="text-end">
                                        <span class="badge bg-${regla.valor_modificador >= 0 ? 'success' : 'danger'} fs-6">
                                            ${regla.tipo_modificador === 'porcentaje' ? 
                                                (regla.valor_modificador >= 0 ? '+' : '') + regla.valor_modificador + '%' : 
                                                regla.tipo_modificador === 'monto_fijo' ? 
                                                (regla.valor_modificador >= 0 ? '+' : '') + this.formatCurrency(regla.valor_modificador) :
                                                this.formatCurrency(regla.valor_modificador)
                                            }
                                        </span>
                                        <br>
                                        <small class="text-muted">
                                            ${regla.descuento > 0 ? `Descuento: ${this.formatCurrency(regla.descuento)}` : ''}
                                            ${regla.recargo > 0 ? `Recargo: ${this.formatCurrency(regla.recargo)}` : ''}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('') : 
                    '<span class="text-muted">Ninguna regla aplicada</span>'
                }
            </div>
            
            <div class="alert alert-info">
                <small>
                    <strong>Duración:</strong> ${this.getDurationInHours()} horas<br>
                    <strong>Participantes:</strong> ${document.getElementById('calcParticipants').value}<br>
                    <strong>Tipo Cliente:</strong> ${document.getElementById('calcClientType').value}
                </small>
            </div>
        `;
        
        console.log('🔍 HTML generado:', htmlContent);
        container.innerHTML = htmlContent;
        console.log('🔍 HTML insertado en el contenedor');
    }

    async createHoraPicoRule() {
        const formData = {
            nombre: document.getElementById('hpName').value,
            hora_inicio: document.getElementById('hpStartTime').value,
            hora_fin: document.getElementById('hpEndTime').value,
            porcentaje_recargo: parseFloat(document.getElementById('hpRecargo').value),
            prioridad: 10,
            dias_lunes: document.getElementById('hpLunes').checked,
            dias_martes: document.getElementById('hpMartes').checked,
            dias_miercoles: document.getElementById('hpMiercoles').checked,
            dias_jueves: document.getElementById('hpJueves').checked,
            dias_viernes: document.getElementById('hpViernes').checked,
            dias_sabado: document.getElementById('hpSabado').checked,
            dias_domingo: document.getElementById('hpDomingo').checked
        };

        try {
            const result = await this.apiCall('/precios-dinamicos/reglas-rapidas/hora-pico', 'POST', formData);
            if (result) {
                this.showAlert('Regla de hora pico creada exitosamente', 'success');
                document.getElementById('horaPicoForm').reset();
                await this.loadDashboard();
            }
        } catch (error) {
            console.error('Error creando regla:', error);
            this.showAlert('Error creando regla de hora pico', 'danger');
        }
    }

    async createAnticipacionRule() {
        const formData = {
            nombre: document.getElementById('antName').value,
            dias_anticipacion_min: parseInt(document.getElementById('antDias').value),
            porcentaje_descuento: parseFloat(document.getElementById('antDescuento').value),
            prioridad: 20
        };

        try {
            const result = await this.apiCall('/precios-dinamicos/reglas-rapidas/descuento-anticipacion', 'POST', formData);
            if (result) {
                this.showAlert('Regla de descuento por anticipación creada exitosamente', 'success');
                document.getElementById('anticipacionForm').reset();
                await this.loadDashboard();
            }
        } catch (error) {
            console.error('Error creando regla:', error);
            this.showAlert('Error creando regla de descuento', 'danger');
        }
    }

    async createFinSemanaRule() {
        const formData = {
            nombre: document.getElementById('fsName').value,
            porcentaje_recargo: parseFloat(document.getElementById('fsRecargo').value),
            prioridad: 15,
            dias_sabado: document.getElementById('fsSabado').checked,
            dias_domingo: document.getElementById('fsDomingo').checked
        };

        try {
            const result = await this.apiCall('/precios-dinamicos/reglas-rapidas/fin-de-semana', 'POST', formData);
            if (result) {
                this.showAlert('Regla de recargo por fin de semana creada exitosamente', 'success');
                document.getElementById('finSemanaForm').reset();
                await this.loadDashboard();
            }
        } catch (error) {
            console.error('Error creando regla:', error);
            this.showAlert('Error creando regla de fin de semana', 'danger');
        }
    }

    // Formato de moneda en euros con formato español
    formatCurrency(amount) {
        if (amount === null || amount === undefined || isNaN(amount)) {
            return '€0,00';
        }
        
        // Convertir a número y redondear a 2 decimales
        const num = Math.round(parseFloat(amount) * 100) / 100;
        
        // Formato español: 1234.56 -> 1.234,56
        const formatted = num.toLocaleString('es-ES', {
            style: 'currency',
            currency: 'EUR',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        
        return formatted;
    }

    // Formato numérico español para números grandes
    formatNumber(number) {
        if (number === null || number === undefined || isNaN(number)) {
            return '0';
        }
        
        return number.toLocaleString('es-ES');
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error en API call a ${endpoint}:`, error);
            throw error;
        }
    }

    showAlert(message, type = 'info') {
        try {
            // Crear el elemento de alerta
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            alertDiv.style.cssText = `
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            `;
            
            alertDiv.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="flex-grow-1">
                        ${message}
                    </div>
                    <button type="button" class="btn-close ms-2" onclick="this.parentElement.parentElement.remove()"></button>
                </div>
            `;
            
            // Insertar al inicio del body (más seguro)
            document.body.appendChild(alertDiv);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
            
        } catch (error) {
            console.error('❌ Error mostrando alerta:', error);
            // Fallback: usar console.log y alert nativo
            console.log(`[${type.toUpperCase()}] ${message}`);
            try {
                alert(`${type.toUpperCase()}: ${message}`);
            } catch (alertError) {
                console.log(`[${type.toUpperCase()}] ${message}`);
            }
        }
    }

    // Sistema de notificaciones en tiempo real
    showNotification(message, type = 'info', duration = 4000) {
        try {
            // Crear el elemento de notificación
            const notificationDiv = document.createElement('div');
            notificationDiv.className = `notification notification-${type} notification-slide-in`;
            notificationDiv.innerHTML = `
                <div class="notification-content">
                    <i class="fas fa-${this.getNotificationIcon(type)} me-2"></i>
                    <span>${message}</span>
                    <button type="button" class="notification-close" onclick="this.parentElement.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            
            // Insertar en el contenedor de notificaciones
            let notificationContainer = document.getElementById('notificationContainer');
            if (!notificationContainer) {
                notificationContainer = document.createElement('div');
                notificationContainer.id = 'notificationContainer';
                notificationContainer.className = 'notification-container';
                document.body.appendChild(notificationContainer);
            }
            
            notificationContainer.appendChild(notificationDiv);
            
            // Auto-remove después del tiempo especificado
            setTimeout(() => {
                if (notificationDiv.parentNode) {
                    notificationDiv.classList.add('notification-slide-out');
                    setTimeout(() => {
                        if (notificationDiv.parentNode) {
                            notificationDiv.remove();
                        }
                    }, 300);
                }
            }, duration);
            
        } catch (error) {
            console.error('❌ Error mostrando notificación:', error);
            // Fallback
            this.showAlert(message, type);
        }
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'danger': 'times-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Sistema de historial de cálculos
    addToHistory(formData, result) {
        const historyItem = {
            id: Date.now(),
            timestamp: new Date(),
            formData: formData,
            result: result,
            servicio: this.currentData.services.find(s => s.id == formData.servicio_id)?.nombre || 'Desconocido',
            recurso: this.currentData.resources.find(r => r.id == formData.recurso_id)?.nombre || 'Desconocido'
        };
        
        // Agregar al inicio del historial
        this.calculationHistory.unshift(historyItem);
        
        // Mantener solo los últimos elementos
        if (this.calculationHistory.length > this.maxHistoryItems) {
            this.calculationHistory = this.calculationHistory.slice(0, this.maxHistoryItems);
        }
        
        // Guardar en localStorage
        this.saveHistoryToStorage();
        
        // Actualizar la interfaz si está visible
        this.updateHistoryDisplay();
    }

    saveHistoryToStorage() {
        try {
            const historyData = this.calculationHistory.map(item => ({
                ...item,
                timestamp: item.timestamp.toISOString()
            }));
            localStorage.setItem('calculationHistory', JSON.stringify(historyData));
        } catch (error) {
            console.error('❌ Error guardando historial:', error);
        }
    }

    loadHistoryFromStorage() {
        try {
            const savedHistory = localStorage.getItem('calculationHistory');
            if (savedHistory) {
                const historyData = JSON.parse(savedHistory);
                this.calculationHistory = historyData.map(item => ({
                    ...item,
                    timestamp: new Date(item.timestamp)
                }));
            }
        } catch (error) {
            console.error('❌ Error cargando historial:', error);
        }
    }

    updateHistoryDisplay() {
        const historyContainer = document.getElementById('historyContainer');
        if (!historyContainer) return;
        
        if (this.calculationHistory.length === 0) {
            historyContainer.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-history fa-2x mb-3"></i>
                    <p>No hay cálculos en el historial</p>
                </div>
            `;
            return;
        }
        
        historyContainer.innerHTML = this.calculationHistory.map(item => `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${item.servicio} - ${item.recurso}</h6>
                        <small class="text-muted">
                            ${item.timestamp.toLocaleString('es-ES')} | 
                            ${item.formData.participantes} participante${item.formData.participantes > 1 ? 's' : ''} | 
                            ${item.formData.tipo_cliente}
                        </small>
                        <div class="mt-2">
                            <span class="badge bg-primary me-2">
                                Base: ${this.formatCurrency(item.result.precio_base)}
                            </span>
                            <span class="badge bg-success">
                                Final: ${this.formatCurrency(item.result.precio_final)}
                            </span>
                        </div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary" onclick="app.repeatCalculation(${item.id})">
                        <i class="fas fa-redo"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    repeatCalculation(historyId) {
        const historyItem = this.calculationHistory.find(item => item.id === historyId);
        if (!historyItem) return;
        
        // Rellenar el formulario con los datos del historial
        document.getElementById('calcService').value = historyItem.formData.servicio_id;
        document.getElementById('calcResource').value = historyItem.formData.recurso_id;
        document.getElementById('calcDate').value = historyItem.formData.fecha_hora_inicio.split('T')[0];
        document.getElementById('calcTime').value = historyItem.formData.fecha_hora_inicio.split('T')[1];
        document.getElementById('calcParticipants').value = historyItem.formData.participantes;
        document.getElementById('calcClientType').value = historyItem.formData.tipo_cliente;
        
        // Actualizar la duración
        this.updateDurationUnit(historyItem.formData.servicio_id);
        
        // Calcular automáticamente
        this.calculatePrice();
        
        // Cambiar a la pestaña de calculadora
        const calculatorTab = document.getElementById('calculator-tab');
        if (calculatorTab) {
            calculatorTab.click();
        }
        
        this.showNotification('Formulario rellenado con datos del historial', 'info');
    }

    // Limpiar historial
    clearHistory() {
        if (this.calculationHistory.length === 0) {
            this.showNotification('El historial ya está vacío', 'info');
            return;
        }
        
        if (confirm('¿Estás seguro de que quieres limpiar todo el historial de cálculos?')) {
            this.calculationHistory = [];
            this.saveHistoryToStorage();
            this.updateHistoryDisplay();
            this.showNotification('Historial limpiado correctamente', 'success');
        }
    }

    // Exportar historial a CSV
    exportHistoryToCSV() {
        if (this.calculationHistory.length === 0) {
            this.showNotification('No hay datos para exportar', 'warning');
            return;
        }
        
        try {
            // Crear contenido CSV
            const csvContent = this.generateHistoryCSV();
            
            // Crear y descargar archivo
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `historial_calculos_${new Date().toISOString().split('T')[0]}.csv`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showNotification('Historial exportado a CSV correctamente', 'success');
            
        } catch (error) {
            console.error('❌ Error exportando historial:', error);
            this.showNotification('Error al exportar el historial', 'danger');
        }
    }

    generateHistoryCSV() {
        const headers = [
            'Fecha',
            'Servicio',
            'Recurso',
            'Participantes',
            'Tipo Cliente',
            'Precio Base',
            'Precio Final',
            'Diferencia',
            'Reglas Aplicadas'
        ];
        
        const rows = this.calculationHistory.map(item => [
            item.timestamp.toLocaleString('es-ES'),
            item.servicio,
            item.recurso,
            item.formData.participantes,
            item.formData.tipo_cliente,
            item.result.precio_base,
            item.result.precio_final,
            item.result.precio_final - item.result.precio_base,
            item.result.reglas_aplicadas.map(r => r.nombre).join('; ')
        ]);
        
        return [headers, ...rows]
            .map(row => row.map(cell => `"${cell}"`).join(','))
            .join('\n');
    }

    // Exportar estadísticas del dashboard
    exportDashboardStats() {
        try {
            const stats = {
                totalReglas: document.getElementById('totalRules')?.textContent || 0,
                reglasActivas: document.getElementById('activeRules')?.textContent || 0,
                totalServicios: this.currentData.services.length,
                totalRecursos: this.currentData.resources.length,
                fechaExportacion: new Date().toLocaleString('es-ES')
            };
            
            const jsonContent = JSON.stringify(stats, null, 2);
            const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `estadisticas_dashboard_${new Date().toISOString().split('T')[0]}.json`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showNotification('Estadísticas exportadas correctamente', 'success');
            
        } catch (error) {
            console.error('❌ Error exportando estadísticas:', error);
            this.showNotification('Error al exportar las estadísticas', 'danger');
        }
    }

    // Sistema de notificaciones automáticas
    startNotificationSystem() {
        // Configurar recordatorios automáticos
        this.setupAutomaticReminders();
        
        // Configurar notificaciones de sistema
        this.setupSystemNotifications();
        
        // Configurar confirmaciones automáticas
        this.setupAutomaticConfirmations();
        
        console.log('🔔 Sistema de notificaciones automáticas iniciado');
    }

    setupAutomaticReminders() {
        // Recordatorio cada 30 minutos para verificar el sistema
        setInterval(() => {
            this.checkSystemHealth();
        }, 30 * 60 * 1000); // 30 minutos
        
        // Recordatorio diario para revisar reglas
        this.scheduleDailyReminder();
        
        // Recordatorio semanal para exportar datos
        this.scheduleWeeklyReminder();
    }

    async checkSystemHealth() {
        try {
            const response = await this.apiCall('/health');
            if (response.status !== 'healthy') {
                this.showNotification('⚠️ El sistema tiene problemas de salud', 'warning');
            }
        } catch (error) {
            this.showNotification('❌ No se puede conectar al sistema', 'danger');
        }
    }

    scheduleDailyReminder() {
        const now = new Date();
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(9, 0, 0, 0); // 9:00 AM
        
        const timeUntilReminder = tomorrow.getTime() - now.getTime();
        
        setTimeout(() => {
            this.showNotification('📋 Recordatorio diario: Revisa las reglas de precios activas', 'info');
            this.scheduleDailyReminder(); // Programar para mañana
        }, timeUntilReminder);
    }

    scheduleWeeklyReminder() {
        const now = new Date();
        const nextMonday = new Date(now);
        const daysUntilMonday = (8 - now.getDay()) % 7;
        nextMonday.setDate(now.getDate() + daysUntilMonday);
        nextMonday.setHours(10, 0, 0, 0); // 10:00 AM
        
        const timeUntilReminder = nextMonday.getTime() - now.getTime();
        
        setTimeout(() => {
            this.showNotification('📊 Recordatorio semanal: Exporta los datos del sistema', 'info');
            this.scheduleWeeklyReminder(); // Programar para la próxima semana
        }, timeUntilReminder);
    }

    setupSystemNotifications() {
        // Notificar cuando se cargan datos
        this.notifyDataLoaded();
        
        // Notificar cambios en el sistema
        this.setupChangeNotifications();
    }

    notifyDataLoaded() {
        if (this.currentData.services.length > 0 && this.currentData.resources.length > 0) {
            this.showNotification(
                `✅ Sistema cargado: ${this.currentData.services.length} servicios, ${this.currentData.resources.length} recursos`,
                'success'
            );
        }
    }

    setupChangeNotifications() {
        // Observar cambios en el historial
        this.observeHistoryChanges();
        
        // Observar cambios en las reglas
        this.observeRulesChanges();
    }

    observeHistoryChanges() {
        const originalAddToHistory = this.addToHistory.bind(this);
        this.addToHistory = (formData, result) => {
            originalAddToHistory(formData, result);
            
            // Notificar sobre el nuevo cálculo
            const serviceName = this.currentData.services.find(s => s.id == formData.servicio_id)?.nombre || 'Servicio';
            const resourceName = this.currentData.resources.find(r => r.id == formData.recurso_id)?.nombre || 'Recurso';
            
            this.showNotification(
                `💾 Cálculo guardado: ${serviceName} - ${resourceName}`,
                'success',
                3000
            );
            
            // Recordatorio para exportar si hay muchos cálculos
            if (this.calculationHistory.length >= 5) {
                this.showNotification(
                    '📤 Tienes varios cálculos. Considera exportar el historial',
                    'info',
                4000
                );
            }
        };
    }

    observeRulesChanges() {
        // Notificar cuando se crean nuevas reglas
        const originalCreateHoraPicoRule = this.createHoraPicoRule.bind(this);
        this.createHoraPicoRule = async function() {
            const result = await originalCreateHoraPicoRule();
            if (result) {
                this.showNotification('⚡ Regla de hora pico creada exitosamente', 'success');
                this.scheduleRuleReminder('hora pico');
            }
        }.bind(this);

        const originalCreateAnticipacionRule = this.createAnticipacionRule.bind(this);
        this.createAnticipacionRule = async function() {
            const result = await originalCreateAnticipacionRule();
            if (result) {
                this.showNotification('📅 Regla de anticipación creada exitosamente', 'success');
                this.scheduleRuleReminder('anticipación');
            }
        }.bind(this);

        const originalCreateFinSemanaRule = this.createFinSemanaRule.bind(this);
        this.createFinSemanaRule = async function() {
            const result = await originalCreateFinSemanaRule();
            if (result) {
                this.showNotification('🏖️ Regla de fin de semana creada exitosamente', 'success');
                this.scheduleRuleReminder('fin de semana');
            }
        }.bind(this);
    }

    scheduleRuleReminder(ruleType) {
        // Recordatorio para revisar la regla en 24 horas
        setTimeout(() => {
            this.showNotification(
                `🔍 Recordatorio: Revisa la regla de ${ruleType} que creaste ayer`,
                'info',
                6000
            );
        }, 24 * 60 * 60 * 1000); // 24 horas
    }

    setupAutomaticConfirmations() {
        // Confirmar acciones importantes
        this.setupActionConfirmations();
        
        // Confirmar exportaciones
        this.setupExportConfirmations();
    }

    setupActionConfirmations() {
        // Confirmar limpieza del historial
        const originalClearHistory = this.clearHistory.bind(this);
        this.clearHistory = function() {
            if (this.calculationHistory.length === 0) {
                this.showNotification('El historial ya está vacío', 'info');
                return;
            }
            
            if (confirm('¿Estás seguro de que quieres limpiar todo el historial de cálculos?\n\nEsta acción no se puede deshacer.')) {
                originalClearHistory();
                this.showNotification('🗑️ Historial limpiado correctamente', 'success');
            } else {
                this.showNotification('❌ Operación cancelada', 'info');
            }
        }.bind(this);
    }

    setupExportConfirmations() {
        // Confirmar exportación del historial
        const originalExportHistoryToCSV = this.exportHistoryToCSV.bind(this);
        this.exportHistoryToCSV = function() {
            if (this.calculationHistory.length === 0) {
                this.showNotification('No hay datos para exportar', 'warning');
                return;
            }
            
            if (confirm(`¿Exportar ${this.calculationHistory.length} cálculos a CSV?\n\nEl archivo se descargará automáticamente.`)) {
                originalExportHistoryToCSV();
            } else {
                this.showNotification('❌ Exportación cancelada', 'info');
            }
        }.bind(this);

        // Confirmar exportación de estadísticas
        const originalExportDashboardStats = this.exportDashboardStats.bind(this);
        this.exportDashboardStats = function() {
            if (confirm('¿Exportar estadísticas del dashboard a JSON?\n\nEl archivo se descargará automáticamente.')) {
                originalExportDashboardStats();
            } else {
                this.showNotification('❌ Exportación cancelada', 'info');
            }
        }.bind(this);
    }

    // Configuración de notificaciones
    loadNotificationSettings() {
        try {
            const savedSettings = localStorage.getItem('notificationSettings');
            if (savedSettings) {
                this.notificationSettings = { ...this.notificationSettings, ...JSON.parse(savedSettings) };
            }
            
            // Actualizar la UI con la configuración cargada
            this.updateNotificationSettingsUI();
            
        } catch (error) {
            console.error('❌ Error cargando configuración de notificaciones:', error);
        }
    }

    saveNotificationSettings() {
        const settings = {
            confirmations: document.getElementById('confirmationsEnabled').checked,
            reminders: document.getElementById('remindersEnabled').checked,
            systemAlerts: document.getElementById('systemAlertsEnabled').checked,
            autoDismiss: parseInt(document.getElementById('autoDismissTime').value),
            sound: document.getElementById('soundEnabled').checked,
            desktopNotifications: document.getElementById('desktopNotificationsEnabled').checked,
            priorityNotifications: document.getElementById('priorityNotificationsEnabled').checked
        };

        this.updateNotificationSettings(settings);
        this.showNotification('⚙️ Configuración de notificaciones guardada', 'success');
    }

    updateNotificationSettings(newSettings) {
        this.notificationSettings = { ...this.notificationSettings, ...newSettings };
        this.saveNotificationSettings();
        
        this.showNotification('⚙️ Configuración de notificaciones actualizada', 'success');
    }

    // Notificaciones inteligentes
    showSmartNotification(message, type = 'info', options = {}) {
        if (!this.notificationSettings.systemAlerts && type === 'info') {
            return; // No mostrar notificaciones informativas si están deshabilitadas
        }
        
        const duration = options.duration || this.notificationSettings.autoDismiss;
        this.showNotification(message, type, duration);
        
        // Guardar en el historial de notificaciones si es importante
        if (type === 'warning' || type === 'danger') {
            this.saveNotificationToHistory(message, type);
        }
    }

    saveNotificationToHistory(message, type) {
        try {
            const notifications = JSON.parse(localStorage.getItem('notificationHistory') || '[]');
            notifications.unshift({
                message,
                type,
                timestamp: new Date().toISOString(),
                read: false
            });
            
            // Mantener solo las últimas 50 notificaciones
            if (notifications.length > 50) {
                notifications.splice(50);
            }
            
            localStorage.setItem('notificationHistory', JSON.stringify(notifications));
        } catch (error) {
            console.error('❌ Error guardando notificación en historial:', error);
        }
    }

    // Notificaciones de confirmación mejoradas
    showConfirmationDialog(message, onConfirm, onCancel = null) {
        const confirmed = confirm(message);
        if (confirmed) {
            onConfirm();
        } else if (onCancel) {
            onCancel();
        }
    }

    // Notificaciones de progreso
    showProgressNotification(message, progress = 0) {
        const notificationDiv = document.createElement('div');
        notificationDiv.className = 'notification notification-info notification-slide-in';
        notificationDiv.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-spinner fa-spin me-2"></i>
                <span>${message}</span>
                <div class="progress mt-2" style="height: 4px;">
                    <div class="progress-bar" style="width: ${progress}%"></div>
                </div>
                <button type="button" class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        let notificationContainer = document.getElementById('notificationContainer');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notificationContainer';
            notificationContainer.className = 'notification-container';
            document.body.appendChild(notificationContainer);
        }
        
        notificationContainer.appendChild(notificationDiv);
        
        return {
            updateProgress: (newProgress) => {
                const progressBar = notificationDiv.querySelector('.progress-bar');
                if (progressBar) {
                    progressBar.style.width = `${newProgress}%`;
                }
            },
            complete: (finalMessage) => {
                notificationDiv.querySelector('span').textContent = finalMessage;
                notificationDiv.querySelector('.fas.fa-spinner').className = 'fas fa-check me-2';
                setTimeout(() => {
                    if (notificationDiv.parentNode) {
                        notificationDiv.remove();
                    }
                }, 2000);
            },
            remove: () => {
                if (notificationDiv.parentNode) {
                    notificationDiv.remove();
                }
            }
        };
    }

    // Funciones de la pestaña de notificaciones
    saveNotificationSettings() {
        const settings = {
            confirmations: document.getElementById('confirmationsEnabled').checked,
            reminders: document.getElementById('remindersEnabled').checked,
            systemAlerts: document.getElementById('systemAlertsEnabled').checked,
            autoDismiss: parseInt(document.getElementById('autoDismissTime').value),
            sound: document.getElementById('soundEnabled').checked,
            desktopNotifications: document.getElementById('desktopNotificationsEnabled').checked,
            priorityNotifications: document.getElementById('priorityNotificationsEnabled').checked
        };

        this.updateNotificationSettings(settings);
        this.showNotification('⚙️ Configuración de notificaciones guardada', 'success');
    }

    testReminder() {
        this.showNotification('🔔 Este es un recordatorio de prueba', 'info', 3000);
        this.showNotification('📋 Recordatorio diario: Revisa las reglas de precios activas', 'info', 4000);
    }

    clearAllReminders() {
        if (confirm('¿Estás seguro de que quieres limpiar todos los recordatorios programados?')) {
            // Limpiar recordatorios programados
            this.pendingReminders = [];
            this.showNotification('🗑️ Todos los recordatorios han sido limpiados', 'success');
        }
    }

    markAllAsRead() {
        try {
            const notifications = JSON.parse(localStorage.getItem('notificationHistory') || '[]');
            notifications.forEach(notification => {
                notification.read = true;
            });
            localStorage.setItem('notificationHistory', JSON.stringify(notifications));
            
            this.updateNotificationStats();
            this.showNotification('✅ Todas las notificaciones marcadas como leídas', 'success');
        } catch (error) {
            console.error('❌ Error marcando notificaciones como leídas:', error);
        }
    }

    requestNotificationPermission() {
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.showNotification('✅ Permisos de notificación concedidos', 'success');
                    this.updateNotificationSettings({ desktopNotifications: true });
                } else {
                    this.showNotification('❌ Permisos de notificación denegados', 'warning');
                }
            });
        } else {
            this.showNotification('❌ Tu navegador no soporta notificaciones del escritorio', 'warning');
        }
    }

    resetNotificationSettings() {
        if (confirm('¿Estás seguro de que quieres restablecer toda la configuración de notificaciones?')) {
            this.notificationSettings = {
                confirmations: true,
                reminders: true,
                systemAlerts: true,
                autoDismiss: 5000,
                sound: true,
                desktopNotifications: false,
                priorityNotifications: true
            };
            
            this.saveNotificationSettings();
            this.loadNotificationSettings();
            this.showNotification('🔄 Configuración restablecida a valores predeterminados', 'info');
        }
    }

    exportNotificationSettings() {
        try {
            const settings = {
                notificationSettings: this.notificationSettings,
                exportDate: new Date().toISOString(),
                version: '1.0'
            };
            
            const jsonContent = JSON.stringify(settings, null, 2);
            const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `configuracion_notificaciones_${new Date().toISOString().split('T')[0]}.json`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showNotification('📤 Configuración exportada correctamente', 'success');
            
        } catch (error) {
            console.error('❌ Error exportando configuración:', error);
            this.showNotification('Error al exportar la configuración', 'danger');
        }
    }

    updateNotificationStats() {
        try {
            const notifications = JSON.parse(localStorage.getItem('notificationHistory') || '[]');
            const today = new Date().toDateString();
            
            const total = notifications.length;
            const unread = notifications.filter(n => !n.read).length;
            const todayCount = notifications.filter(n => 
                new Date(n.timestamp).toDateString() === today
            ).length;
            
            document.getElementById('totalNotifications').textContent = total;
            document.getElementById('unreadNotifications').textContent = unread;
            document.getElementById('todayNotifications').textContent = todayCount;
            
        } catch (error) {
            console.error('❌ Error actualizando estadísticas:', error);
        }
    }

    updateNotificationHistoryDisplay() {
        const container = document.getElementById('notificationHistoryContainer');
        if (!container) return;
        
        try {
            const notifications = JSON.parse(localStorage.getItem('notificationHistory') || '[]');
            
            if (notifications.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-bell fa-2x mb-3"></i>
                        <p>No hay notificaciones en el historial</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = notifications.slice(0, 20).map(notification => `
                <div class="list-group-item ${notification.read ? '' : 'fw-bold'}">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center">
                                <i class="fas fa-${this.getNotificationIcon(notification.type)} me-2 text-${this.getNotificationColor(notification.type)}"></i>
                                <span>${notification.message}</span>
                                ${!notification.read ? '<span class="badge bg-primary ms-2">Nueva</span>' : ''}
                            </div>
                            <small class="text-muted d-block mt-1">
                                ${new Date(notification.timestamp).toLocaleString('es-ES')}
                            </small>
                        </div>
                        <button class="btn btn-sm btn-outline-secondary" onclick="app.markNotificationAsRead('${notification.timestamp}')">
                            <i class="fas fa-check"></i>
                        </button>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('❌ Error actualizando historial de notificaciones:', error);
        }
    }

    markNotificationAsRead(timestamp) {
        try {
            const notifications = JSON.parse(localStorage.getItem('notificationHistory') || '[]');
            const notification = notifications.find(n => n.timestamp === timestamp);
            if (notification) {
                notification.read = true;
                localStorage.setItem('notificationHistory', JSON.stringify(notifications));
                this.updateNotificationHistoryDisplay();
                this.updateNotificationStats();
            }
        } catch (error) {
            console.error('❌ Error marcando notificación como leída:', error);
        }
    }

    getNotificationColor(type) {
        const colors = {
            'success': 'success',
            'warning': 'warning',
            'danger': 'danger',
            'info': 'info'
        };
        return colors[type] || 'info';
    }

    // Cargar configuración de notificaciones en la UI
    loadNotificationSettings() {
        try {
            const savedSettings = localStorage.getItem('notificationSettings');
            if (savedSettings) {
                this.notificationSettings = { ...this.notificationSettings, ...JSON.parse(savedSettings) };
            }
            
            // Actualizar la UI con la configuración cargada
            this.updateNotificationSettingsUI();
            
        } catch (error) {
            console.error('❌ Error cargando configuración de notificaciones:', error);
        }
    }

    updateNotificationSettingsUI() {
        // Actualizar checkboxes
        if (document.getElementById('confirmationsEnabled')) {
            document.getElementById('confirmationsEnabled').checked = this.notificationSettings.confirmations;
        }
        if (document.getElementById('remindersEnabled')) {
            document.getElementById('remindersEnabled').checked = this.notificationSettings.reminders;
        }
        if (document.getElementById('systemAlertsEnabled')) {
            document.getElementById('systemAlertsEnabled').checked = this.notificationSettings.systemAlerts;
        }
        if (document.getElementById('autoDismissTime')) {
            document.getElementById('autoDismissTime').value = this.notificationSettings.autoDismiss;
        }
        if (document.getElementById('soundEnabled')) {
            document.getElementById('soundEnabled').checked = this.notificationSettings.sound || false;
        }
        if (document.getElementById('desktopNotificationsEnabled')) {
            document.getElementById('desktopNotificationsEnabled').checked = this.notificationSettings.desktopNotifications || false;
        }
        if (document.getElementById('priorityNotificationsEnabled')) {
            document.getElementById('priorityNotificationsEnabled').checked = this.notificationSettings.priorityNotifications || false;
        }
    }

    // ===== CRUD DE REGLAS =====
    
    async refreshRulesList() {
        try {
            console.log('🔄 Actualizando lista de reglas...');
            const rules = await this.apiCall('/precios-dinamicos/reglas');
            this.displayRulesList(rules);
            this.showAlert('Lista de reglas actualizada', 'success');
        } catch (error) {
            console.error('❌ Error actualizando lista de reglas:', error);
            this.showAlert('Error al actualizar reglas', 'danger');
        }
    }

    displayRulesList(rules) {
        const container = document.getElementById('rulesListContainer');
        
        if (!rules || rules.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-info-circle fa-2x mb-3"></i>
                    <p>No hay reglas de precio creadas aún</p>
                    <p class="small">Usa los formularios de abajo para crear tu primera regla</p>
                </div>
            `;
            return;
        }

        const rulesHtml = rules.map(rule => `
            <div class="card mb-3 rule-card" data-rule-id="${rule.id}">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <div class="d-flex align-items-center mb-2">
                                <h6 class="mb-0 me-3">${rule.nombre}</h6>
                                <span class="badge bg-${rule.activa ? 'success' : 'secondary'}">
                                    ${rule.activa ? 'Activa' : 'Inactiva'}
                                </span>
                                <span class="badge bg-info ms-2">${rule.tipo_regla}</span>
                                <span class="badge bg-warning ms-2">${rule.tipo_modificador}</span>
                            </div>
                            <div class="row">
                                <div class="col-md-4">
                                    <small class="text-muted">Modificador:</small><br>
                                    <strong>${rule.valor_modificador}${rule.tipo_modificador === 'porcentaje' ? '%' : '€'}</strong>
                                </div>
                                <div class="col-md-4">
                                    <small class="text-muted">Prioridad:</small><br>
                                    <strong>${rule.prioridad}</strong>
                                </div>
                                <div class="col-md-4">
                                    <small class="text-muted">Creada:</small><br>
                                    <strong>${new Date(rule.created_at).toLocaleDateString('es-ES')}</strong>
                                </div>
                            </div>
                            ${rule.condicion ? `
                                <div class="mt-2">
                                    <small class="text-muted">Condición:</small><br>
                                    <code class="small">${JSON.stringify(rule.condicion)}</code>
                                </div>
                            ` : ''}
                        </div>
                        <div class="col-md-4 text-end">
                            <div class="btn-group-vertical btn-group-sm">
                                <button class="btn btn-outline-primary btn-sm mb-1" onclick="app.editRule(${rule.id})">
                                    <i class="fas fa-edit me-1"></i>Editar
                                </button>
                                <button class="btn btn-outline-${rule.activa ? 'warning' : 'success'} btn-sm mb-1" 
                                        onclick="app.toggleRuleStatus(${rule.id}, ${rule.activa})">
                                    <i class="fas fa-${rule.activa ? 'pause' : 'play'} me-1"></i>
                                    ${rule.activa ? 'Desactivar' : 'Activar'}
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="app.deleteRule(${rule.id}, '${rule.nombre}')">
                                    <i class="fas fa-trash me-1"></i>Eliminar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = rulesHtml;
    }

    async editRule(ruleId) {
        try {
            console.log('🔍 Editando regla ID:', ruleId);
            const rule = await this.apiCall(`/precios-dinamicos/reglas/${ruleId}`);
            
            // Llenar el modal con los datos de la regla
            document.getElementById('editRuleId').value = rule.id;
            document.getElementById('editRuleName').value = rule.nombre;
            document.getElementById('editRuleType').value = rule.tipo_regla;
            document.getElementById('editRuleModifierType').value = rule.tipo_modificador;
            document.getElementById('editRuleModifierValue').value = rule.valor_modificador;
            document.getElementById('editRulePriority').value = rule.prioridad;
            document.getElementById('editRuleActive').checked = rule.activa;
            document.getElementById('editRuleCondition').value = rule.condicion ? JSON.stringify(rule.condicion, null, 2) : '';
            
            // Mostrar el modal usando la función optimizada
            const modal = this.abrirModal('editRuleModal');
            
        } catch (error) {
            console.error('❌ Error cargando regla para editar:', error);
            this.showAlert('Error al cargar la regla', 'danger');
        }
    }

    async saveEditedRule() {
        try {
            const ruleId = document.getElementById('editRuleId').value;
            const ruleData = {
                nombre: document.getElementById('editRuleName').value,
                tipo_regla: document.getElementById('editRuleType').value,
                tipo_modificador: document.getElementById('editRuleModifierType').value,
                valor_modificador: parseFloat(document.getElementById('editRuleModifierValue').value),
                prioridad: parseInt(document.getElementById('editRulePriority').value),
                activa: document.getElementById('editRuleActive').checked,
                condicion: document.getElementById('editRuleCondition').value ? 
                    JSON.parse(document.getElementById('editRuleCondition').value) : null
            };

            console.log('💾 Guardando regla editada:', ruleData);
            
            const updatedRule = await this.apiCall(`/precios-dinamicos/reglas/${ruleId}`, 'PUT', ruleData);
            
            if (updatedRule) {
                this.showAlert(`Regla "${updatedRule.nombre}" actualizada exitosamente`, 'success');
                
                // Cerrar el modal inmediatamente
                const modal = bootstrap.Modal.getInstance(document.getElementById('editRuleModal'));
                if (modal) {
                    modal.hide();
                    // Forzar la eliminación del backdrop si existe
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    // Restaurar el scroll del body
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }
                
                // Actualizar la lista de reglas
                await this.refreshRulesList();
                
                // Actualizar el dashboard
                await this.loadDashboard();
            }
            
        } catch (error) {
            console.error('❌ Error guardando regla editada:', error);
            this.showAlert('Error al guardar la regla', 'danger');
        }
    }

    async toggleRuleStatus(ruleId, currentStatus) {
        try {
            const newStatus = !currentStatus;
            const action = newStatus ? 'activar' : 'desactivar';
            
            console.log(`🔄 ${action} regla ID:`, ruleId);
            
            // Obtener la regla actual
            const currentRule = await this.apiCall(`/precios-dinamicos/reglas/${ruleId}`);
            
            // Actualizar solo el estado
            const updatedRule = await this.apiCall(`/precios-dinamicos/reglas/${ruleId}`, 'PUT', {
                ...currentRule,
                activa: newStatus
            });
            
            if (updatedRule) {
                this.showAlert(`Regla ${action} exitosamente`, 'success');
                
                // Actualizar la lista de reglas
                await this.refreshRulesList();
                
                // Actualizar el dashboard
                await this.loadDashboard();
            }
            
        } catch (error) {
            console.error('❌ Error cambiando estado de la regla:', error);
            this.showAlert('Error al cambiar el estado de la regla', 'danger');
        }
    }

    async deleteRule(ruleId, ruleName) {
        try {
            const confirmed = await this.showConfirmationDialog(
                `¿Estás seguro de que quieres eliminar la regla "${ruleName}"?`,
                'Esta acción no se puede deshacer.'
            );
            
            if (!confirmed) return;
            
            console.log('🗑️ Eliminando regla ID:', ruleId);
            
            const result = await this.apiCall(`/precios-dinamicos/reglas/${ruleId}`, 'DELETE');
            
            if (result) {
                this.showAlert(`Regla "${ruleName}" eliminada exitosamente`, 'success');
                
                // Cerrar cualquier modal que pueda estar abierto
                this.cerrarTodosLosModales();
                
                // Actualizar la lista de reglas
                await this.refreshRulesList();
                
                // Actualizar el dashboard
                await this.loadDashboard();
            }
            
        } catch (error) {
            console.error('❌ Error eliminando regla:', error);
            this.showAlert('Error al eliminar la regla', 'danger');
        }
    }

    // ===== CRUD DE SERVICIOS =====
    
    async refreshServicesList() {
        try {
            console.log('🔄 Actualizando lista de servicios...');
            const services = await this.apiCall('/servicios/');
            console.log('📋 Servicios recibidos de la API:', services);
            this.displayServicesList(services);
            console.log('✅ Lista de servicios actualizada en el DOM');
            this.showAlert('Lista de servicios actualizada', 'success');
        } catch (error) {
            console.error('❌ Error actualizando lista de servicios:', error);
            this.showAlert('Error al actualizar servicios', 'danger');
        }
    }

    displayServicesList(services) {
        console.log('🎯 displayServicesList ejecutándose con', services.length, 'servicios');
        const container = document.getElementById("servicesContainer");
        if (!container) {
            console.error('❌ No se encontró el contenedor servicesContainer');
            return;
        }
        container.innerHTML = "";
        
        if (services.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-info-circle fa-3x mb-3"></i>
                    <h5>No hay servicios disponibles</h5>
                    <p>Crea tu primer servicio usando el formulario de la derecha.</p>
                </div>`;
            return;
        }
        
        services.forEach(s => {
            container.innerHTML += `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h5 class="card-title mb-2">${s.nombre}</h5>
                                <p class="card-text text-muted mb-2">${s.descripcion || "Sin descripción"}</p>
                                <div class="row">
                                    <div class="col-md-6">
                                        <small class="text-muted">
                                            <i class="fas fa-clock me-1"></i>Duración: ${s.duracion_minutos} min
                                        </small>
                                    </div>
                                    <div class="col-md-6">
                                        <small class="text-muted">
                                            <i class="fas fa-euro-sign me-1"></i>Precio: €${s.precio_base}
                                        </small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 text-end">
                                <button class="btn btn-outline-primary btn-sm me-2" onclick="app.editService(${s.id})">
                                    <i class="fas fa-edit me-1"></i>Editar
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="app.deleteService(${s.id}, '${s.nombre}')">
                                    <i class="fas fa-trash me-1"></i>Eliminar
                                </button>
                                <button class="btn btn-outline-info btn-sm ms-2" onclick="app.testModal()">
                                    <i class="fas fa-bug me-1"></i>Test
                                </button>
                            </div>
                        </div>
                    </div>
                </div>`;
        });
        console.log('✅ Servicios renderizados en servicesContainer');
    }

    async createNewService() {
        try {
            // Validar campos requeridos
            const nombre = document.getElementById('newServiceName').value.trim();
            const duracion = parseInt(document.getElementById('newServiceDuration').value);
            const precio = parseFloat(document.getElementById('newServiceBasePrice').value);
            
            if (!nombre) {
                this.showAlert('El nombre del servicio es obligatorio', 'warning');
                return;
            }
            
            if (!duracion || duracion <= 0) {
                this.showAlert('La duración debe ser mayor a 0 minutos', 'warning');
                return;
            }
            
            if (!precio || precio <= 0) {
                this.showAlert('El precio debe ser mayor a 0', 'warning');
                return;
            }
            
            // Deshabilitar el botón y mostrar indicador de carga
            const submitBtn = document.querySelector('#newServiceForm button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creando...';
            
            const formData = {
                nombre: nombre,
                descripcion: document.getElementById('newServiceDescription').value.trim(),
                duracion_minutos: duracion,
                precio_base: precio
            };

            console.log('💾 Creando nuevo servicio:', formData);
            
            const newService = await this.apiCall('/servicios/', 'POST', formData);
            
            if (newService) {
                this.showAlert(`Servicio "${newService.nombre}" creado exitosamente con precio base €${newService.precio_base}`, 'success');
                document.getElementById('newServiceForm').reset();
                
                // Cerrar cualquier modal que pueda estar abierto
                this.cerrarTodosLosModales();
                
                // Actualizar la lista de servicios y marcar como no cargada
                await this.refreshServicesList();
                this.tabsLoaded.services = false;
                
                // Actualizar los selectores de la calculadora
                await this.loadInitialData();
                this.populateSelectors();
                
                // Actualizar el dashboard
                await this.loadDashboard();
            }
        } catch (error) {
            console.error('❌ Error creando servicio:', error);
            this.showAlert('Error al crear el servicio', 'danger');
        } finally {
            // Restaurar el botón
            const submitBtn = document.querySelector('#newServiceForm button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-plus me-2"></i>Crear Servicio';
        }
    }

    async editService(serviceId) {
        try {
            console.log('🔍 Editando servicio ID:', serviceId);
            const service = await this.apiCall(`/servicios/${serviceId}`);
            
            // Llenar el modal con los datos del servicio
            document.getElementById('editServiceId').value = service.id;
            document.getElementById('editServiceName').value = service.nombre;
            document.getElementById('editServiceDescription').value = service.descripcion || '';
            document.getElementById('editServiceDuration').value = service.duracion_minutos;
            document.getElementById('editServiceBasePrice').value = service.precio_base;
            
            // Mostrar el modal usando la función optimizada
            const modal = this.abrirModal('editServiceModal');
            
        } catch (error) {
            console.error('❌ Error cargando servicio para editar:', error);
            this.showAlert('Error al cargar el servicio', 'danger');
        }
    }

    async saveEditedService() {
        try {
            // Validar campos requeridos
            const nombre = document.getElementById('editServiceName').value.trim();
            const duracion = parseInt(document.getElementById('editServiceDuration').value);
            const precio = parseFloat(document.getElementById('editServiceBasePrice').value);
            
            if (!nombre) {
                this.showAlert('El nombre del servicio es obligatorio', 'warning');
                return;
            }
            
            if (!duracion || duracion <= 0) {
                this.showAlert('La duración debe ser mayor a 0 minutos', 'warning');
                return;
            }
            
            if (!precio || precio <= 0) {
                this.showAlert('El precio debe ser mayor a 0', 'warning');
                return;
            }
            
            // Deshabilitar el botón y mostrar indicador de carga
            const submitBtn = document.querySelector('#editServiceModal .btn-primary');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Guardando...';
            
            const serviceId = document.getElementById('editServiceId').value;
            const serviceData = {
                nombre: nombre,
                descripcion: document.getElementById('editServiceDescription').value.trim(),
                duracion_minutos: duracion,
                precio_base: precio
            };

            console.log('💾 Guardando servicio editado:', serviceData);
            
            const updatedService = await this.apiCall(`/servicios/${serviceId}`, 'PUT', serviceData);
            
            if (updatedService) {
                this.showAlert(`Servicio "${updatedService.nombre}" actualizado exitosamente`, 'success');
                
                // Cerrar el modal inmediatamente
                const modal = bootstrap.Modal.getInstance(document.getElementById('editServiceModal'));
                if (modal) {
                    modal.hide();
                    // Forzar la eliminación del backdrop si existe
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    // Restaurar el scroll del body
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }
                
                // Actualizar la lista de servicios y marcar como no cargada
                await this.refreshServicesList();
                this.tabsLoaded.services = false;
                
                // Actualizar los selectores de la calculadora
                await this.loadInitialData();
                this.populateSelectors();
                
                // Actualizar el dashboard
                await this.loadDashboard();
            }
            
        } catch (error) {
            console.error('❌ Error guardando servicio editado:', error);
            this.showAlert('Error al guardar el servicio', 'danger');
        } finally {
            // Restaurar el botón
            const submitBtn = document.querySelector('#editServiceModal .btn-primary');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Guardar Cambios';
        }
    }

    async deleteService(serviceId, serviceName) {
        try {
            if (!confirm(`¿Estás seguro de que quieres eliminar el servicio "${serviceName}"?\n\n⚠️ Esta acción no se puede deshacer y eliminará todas las reservas asociadas a este servicio.`)) {
                return;
            }
            
            // Mostrar indicador de carga en el botón de eliminar
            const deleteBtn = document.querySelector(`button[onclick="app.deleteService(${serviceId}, '${serviceName}')"]`);
            if (deleteBtn) {
                const originalText = deleteBtn.innerHTML;
                deleteBtn.disabled = true;
                deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Eliminando...';
                
                // Restaurar el botón después de un tiempo
                setTimeout(() => {
                    deleteBtn.disabled = false;
                    deleteBtn.innerHTML = originalText;
                }, 5000); // 5 segundos como máximo
            }
            
            console.log('🗑️ Eliminando servicio ID:', serviceId);
            
            const result = await this.apiCall(`/servicios/${serviceId}`, 'DELETE');
            
            if (result) {
                this.showAlert(`Servicio "${serviceName}" eliminado exitosamente`, 'success');
                
                // Cerrar cualquier modal que pueda estar abierto
                this.cerrarTodosLosModales();
                
                // Actualizar la lista de servicios y marcar como no cargada
                await this.refreshServicesList();
                this.tabsLoaded.services = false;
                
                // Actualizar los selectores de la calculadora
                await this.loadInitialData();
                this.populateSelectors();
                
                // Actualizar el dashboard
                await this.loadDashboard();
            }
            
        } catch (error) {
            console.error('❌ Error eliminando servicio:', error);
            this.showAlert('Error al eliminar el servicio', 'danger');
        }
    }

    // ===== CRUD DE RECURSOS =====
    
    async refreshResourcesList() {
        try {
            console.log('🔄 Actualizando lista de recursos...');
            const resources = await this.apiCall('/recursos/');
            console.log('🏢 Recursos recibidos de la API:', resources);
            this.displayResourcesList(resources);
            console.log('✅ Lista de recursos actualizada en el DOM');
            this.showAlert('Lista de recursos actualizada', 'success');
        } catch (error) {
            console.error('❌ Error actualizando lista de recursos:', error);
            this.showAlert('Error al actualizar recursos', 'danger');
        }
    }

    displayResourcesList(resources) {
        console.log('🎯 displayResourcesList ejecutándose con', resources.length, 'recursos');
        const container = document.getElementById("resourcesContainer");
        if (!container) {
            console.error('❌ No se encontró el contenedor resourcesContainer');
            return;
        }
        
        if (resources.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-building fa-3x mb-3"></i>
                    <p>No hay recursos disponibles</p>
                    <p class="small">Haz clic en "Crear Nuevo Recurso" para agregar el primero</p>
                </div>`;
            return;
        }
        
        container.innerHTML = "";
        resources.forEach(r => {
            const statusClass = r.disponible ? 'success' : 'danger';
            const statusText = r.disponible ? 'Disponible' : 'No Disponible';
            
            container.innerHTML += `
                <div class="card mb-3 resource-card" style="cursor: pointer;" onclick="app.mostrarDetalleRecurso(${r.id})">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h5 class="card-title mb-1">
                                    <i class="fas fa-building me-2"></i>${r.nombre}
                                </h5>
                                <p class="card-text text-muted mb-1">
                                    <i class="fas fa-tag me-1"></i><strong>Tipo:</strong> ${r.tipo || 'No especificado'}
                                </p>
                                <p class="card-text text-muted mb-1">
                                    <i class="fas fa-users me-1"></i><strong>Capacidad:</strong> ${r.capacidad || 1} persona(s)
                                </p>
                                <p class="card-text text-muted mb-1">
                                    <i class="fas fa-euro-sign me-1"></i><strong>Precio:</strong> €${r.precio_base ? r.precio_base.toFixed(2) : '0.00'}/hora
                                </p>
                                ${r.descripcion ? `<p class="card-text text-muted mb-1"><i class="fas fa-info-circle me-1"></i>${r.descripcion}</p>` : ''}
                                <span class="badge bg-${statusClass}">
                                    <i class="fas fa-${r.disponible ? 'check' : 'times'} me-1"></i>${statusText}
                                </span>
                            </div>
                            <div class="col-md-4 text-end">
                                <div class="btn-group-vertical w-100">
                                    <button class="btn btn-outline-primary btn-sm mb-1" onclick="event.stopPropagation(); app.editResource(${r.id})">
                                        <i class="fas fa-edit me-1"></i>Editar
                                    </button>
                                    <button class="btn btn-outline-danger btn-sm" onclick="event.stopPropagation(); app.deleteResource(${r.id}, '${r.nombre}')">
                                        <i class="fas fa-trash me-1"></i>Eliminar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;
        });
        console.log('✅ Recursos renderizados en resourcesContainer');
    }

    async createNewResource() {
        try {
            const formData = {
                nombre: document.getElementById('newResourceName').value,
                tipo: document.getElementById('newResourceType').value,
                capacidad: parseInt(document.getElementById('newResourceCapacity').value),
                descripcion: document.getElementById('newResourceDescription').value,
                disponible: document.getElementById('newResourceAvailable').checked,
                precio_base: parseFloat(document.getElementById('newResourcePrice').value) || 0
            };

            console.log('💾 Creando nuevo recurso:', formData);
            
            const newResource = await this.apiCall('/recursos/', 'POST', formData);
            
            if (newResource) {
                this.showAlert(`Recurso "${newResource.nombre}" creado exitosamente`, 'success');
                
                // Cerrar el modal inmediatamente
                const modal = bootstrap.Modal.getInstance(document.getElementById('newResourceModal'));
                if (modal) {
                    modal.hide();
                    // Forzar la eliminación del backdrop si existe
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    // Restaurar el scroll del body
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }
                
                // Limpiar el formulario
                document.getElementById('newResourceForm').reset();
                
                // Actualizar la lista de recursos y marcar como no cargada
                await this.refreshResourcesList();
                this.tabsLoaded.resources = false;
                
                // Actualizar los selectores de la calculadora
                await this.loadInitialData();
                this.populateSelectors();
                
                // Actualizar el dashboard
                await this.loadDashboard();
            }
            
        } catch (error) {
            console.error('❌ Error creando recurso:', error);
            this.showAlert('Error al crear el recurso', 'danger');
        }
    }

    async editResource(resourceId) {
        try {
            console.log('🔍 Editando recurso ID:', resourceId);
            const resource = await this.apiCall(`/recursos/${resourceId}`);
            
            // Llenar el modal con los datos del recurso
            document.getElementById('editResourceId').value = resource.id;
            document.getElementById('editResourceName').value = resource.nombre;
            document.getElementById('editResourceType').value = resource.tipo;
            document.getElementById('editResourceCapacity').value = resource.capacidad || 1;
            document.getElementById('editResourceDescription').value = resource.descripcion || '';
            document.getElementById('editResourceAvailable').checked = resource.disponible;
            document.getElementById('editResourcePrice').value = resource.precio_base || '';
            
            // Mostrar el modal usando la función optimizada
            const modal = this.abrirModal('editResourceModal');
            
        } catch (error) {
            console.error('❌ Error cargando recurso para editar:', error);
            this.showAlert('Error al cargar el recurso', 'danger');
        }
    }

    async saveEditedResource() {
        try {
            const resourceId = document.getElementById('editResourceId').value;
            const resourceData = {
                nombre: document.getElementById('editResourceName').value,
                tipo: document.getElementById('editResourceType').value,
                capacidad: parseInt(document.getElementById('editResourceCapacity').value),
                descripcion: document.getElementById('editResourceDescription').value,
                disponible: document.getElementById('editResourceAvailable').checked,
                precio_base: parseFloat(document.getElementById('editResourcePrice').value) || 0
            };

            console.log('💾 Guardando recurso editado:', resourceData);
            
            const updatedResource = await this.apiCall(`/recursos/${resourceId}`, 'PUT', resourceData);
            
            if (updatedResource) {
                this.showAlert(`Recurso "${updatedResource.nombre}" actualizado exitosamente`, 'success');
                
                // Cerrar el modal inmediatamente
                const modal = bootstrap.Modal.getInstance(document.getElementById('editResourceModal'));
                if (modal) {
                    modal.hide();
                    // Forzar la eliminación del backdrop si existe
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    // Restaurar el scroll del body
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }
                
                // Actualizar la lista de recursos y marcar como no cargada
                await this.refreshResourcesList();
                this.tabsLoaded.resources = false;
                
                // Actualizar los selectores de la calculadora
                await this.loadInitialData();
                this.populateSelectors();
                
                // Actualizar el dashboard
                await this.loadDashboard();
            }
            
        } catch (error) {
            console.error('❌ Error guardando recurso editado:', error);
            this.showAlert('Error al guardar el recurso', 'danger');
        }
    }

    async toggleResourceAvailability(resourceId, currentStatus) {
        try {
            const newStatus = !currentStatus;
            const action = newStatus ? 'activar' : 'desactivar';
            
            console.log(`🔄 ${action} recurso ID:`, resourceId);
            
            const result = await this.apiCall(`/recursos/${resourceId}/toggle-disponibilidad`, 'PUT');
            
            if (result) {
                this.showAlert(`Recurso ${action} exitosamente`, 'success');
                
                // Actualizar la lista de recursos y marcar como no cargada
                await this.refreshResourcesList();
                this.tabsLoaded.resources = false;
                
                // Actualizar los selectores de la calculadora
                await this.loadInitialData();
                this.populateSelectors();
                
                // Actualizar el dashboard
                await this.loadDashboard();
            }
            
        } catch (error) {
            console.error('❌ Error cambiando disponibilidad del recurso:', error);
            this.showAlert('Error al cambiar la disponibilidad del recurso', 'danger');
        }
    }

    async deleteResource(resourceId, resourceName) {
        try {
            if (!confirm(`¿Estás seguro de que quieres eliminar el recurso "${resourceName}"?\n\nEsta acción no se puede deshacer.`)) {
                return;
            }
            
            console.log('🗑️ Eliminando recurso ID:', resourceId);
            
            const result = await this.apiCall(`/recursos/${resourceId}`, 'DELETE');
            
            if (result) {
                this.showAlert(`Recurso "${resourceName}" eliminado exitosamente`, 'success');
                
                // Cerrar cualquier modal que pueda estar abierto
                this.cerrarTodosLosModales();
                
                // Actualizar la lista de recursos y marcar como no cargada
                await this.refreshResourcesList();
                this.tabsLoaded.resources = false;
                
                // Actualizar los selectores de la calculadora
                await this.loadInitialData();
                this.populateSelectors();
                
                // Actualizar el dashboard
                await this.loadDashboard();
            }
            
        } catch (error) {
            console.error('❌ Error eliminando recurso:', error);
            this.showAlert('Error al eliminar el recurso', 'danger');
        }
    }

    // ===== CRUD DE RESERVAS =====
    
    async refreshReservasList() {
        try {
            console.log('🔄 Actualizando lista de reservas...');
            const reservas = await this.apiCall('/reservas/listar');
            console.log('📅 Reservas recibidas de la API:', reservas);
            this.displayReservasList(reservas);
            this.populateReservaSelectors();
            console.log('✅ Lista de reservas actualizada en el DOM');
        } catch (error) {
            console.error('❌ Error actualizando lista de reservas:', error);
            this.showAlert('Error al actualizar reservas', 'danger');
        }
    }

    displayReservasList(reservas) {
        console.log('🎯 displayReservasList ejecutándose con', reservas.length, 'reservas');
        const container = document.getElementById("reservasContainer");
        if (!container) {
            console.error('❌ No se encontró el contenedor reservasContainer');
            return;
        }
        
        if (reservas.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-calendar-times fa-3x mb-3"></i>
                    <p>No hay reservas registradas</p>
                </div>`;
            return;
        }

        container.innerHTML = "";
        reservas.forEach(reserva => {
            const fechaInicio = new Date(reserva.fecha_hora_inicio).toLocaleString('es-ES');
            const fechaFin = new Date(reserva.fecha_hora_fin).toLocaleString('es-ES');
            
            // Obtener nombres de cliente, servicio y recurso
            const cliente = this.currentData.clientes?.find(c => c.id === reserva.cliente_id);
            const servicio = this.currentData.services.find(s => s.id === reserva.servicio_id);
            const recurso = this.currentData.resources.find(r => r.id === reserva.recurso_id);
            
            // Debug: mostrar información del recurso encontrado
            console.log(`🔍 Reserva ${reserva.id} - Recurso ID: ${reserva.recurso_id}, Encontrado:`, recurso);
            
            container.innerHTML += `
                <div class="card mb-3 reserva-card" data-reserva-id="${reserva.id}">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h6 class="card-title mb-1">
                                    <i class="fas fa-calendar-check me-2"></i>
                                    Reserva #${reserva.id}
                                </h6>
                                <p class="card-text mb-1">
                                    <strong>Cliente:</strong> ${cliente ? cliente.nombre : `ID: ${reserva.cliente_id}`} | 
                                    <strong>Servicio:</strong> ${servicio ? servicio.nombre : `ID: ${reserva.servicio_id}`} | 
                                    <strong>Recurso:</strong> ${recurso ? recurso.nombre : `ID: ${reserva.recurso_id}`}
                                </p>
                                <p class="card-text mb-1">
                                    <strong>Inicio:</strong> ${fechaInicio} | 
                                    <strong>Fin:</strong> ${fechaFin}
                                </p>
                                <span class="badge bg-${this.getEstadoBadgeColor(reserva.estado)}">
                                    ${reserva.estado.toUpperCase()}
                                </span>
                            </div>
                            <div class="col-md-4 text-end">
                                <button class="btn btn-sm btn-outline-primary me-2" 
                                        onclick="app.editReserva(${reserva.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" 
                                        onclick="app.deleteReserva(${reserva.id}, 'Reserva #${reserva.id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>`;
        });
        console.log('✅ Reservas renderizadas en reservasContainer');
    }

    getEstadoBadgeColor(estado) {
        const colores = {
            'confirmada': 'success',
            'pendiente': 'warning',
            'cancelada': 'danger',
            'completada': 'info'
        };
        return colores[estado] || 'secondary';
    }

    async populateReservaSelectors() {
        try {
            // Poblar selector de clientes
            const clienteSelect = document.getElementById('newReservaCliente');
            if (clienteSelect) {
                clienteSelect.innerHTML = '<option value="">Seleccionar cliente...</option>';
                const clientes = await this.apiCall('/clientes/');
                if (clientes) {
                    clientes.forEach(cliente => {
                        clienteSelect.innerHTML += `
                            <option value="${cliente.id}">${cliente.nombre} - ${cliente.email}</option>`;
                    });
                }
            }

            // Poblar selector de servicios
            const servicioSelect = document.getElementById('newReservaServicio');
            if (servicioSelect) {
                servicioSelect.innerHTML = '<option value="">Seleccionar servicio...</option>';
                this.currentData.services.forEach(service => {
                    servicioSelect.innerHTML += `
                        <option value="${service.id}" data-duracion="${service.duracion_minutos}">${service.nombre} - €${service.precio_base} (${service.duracion_minutos} min)</option>`;
                });
                
                // Remover event listeners existentes para evitar duplicados
                servicioSelect.removeEventListener('change', this._handleServicioChange);
                
                // Agregar event listener para calcular automáticamente la fecha de fin
                this._handleServicioChange = () => this.calcularFechaFinReserva();
                servicioSelect.addEventListener('change', this._handleServicioChange);
            }

            // Poblar selector de recursos
            const recursoSelect = document.getElementById('newReservaRecurso');
            if (recursoSelect) {
                recursoSelect.innerHTML = '<option value="">Seleccionar recurso...</option>';
                this.currentData.resources.forEach(resource => {
                    if (resource.disponible) {
                        recursoSelect.innerHTML += `
                            <option value="${resource.id}">${resource.nombre} (${resource.tipo})</option>`;
                    }
                });
            }

            // Poblar selector de filtros
            const filterServicioSelect = document.getElementById('filterServicio');
            if (filterServicioSelect) {
                filterServicioSelect.innerHTML = '<option value="">Todos</option>';
                this.currentData.services.forEach(service => {
                    filterServicioSelect.innerHTML += `
                        <option value="${service.id}">${service.nombre}</option>`;
                });
            }
            
            // Agregar event listener para fecha de inicio
            const fechaInicioInput = document.getElementById('newReservaFechaInicio');
            if (fechaInicioInput) {
                // Remover event listeners existentes para evitar duplicados
                fechaInicioInput.removeEventListener('change', this._handleFechaInicioChange);
                
                // Agregar event listener para calcular automáticamente la fecha de fin
                this._handleFechaInicioChange = () => this.calcularFechaFinReserva();
                fechaInicioInput.addEventListener('change', this._handleFechaInicioChange);
            }
        } catch (error) {
            console.error('❌ Error poblando selectores de reservas:', error);
        }
    }

    async createNewReserva() {
        try {
            // Validar campos obligatorios
            const clienteId = document.getElementById('newReservaCliente').value;
            const servicioId = document.getElementById('newReservaServicio').value;
            const recursoId = document.getElementById('newReservaRecurso').value;
            const fechaInicio = document.getElementById('newReservaFechaInicio').value;
            const fechaFin = document.getElementById('newReservaFechaFin').value;
            const estado = document.getElementById('newReservaEstado').value;
            
            if (!clienteId || !servicioId || !recursoId || !fechaInicio || !fechaFin) {
                this.showReservaMessage('Por favor completa todos los campos obligatorios', 'warning');
                return;
            }
            
            // Validar que la fecha de fin sea posterior a la de inicio
            const fechaInicioObj = new Date(fechaInicio);
            const fechaFinObj = new Date(fechaFin);
            
            if (fechaFinObj <= fechaInicioObj) {
                this.showReservaMessage('La fecha de fin debe ser posterior a la fecha de inicio', 'warning');
                return;
            }
            
            // Validar que la duración coincida con el servicio seleccionado
            const servicioSelect = document.getElementById('newReservaServicio');
            const selectedOption = servicioSelect.options[servicioSelect.selectedIndex];
            const duracionEsperada = parseInt(selectedOption.getAttribute('data-duracion'));
            const duracionReal = Math.round((fechaFinObj - fechaInicioObj) / (1000 * 60)); // en minutos
            
            if (Math.abs(duracionReal - duracionEsperada) > 1) { // tolerancia de 1 minuto
                this.showReservaMessage(`La duración de la reserva (${duracionReal} min) no coincide con la duración del servicio (${duracionEsperada} min). Se calculará automáticamente.`, 'warning');
                
                // Recalcular automáticamente la fecha de fin
                this.calcularFechaFinReserva();
                return;
            }
            
            const formData = {
                cliente_id: parseInt(clienteId),
                servicio_id: parseInt(servicioId),
                recurso_id: parseInt(recursoId),
                fecha_hora_inicio: fechaInicio,
                fecha_hora_fin: fechaFin,
                estado: estado
            };

            console.log('💾 Creando nueva reserva:', formData);
            
            const newReserva = await this.apiCall('/reservas/', 'POST', formData);
            
            if (newReserva) {
                this.showReservaMessage('Reserva creada exitosamente', 'success');
                document.getElementById('newReservaForm').reset();
                
                // Limpiar mensajes previos
                this.clearReservaMessage();
                
                // Actualizar la lista de reservas y marcar como no cargada
                await this.refreshReservasList();
                this.tabsLoaded.reservas = false;
            }
            
        } catch (error) {
            console.error('❌ Error creando reserva:', error);
            this.showReservaMessage('Error al crear la reserva', 'danger');
        }
    }

    calcularFechaFinReserva() {
        const servicioSelect = document.getElementById('newReservaServicio');
        const fechaInicioInput = document.getElementById('newReservaFechaInicio');
        const fechaFinInput = document.getElementById('newReservaFechaFin');
        
        if (!servicioSelect.value || !fechaInicioInput.value) {
            console.log('❌ No se puede calcular: servicio o fecha de inicio no seleccionados');
            return;
        }
        
        // Obtener la duración del servicio seleccionado
        const selectedOption = servicioSelect.options[servicioSelect.selectedIndex];
        const duracionMinutos = parseInt(selectedOption.getAttribute('data-duracion'));
        
        console.log('🔍 Datos para cálculo:', {
            fechaInicioValue: fechaInicioInput.value,
            duracionMinutos: duracionMinutos,
            selectedOption: selectedOption.textContent
        });
        
        if (duracionMinutos && fechaInicioInput.value) {
            try {
                // Calcular la fecha de fin
                const fechaInicio = new Date(fechaInicioInput.value);
                console.log('🔍 Fecha de inicio parseada:', {
                    original: fechaInicioInput.value,
                    parsed: fechaInicio,
                    timestamp: fechaInicio.getTime(),
                    isoString: fechaInicio.toISOString()
                });
                
                const fechaFin = new Date(fechaInicio.getTime() + (duracionMinutos * 60 * 1000));
                console.log('🔍 Fecha de fin calculada:', {
                    timestamp: fechaFin.getTime(),
                    isoString: fechaFin.toISOString(),
                    localString: fechaFin.toString()
                });
                
                // Formatear la fecha de fin para el input datetime-local
                // Usar toLocaleString para mantener la hora local
                const year = fechaFin.getFullYear();
                const month = String(fechaFin.getMonth() + 1).padStart(2, '0');
                const day = String(fechaFin.getDate()).padStart(2, '0');
                const hours = String(fechaFin.getHours()).padStart(2, '0');
                const minutes = String(fechaFin.getMinutes()).padStart(2, '0');
                
                const fechaFinFormateada = `${year}-${month}-${day}T${hours}:${minutes}`;
                fechaFinInput.value = fechaFinFormateada;
                
                console.log(`✅ Fecha de fin calculada automáticamente: ${fechaInicioInput.value} + ${duracionMinutos} min = ${fechaFinFormateada}`);
                
                // Mostrar notificación de que se calculó automáticamente
                this.showNotification(`Fecha de fin calculada automáticamente: ${duracionMinutos} minutos después del inicio`, 'info', 3000);
                
            } catch (error) {
                console.error('❌ Error calculando fecha de fin:', error);
                console.error('❌ Detalles del error:', {
                    fechaInicioValue: fechaInicioInput.value,
                    duracionMinutos: duracionMinutos,
                    error: error.message
                });
            }
        } else {
            console.log('❌ No se puede calcular:', {
                duracionMinutos: duracionMinutos,
                fechaInicioValue: fechaInicioInput.value
            });
        }
    }

         async filterReservas() {
         try {
             const filters = {
                 fecha_inicio: document.getElementById('filterFechaInicio').value,
                 fecha_fin: document.getElementById('filterFechaFin').value,
                 estado: document.getElementById('filterEstado').value,
                 servicio_id: document.getElementById('filterServicio').value
             };

             // Filtrar valores vacíos
             Object.keys(filters).forEach(key => {
                 if (!filters[key]) delete filters[key];
             });

             console.log('🔍 Aplicando filtros:', filters);
             
             let url = '/reservas/listar?';
             Object.keys(filters).forEach(key => {
                 url += `${key}=${filters[key]}&`;
             });
             url = url.slice(0, -1); // Remover último &

             const reservas = await this.apiCall(url);
             this.displayReservasList(reservas);
             
         } catch (error) {
             console.error('❌ Error filtrando reservas:', error);
             this.showAlert('Error al filtrar reservas', 'danger');
         }
     }

     // ===== FUNCIONES DE EDICIÓN Y ELIMINACIÓN DE RESERVAS =====
     
     async editReserva(reservaId) {
         try {
             console.log('🔍 Editando reserva ID:', reservaId);
             const reserva = await this.apiCall(`/reservas/${reservaId}`);
             
             // Llenar el modal con los datos de la reserva
             document.getElementById('editReservaId').value = reserva.id;
             document.getElementById('editReservaCliente').value = reserva.cliente_id;
             document.getElementById('editReservaServicio').value = reserva.servicio_id;
             document.getElementById('editReservaRecurso').value = reserva.recurso_id;
             document.getElementById('editReservaFechaInicio').value = reserva.fecha_hora_inicio.slice(0, 16);
             document.getElementById('editReservaFechaFin').value = reserva.fecha_hora_fin.slice(0, 16);
             document.getElementById('editReservaEstado').value = reserva.estado;
             
             // Poblar los selectores si no están poblados
             await this.poblarSelectoresEditReserva();
             
             // Mostrar el modal usando la función optimizada
             const modal = this.abrirModal('editReservaModal');
             
         } catch (error) {
             console.error('❌ Error cargando reserva para editar:', error);
             this.showAlert('Error al cargar la reserva', 'danger');
         }
     }

     async deleteReserva(reservaId, reservaName) {
         try {
             if (!confirm(`¿Estás seguro de que quieres eliminar la reserva "${reservaName}"?\n\nEsta acción no se puede deshacer.`)) {
                 return;
             }
             
             console.log('🗑️ Eliminando reserva ID:', reservaId);
             
             const result = await this.apiCall(`/reservas/${reservaId}`, 'DELETE');
             
             if (result) {
                 this.showAlert(`Reserva "${reservaName}" eliminada exitosamente`, 'success');
                 
                 // Cerrar cualquier modal que pueda estar abierto
                 this.cerrarTodosLosModales();
                 
                 // Actualizar la lista de reservas
                 await this.refreshReservasList();
                 
                 // Actualizar el calendario
                 await this.actualizarCalendario();
                 
                 // Actualizar el dashboard
                 await this.loadDashboard();
             }
             
         } catch (error) {
             console.error('❌ Error eliminando reserva:', error);
             this.showAlert('Error al eliminar la reserva', 'danger');
         }
     }

     /**
      * Pobla los selectores del modal de edición de reserva
      */
     async poblarSelectoresEditReserva() {
         try {
             // Poblar selector de clientes
             const clienteSelect = document.getElementById('editReservaCliente');
             if (clienteSelect && this.currentData.clientes) {
                 clienteSelect.innerHTML = '<option value="">Seleccionar cliente...</option>';
                 this.currentData.clientes.forEach(cliente => {
                     const option = document.createElement('option');
                     option.value = cliente.id;
                     option.textContent = cliente.nombre;
                     clienteSelect.appendChild(option);
                 });
             }
             
             // Poblar selector de servicios
             const servicioSelect = document.getElementById('editReservaServicio');
             if (servicioSelect && this.currentData.services) {
                 servicioSelect.innerHTML = '<option value="">Seleccionar servicio...</option>';
                 this.currentData.services.forEach(servicio => {
                     const option = document.createElement('option');
                     option.value = servicio.id;
                     option.textContent = servicio.nombre;
                     servicioSelect.appendChild(option);
                 });
             }
             
             // Poblar selector de recursos
             const recursoSelect = document.getElementById('editReservaRecurso');
             if (recursoSelect && this.currentData.resources) {
                 recursoSelect.innerHTML = '<option value="">Seleccionar recurso...</option>';
                 this.currentData.resources.forEach(recurso => {
                     const option = document.createElement('option');
                     option.value = recurso.id;
                     option.textContent = recurso.nombre;
                     recursoSelect.appendChild(option);
                 });
             }
             
             console.log('✅ Selectores del modal de edición de reserva poblados');
         } catch (error) {
             console.error('❌ Error poblando selectores de edición de reserva:', error);
         }
     }

     /**
      * Guarda los cambios de una reserva editada
      */
     async saveEditedReserva() {
         try {
             const reservaId = document.getElementById('editReservaId').value;
             const reservaData = {
                 cliente_id: parseInt(document.getElementById('editReservaCliente').value),
                 servicio_id: parseInt(document.getElementById('editReservaServicio').value),
                 recurso_id: parseInt(document.getElementById('editReservaRecurso').value),
                 fecha_hora_inicio: document.getElementById('editReservaFechaInicio').value,
                 fecha_hora_fin: document.getElementById('editReservaFechaFin').value,
                 estado: document.getElementById('editReservaEstado').value
             };
             
             console.log('💾 Guardando reserva editada:', reservaData);
             
             const updatedReserva = await this.apiCall(`/reservas/${reservaId}`, 'PUT', reservaData);
             
             if (updatedReserva) {
                 this.showAlert(`Reserva actualizada exitosamente`, 'success');
                 
                 // Cerrar el modal inmediatamente
                 const modal = bootstrap.Modal.getInstance(document.getElementById('editReservaModal'));
                 if (modal) {
                     modal.hide();
                     // Forzar la eliminación del backdrop si existe
                     const backdrop = document.querySelector('.modal-backdrop');
                     if (backdrop) {
                         backdrop.remove();
                     }
                     // Restaurar el scroll del body
                     document.body.classList.remove('modal-open');
                     document.body.style.overflow = '';
                     document.body.style.paddingRight = '';
                 }
                 
                 // Actualizar la lista de reservas
                 await this.refreshReservasList();
                 
                 // Actualizar el calendario
                 await this.actualizarCalendario();
                 
                 // Actualizar el dashboard
                 await this.loadDashboard();
             }
             
         } catch (error) {
             console.error('❌ Error guardando reserva editada:', error);
             this.showAlert('Error al guardar la reserva', 'danger');
         }
     }

     // ===== FUNCIÓN PARA ACTUALIZAR RESERVA EXISTENTE =====
     
     async updateExistingReserva() {
         try {
             const reservaId = document.getElementById('newReservaForm').getAttribute('data-edit-id');
             
             if (!reservaId) {
                 // Si no hay ID de edición, crear nueva reserva
                 return this.createNewReserva();
             }
             
             // Validar campos obligatorios
             const clienteId = document.getElementById('newReservaCliente').value;
             const servicioId = document.getElementById('newReservaServicio').value;
             const recursoId = document.getElementById('newReservaRecurso').value;
             const fechaInicio = document.getElementById('newReservaFechaInicio').value;
             const fechaFin = document.getElementById('newReservaFechaFin').value;
             const estado = document.getElementById('newReservaEstado').value;
             
             if (!clienteId || !servicioId || !recursoId || !fechaInicio || !fechaFin) {
                 this.showAlert('Por favor completa todos los campos obligatorios', 'warning');
                 return;
             }
             
             // Validar que la fecha de fin sea posterior a la de inicio
             const fechaInicioObj = new Date(fechaInicio);
             const fechaFinObj = new Date(fechaFin);
             
             if (fechaFinObj <= fechaInicioObj) {
                 this.showAlert('La fecha de fin debe ser posterior a la fecha de inicio', 'warning');
                 return;
             }
             
             const formData = {
                 cliente_id: parseInt(clienteId),
                 servicio_id: parseInt(servicioId),
                 recurso_id: parseInt(recursoId),
                 fecha_hora_inicio: fechaInicio,
                 fecha_hora_fin: fechaFin,
                 estado: estado
             };

             console.log('💾 Actualizando reserva ID:', reservaId, 'con datos:', formData);
             
             const updatedReserva = await this.apiCall(`/reservas/${reservaId}`, 'PUT', formData);
             
             if (updatedReserva) {
                 // Mostrar mensaje de éxito
                 this.showReservaMessage('Reserva actualizada exitosamente', 'success');
                 
                 // Limpiar el formulario y resetear el modo de edición
                 document.getElementById('newReservaForm').reset();
                 document.getElementById('newReservaForm').removeAttribute('data-edit-id');
                 
                 // Restaurar título y botón del formulario
                 document.getElementById('reservaFormTitle').textContent = 'Nueva Reserva';
                 document.getElementById('reservaFormButtonText').textContent = 'Crear Reserva';
                 
                 // Ocultar el campo de ID de la reserva
                 document.getElementById('reservaIdField').style.display = 'none';
                 
                 // Actualizar la lista de reservas y los datos de recursos
                 await this.refreshReservasList();
                 
                 // También actualizar los datos de recursos para asegurar que se muestren los nombres correctos
                 const resourcesResponse = await this.apiCall('/recursos/');
                 if (resourcesResponse) {
                     this.currentData.resources = resourcesResponse;
                     console.log('🔄 Datos de recursos actualizados después de editar reserva');
                 }
                 
                 this.tabsLoaded.reservas = false;
             }
             
         } catch (error) {
             console.error('❌ Error actualizando reserva:', error);
             this.showReservaMessage('Error al actualizar la reserva', 'danger');
         }
     }
     
     // ===== FUNCIÓN PARA MOSTRAR MENSAJES EN EL FORMULARIO DE RESERVAS =====
     
     showReservaMessage(message, type = 'info') {
         const messageArea = document.getElementById('reservaMessageArea');
         const messageElement = document.getElementById('reservaMessage');
         const messageText = document.getElementById('reservaMessageText');
         
         // Configurar el mensaje
         messageText.textContent = message;
         
         // Configurar el tipo de alerta
         messageElement.className = `alert alert-${type}`;
         
         // Mostrar el área de mensajes
         messageArea.style.display = 'block';
         
         // Ocultar automáticamente después de 5 segundos para mensajes de éxito
         if (type === 'success') {
             setTimeout(() => {
                 messageArea.style.display = 'none';
             }, 5000);
         }
     }
     
     // ===== FUNCIÓN PARA LIMPIAR MENSAJES =====
     
     clearReservaMessage() {
         document.getElementById('reservaMessageArea').style.display = 'none';
     }

    // ========================================
    // MÉTODOS DEL CALENDARIO
    // ========================================

    /**
     * Inicializa el calendario y configura todos los eventos
     */
    async inicializarCalendario() {
        console.log('🗓️ Inicializando calendario...');
        
        try {
            // Cargar reservas
            console.log('🔄 Llamando a cargarReservasCalendario...');
            await this.cargarReservasCalendario();
            console.log('✅ cargarReservasCalendario completado');
            
            // Configurar eventos de navegación
            this.configurarEventosCalendario();
            
            // Poblar filtros
            this.poblarFiltrosCalendario();
            
            // Configurar búsqueda avanzada
            this.configurarBusquedaAvanzada();
            
            // Renderizar vista inicial
            this.renderizarCalendario();
            
            console.log('✅ Calendario inicializado correctamente');
        } catch (error) {
            console.error('❌ Error inicializando calendario:', error);
            this.mostrarErrorCalendario('Error al inicializar el calendario');
        }
    }

    /**
     * Carga las reservas para el calendario
     */
    async cargarReservasCalendario() {
        try {
            const response = await this.apiCall('/reservas/listar');
            if (response) {
                this.calendario.reservas = response;
                console.log(`📅 ${this.calendario.reservas.length} reservas cargadas para el calendario`);
                console.log('📋 Primeras reservas:', this.calendario.reservas.slice(0, 3));
                console.log('🔍 Estado del calendario después de cargar:', {
                    reservas: this.calendario.reservas.length,
                    filtros: this.calendario.filtros
                });
            } else {
                console.log('⚠️ No se recibieron reservas de la API');
            }
        } catch (error) {
            console.error('❌ Error cargando reservas del calendario:', error);
            this.calendario.reservas = [];
        }
    }

    /**
     * Configura los eventos del calendario
     */
    configurarEventosCalendario() {
        // Botones de vista
        document.getElementById('btnVistaMensual')?.addEventListener('click', () => {
            this.cambiarVistaCalendario('mensual');
        });
        
        document.getElementById('btnVistaSemanal')?.addEventListener('click', () => {
            this.cambiarVistaCalendario('semanal');
        });
        
        document.getElementById('btnVistaDiaria')?.addEventListener('click', () => {
            this.cambiarVistaCalendario('diaria');
        });

        // Botones de navegación
        document.getElementById('btnAnterior')?.addEventListener('click', () => {
            this.navegarCalendario(-1);
        });
        
        document.getElementById('btnHoy')?.addEventListener('click', () => {
            this.irHoy();
        });
        
        document.getElementById('btnSiguiente')?.addEventListener('click', () => {
            this.navegarCalendario(1);
        });

        // Botón de actualizar
        document.getElementById('btnActualizarCalendario')?.addEventListener('click', () => {
            this.actualizarCalendario();
        });

        // Filtros
        document.getElementById('filtroServicioCalendario')?.addEventListener('change', (e) => {
            this.calendario.filtros.servicio = e.target.value;
            this.renderizarCalendario();
        });
        
        document.getElementById('filtroRecursoCalendario')?.addEventListener('change', (e) => {
            this.calendario.filtros.recurso = e.target.value;
            this.renderizarCalendario();
        });
    }

    /**
     * Pobla los filtros del calendario
     */
    poblarFiltrosCalendario() {
        // Filtro de servicios
        const filtroServicio = document.getElementById('filtroServicioCalendario');
        if (filtroServicio) {
            filtroServicio.innerHTML = '<option value="">Todos los servicios</option>';
            this.currentData.services.forEach(servicio => {
                const option = document.createElement('option');
                option.value = servicio.id;
                option.textContent = servicio.nombre;
                filtroServicio.appendChild(option);
            });
        }

        // Filtro de recursos
        const filtroRecurso = document.getElementById('filtroRecursoCalendario');
        if (filtroRecurso) {
            filtroRecurso.innerHTML = '<option value="">Todos los recursos</option>';
            this.currentData.resources.forEach(recurso => {
                const option = document.createElement('option');
                option.value = recurso.id;
                option.textContent = recurso.nombre;
                filtroRecurso.appendChild(option);
            });
        }
    }

    /**
     * Cambia la vista del calendario
     */
    cambiarVistaCalendario(vista) {
        console.log(`🔄 Cambiando vista del calendario a: ${vista}`);
        this.calendario.vistaActual = vista;
        
        // Ocultar todas las vistas
        document.querySelectorAll('.calendario-vista').forEach(v => {
            v.style.display = 'none';
            console.log(`👁️ Ocultando vista: ${v.id}`);
        });
        
        // Mostrar la vista seleccionada
        const vistaSeleccionada = document.getElementById(`vista${vista.charAt(0).toUpperCase() + vista.slice(1)}`);
        if (vistaSeleccionada) {
            vistaSeleccionada.style.display = 'block';
            console.log(`👁️ Mostrando vista: ${vistaSeleccionada.id}`);
        } else {
            console.error(`❌ No se encontró la vista: vista${vista.charAt(0).toUpperCase() + vista.slice(1)}`);
        }
        
        // Actualizar botones activos
        document.querySelectorAll('#calendario .btn-group .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const botonActivo = document.getElementById(`btnVista${vista.charAt(0).toUpperCase() + vista.slice(1)}`);
        if (botonActivo) {
            botonActivo.classList.add('active');
            console.log(`🔘 Botón activo: ${botonActivo.id}`);
        }
        
        // Actualizar el calendario (incluye carga de reservas)
        this.actualizarCalendario();
        
        console.log(`✅ Vista del calendario cambiada a: ${vista}`);
    }

    /**
     * Navega por el calendario (mes anterior/siguiente, semana anterior/siguiente, día anterior/siguiente)
     */
    navegarCalendario(direccion) {
        const fecha = new Date(this.calendario.fechaActual);
        
        switch (this.calendario.vistaActual) {
            case 'mensual':
                fecha.setMonth(fecha.getMonth() + direccion);
                break;
            case 'semanal':
                fecha.setDate(fecha.getDate() + (direccion * 7));
                break;
            case 'diaria':
                fecha.setDate(fecha.getDate() + direccion);
                break;
        }
        
        this.calendario.fechaActual = fecha;
        this.actualizarTituloCalendario();
        this.actualizarCalendario();
        
        console.log(`🔄 Navegando calendario: ${direccion > 0 ? 'siguiente' : 'anterior'}`);
    }

    /**
     * Va al día de hoy
     */
    irHoy() {
        this.calendario.fechaActual = new Date();
        this.actualizarTituloCalendario();
        this.actualizarCalendario();
        
        console.log('🔄 Calendario movido a hoy');
    }

    /**
     * Actualiza el título del calendario
     */
    actualizarTituloCalendario() {
        const titulo = document.getElementById('calendarioTitulo');
        if (!titulo) return;

        const fecha = this.calendario.fechaActual;
        const opciones = { 
            year: 'numeric', 
            month: 'long' 
        };

        switch (this.calendario.vistaActual) {
            case 'mensual':
                titulo.textContent = fecha.toLocaleDateString('es-ES', opciones);
                break;
            case 'semanal':
                const inicioSemana = this.getInicioSemana(fecha);
                const finSemana = new Date(inicioSemana);
                finSemana.setDate(finSemana.getDate() + 6);
                titulo.textContent = `${inicioSemana.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })} - ${finSemana.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })}`;
                break;
            case 'diaria':
                titulo.textContent = fecha.toLocaleDateString('es-ES', { 
                    weekday: 'long', 
                    day: 'numeric', 
                    month: 'long' 
                });
                break;
        }
    }

    /**
     * Obtiene el inicio de la semana para una fecha dada
     */
    getInicioSemana(fecha) {
        const inicio = new Date(fecha);
        const dia = inicio.getDay();
        // Ajustar para que la semana empiece en lunes (1) en lugar de domingo (0)
        // Si es domingo (0), restamos 6 días para llegar al lunes anterior
        // Si es otro día, restamos (dia - 1) días para llegar al lunes de esa semana
        const diasARestar = dia === 0 ? 6 : dia - 1;
        inicio.setDate(inicio.getDate() - diasARestar);
        
        console.log(`🔍 getInicioSemana: fecha=${fecha.toISOString()}, dia=${dia}, diasARestar=${diasARestar}, resultado=${inicio.toISOString()}`);
        
        return inicio;
    }

    /**
     * Renderiza el calendario según la vista actual
     */
    renderizarCalendario() {
        console.log(`🎨 Renderizando calendario con vista: ${this.calendario.vistaActual}`);
        
        switch (this.calendario.vistaActual) {
            case 'mensual':
                console.log('📅 Renderizando vista mensual...');
                this.renderizarVistaMensual();
                break;
            case 'semanal':
                console.log('📅 Renderizando vista semanal...');
                this.renderizarVistaSemanal();
                break;
            case 'diaria':
                console.log('📅 Renderizando vista diaria...');
                this.renderizarVistaDiaria();
                break;
            default:
                console.error(`❌ Vista desconocida: ${this.calendario.vistaActual}`);
                break;
        }
    }

    /**
     * Renderiza la vista mensual del calendario - VERSIÓN REFACTORIZADA
     */
    renderizarVistaMensual() {
        const container = document.getElementById('calendarioMensual');
        if (!container) {
            console.error('❌ Contenedor calendarioMensual no encontrado');
            return;
        }

        console.log('🔍 Contenedor calendarioMensual encontrado:', container);
        
        // CONFIGURACIÓN SIMPLE DEL GRID
        container.style.display = 'grid';
        container.style.gridTemplateColumns = 'repeat(7, 1fr)';
        container.style.gridTemplateRows = 'repeat(6, 150px)';
        container.style.width = '100%';
        container.style.minWidth = '800px';
        container.style.gap = '1px';
        container.style.backgroundColor = '#e9ecef';

        const fecha = new Date(this.calendario.fechaActual);
        const primerDia = new Date(fecha.getFullYear(), fecha.getMonth(), 1);
        const ultimoDia = new Date(fecha.getFullYear(), fecha.getMonth() + 1, 0);
        const inicioSemana = this.getInicioSemana(primerDia);
        
        let html = '';
        let fechaActual = new Date(inicioSemana);
        
        console.log('🔍 Renderizando vista mensual:', {
            fechaActual: fecha.toISOString(),
            primerDia: primerDia.toISOString(),
            ultimoDia: ultimoDia.toISOString(),
            inicioSemana: inicioSemana.toISOString(),
            inicioSemanaDia: inicioSemana.getDay(),
            inicioSemanaNombre: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'][inicioSemana.getDay()]
        });
        
        // GENERAR CALENDARIO SIMPLE
        for (let semana = 0; semana < 6; semana++) {
            for (let dia = 0; dia < 7; dia++) {
                const esOtroMes = fechaActual.getMonth() !== fecha.getMonth();
                const esHoy = this.esHoy(fechaActual);
                
                // CLASE BASE PARA LA CELDA
                let claseCelda = 'calendario-dia-mensual';
                if (esOtroMes) claseCelda += ' otro-mes';
                if (esHoy) claseCelda += ' hoy';
                
                // Crear fecha en formato YYYY-MM-DD sin conversión UTC
                const fechaStr = fechaActual.getFullYear() + '-' + 
                                String(fechaActual.getMonth() + 1).padStart(2, '0') + '-' + 
                                String(fechaActual.getDate()).padStart(2, '0');
                
                html += `<div class="${claseCelda}" data-fecha="${fechaStr}">`;
                
                // NÚMERO DEL DÍA
                html += `<div class="dia-numero">${fechaActual.getDate()}</div>`;
                
                // RESERVAS DEL DÍA
                const reservasDelDia = this.getReservasDelDia(fechaActual);
                console.log(`🔍 Día ${fechaStr}: ${reservasDelDia.length} reservas encontradas`);
                
                if (reservasDelDia.length > 0) {
                    // CONTENEDOR DE RESERVAS
                    html += '<div class="reservas-container">';
                    
                    reservasDelDia.forEach(reserva => {
                        const cliente = this.currentData.clientes?.find(c => c.id === reserva.cliente_id);
                        const servicio = this.currentData.services.find(s => s.id === reserva.servicio_id);
                        
                        const nombreCliente = cliente ? cliente.nombre : `Cliente ${reserva.cliente_id}`;
                        const nombreServicio = servicio ? servicio.nombre : `Servicio ${reserva.servicio_id}`;
                        
                        html += `<div class="reserva-item ${reserva.estado}" 
                                       onclick="app.mostrarDetalleReserva(${reserva.id})"
                                       title="${nombreCliente} - ${nombreServicio}">
                                    <span class="reserva-texto">${nombreCliente} - ${nombreServicio}</span>
                                </div>`;
                    });
                    
                    html += '</div>';
                } else if (!esOtroMes) {
                    // INDICADOR DE DISPONIBILIDAD CLICKEABLE
                    html += `<div class="disponible-indicator clickeable" 
                                   onclick="app.abrirModalReservaDesdeCalendario('${fechaStr}')"
                                   title="Haz clic para crear una reserva en este día">
                        <i class="fas fa-plus-circle"></i>
                        <div>Hacer Reserva</div>
                    </div>`;
                }
                
                html += '</div>';
                fechaActual.setDate(fechaActual.getDate() + 1);
            }
        }
        
        console.log('📝 HTML generado para vista mensual:', html.substring(0, 500) + '...');
        container.innerHTML = html;
        
        this.actualizarTituloCalendario();
        console.log('✅ Vista mensual refactorizada renderizada correctamente');
    }

    /**
     * Renderiza la vista semanal del calendario
     */
    renderizarVistaSemanal() {
        const container = document.getElementById('calendarioSemanal');
        if (!container) {
            console.error('❌ Contenedor calendarioSemanal no encontrado');
            return;
        }

        console.log('🔍 Contenedor calendarioSemanal encontrado:', container);
        console.log('🔍 Estilos actuales del contenedor:', {
            display: container.style.display,
            gridTemplateColumns: container.style.gridTemplateColumns,
            width: container.style.width,
            minWidth: container.style.minWidth
        });

        const fecha = new Date(this.calendario.fechaActual);
        const inicioSemana = this.getInicioSemana(fecha);
        
        let html = '';
        
        // Generar horas del día (8:00 - 20:00)
        for (let hora = 8; hora <= 20; hora++) {
            const horaFormateada = hora.toString().padStart(2, '0') + ':00';
            html += `<div class="calendario-hora" style="display: flex; align-items: center; justify-content: center; font-weight: 600; background-color: #e9ecef; border-right: 2px solid #dee2e6; min-height: 80px; border-bottom: 1px solid #dee2e6;">${horaFormateada}</div>`;
            
            // Generar celdas para cada día de la semana
            for (let dia = 0; dia < 7; dia++) {
                const fechaDia = new Date(inicioSemana);
                fechaDia.setDate(inicioSemana.getDate() + dia);
                
                const esHoy = this.esHoy(fechaDia);
                const clasesCelda = ['calendario-celda-semanal'];
                if (esHoy) clasesCelda.push('hoy');
                
                const estilosCelda = 'border: 1px solid #dee2e6; padding: 8px; position: relative; background-color: #fff; min-height: 80px; min-width: 0; display: flex; flex-direction: column; overflow: hidden;';
                
                html += `<div class="${clasesCelda.join(' ')}" style="${estilosCelda}" data-fecha="${fechaDia.toISOString().split('T')[0]}" data-hora="${hora}">`;
                
                // La primera fila (08:00) ahora se comporta igual que las demás
                // No duplicamos la información del header superior
                
                // Agregar reservas en esta hora
                const reservasEnHora = this.getReservasEnHora(fechaDia, hora);
                if (reservasEnHora.length > 0) {
                    reservasEnHora.forEach(reserva => {
                        const cliente = this.currentData.clientes?.find(c => c.id === reserva.cliente_id);
                        const servicio = this.currentData.services.find(s => s.id === reserva.servicio_id);
                        const clasesReserva = ['calendario-reserva-detalle', reserva.estado];
                        
                        const estilosReserva = 'position: absolute; left: 4px; right: 4px; background-color: #007bff; color: white; padding: 6px 8px; border-radius: 6px; font-size: 11px; cursor: pointer; z-index: 10; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.2s;';
                        
                        html += `<div class="${clasesReserva.join(' ')}" 
                                       style="${estilosReserva}"
                                       onclick="app.mostrarDetalleReserva(${reserva.id})"
                                       title="${cliente ? cliente.nombre : `Cliente ${reserva.cliente_id}`} - ${servicio ? servicio.nombre : `Servicio ${reserva.servicio_id}`}">
                                    <div style="font-weight: 600; margin-bottom: 2px;">${cliente ? cliente.nombre : `Cliente ${reserva.cliente_id}`}</div>
                                    <div style="font-size: 10px; opacity: 0.9;">${servicio ? servicio.nombre : `Servicio ${reserva.servicio_id}`}</div>
                                </div>`;
                    });
                } else {
                    // Mostrar indicador de disponibilidad clickeable - FECHA CORREGIDA
                    const fechaDiaStr = fechaDia.getFullYear() + '-' + 
                                       String(fechaDia.getMonth() + 1).padStart(2, '0') + '-' + 
                                       String(fechaDia.getDate()).padStart(2, '0');
                    const horaFormateada = hora.toString().padStart(2, '0') + ':00';
                    html += `<div class="calendario-disponible-indicator clickeable" 
                                   onclick="app.abrirModalReservaDesdeCalendario('${fechaDiaStr}', ${hora})"
                                   title="Haz clic para crear una reserva en ${fechaDiaStr} a las ${horaFormateada}">
                        <i class="fas fa-plus-circle"></i>
                        <div>Hacer Reserva</div>
                    </div>`;
                }
                
                html += '</div>';
            }
        }
        
        console.log('📝 HTML generado para vista semanal:', html.substring(0, 500) + '...');
        container.innerHTML = html;
        
        // Verificar que el contenedor tenga los estilos correctos
        console.log('🔧 Aplicando estilos inline al contenedor semanal...');
        container.style.display = 'grid';
        container.style.gridTemplateColumns = '80px repeat(7, 1fr)';
        container.style.gridTemplateRows = 'repeat(13, 80px)'; // 13 filas para 8:00-20:00
        container.style.width = '100%';
        container.style.minWidth = '800px';
        container.style.minHeight = '1040px'; // 13 filas * 80px
        container.style.gap = '0';
        
        console.log('🔍 Estilos aplicados al contenedor semanal:', {
            display: container.style.display,
            gridTemplateColumns: container.style.gridTemplateColumns,
            width: container.style.width,
            minWidth: container.style.minWidth
        });
        
        this.actualizarTituloCalendario();
        console.log('✅ Vista semanal renderizada correctamente');
    }

    /**
     * Renderiza la vista diaria del calendario
     */
    renderizarVistaDiaria() {
        const container = document.getElementById('calendarioDiario');
        if (!container) {
            console.error('❌ Contenedor calendarioDiario no encontrado');
            return;
        }

        console.log('🔍 Contenedor calendarioDiario encontrado:', container);
        console.log('🔍 Estilos actuales del contenedor:', {
            display: container.style.display,
            gridTemplateColumns: container.style.gridTemplateColumns,
            width: container.style.width,
            minWidth: container.style.minWidth
        });

        const fecha = new Date(this.calendario.fechaActual);
        
        let html = '';
        
        // Generar horas del día (8:00 - 20:00)
        for (let hora = 8; hora <= 20; hora++) {
            const horaFormateada = hora.toString().padStart(2, '0') + ':00';
            html += `<div class="calendario-hora" style="display: flex; align-items: center; justify-content: center; font-weight: 600; background-color: #e9ecef; border-right: 2px solid #dee2e6; min-height: 80px;">${horaFormateada}</div>`;
            
            // Celda para el día completo
            const estilosCelda = 'border: 1px solid #dee2e6; padding: 12px; position: relative; background-color: #fff; min-height: 80px; min-width: 0;';
            
            html += `<div class="calendario-celda-diaria" style="${estilosCelda}" data-fecha="${fecha.toISOString().split('T')[0]}" data-hora="${hora}">`;
            
            // Agregar reservas en esta hora
            const reservasEnHora = this.getReservasEnHora(fecha, hora);
            if (reservasEnHora.length > 0) {
                reservasEnHora.forEach(reserva => {
                    const cliente = this.currentData.clientes?.find(c => c.id === reserva.cliente_id);
                    const servicio = this.currentData.services.find(s => s.id === reserva.servicio_id);
                    const clasesReserva = ['calendario-reserva-detalle', reserva.estado];
                    
                    // Estilos específicos para cada estado de reserva
                    let colorFondo = '#007bff';
                    let colorTexto = 'white';
                    
                    switch(reserva.estado) {
                        case 'pendiente':
                            colorFondo = '#ffc107';
                            colorTexto = '#212529';
                            break;
                        case 'confirmada':
                            colorFondo = '#28a745';
                            break;
                        case 'cancelada':
                            colorFondo = '#dc3545';
                            break;
                    }
                    
                    const estilosReserva = `background-color: ${colorFondo}; color: ${colorTexto}; padding: 8px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.2s; border-left: 4px solid ${colorFondo === '#ffc107' ? '#e0a800' : colorFondo};`;
                    
                    html += `<div class="${clasesReserva.join(' ')}" 
                                   style="${estilosReserva}"
                                   onclick="app.mostrarDetalleReserva(${reserva.id})"
                                   title="${cliente ? cliente.nombre : `Cliente ${reserva.cliente_id}`} - ${servicio ? servicio.nombre : `Servicio ${reserva.servicio_id}`}">
                                <div style="font-weight: 600; margin-bottom: 4px;">${cliente ? cliente.nombre : `Cliente ${reserva.cliente_id}`}</div>
                                <div style="font-size: 10px; opacity: 0.8; margin-bottom: 2px;">
                                    <span class="badge bg-secondary me-2">${reserva.estado}</span>
                                    ${servicio ? servicio.nombre : `Servicio ${reserva.servicio_id}`}
                                </div>
                                <div style="font-size: 9px; opacity: 0.7;">
                                    ${reserva.fecha_hora_inicio ? new Date(reserva.fecha_hora_inicio).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }) : ''} - 
                                    ${reserva.fecha_hora_fin ? new Date(reserva.fecha_hora_fin).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }) : ''}
                                </div>
                            </div>`;
                });
            } else {
                // Mostrar indicador de disponibilidad
                html += `<div class="calendario-disponible-indicator" style="text-align: center; color: #6c757d; font-size: 12px; opacity: 0.6; padding: 20px;">
                    <i class="fas fa-check-circle"></i>
                </div>`;
            }
            
            html += '</div>';
        }
        
        console.log('📝 HTML generado para vista diaria:', html.substring(0, 500) + '...');
        container.innerHTML = html;
        
        // Verificar que el contenedor tenga los estilos correctos
        console.log('🔧 Aplicando estilos inline al contenedor diario...');
        container.style.display = 'grid';
        container.style.gridTemplateColumns = '80px 1fr';
        container.style.width = '100%';
        container.style.minWidth = '800px';
        container.style.minHeight = '800px';
        container.style.gap = '0';
        
        console.log('🔍 Estilos aplicados al contenedor diario:', {
            display: container.style.display,
            gridTemplateColumns: container.style.gridTemplateColumns,
            width: container.style.width,
            minWidth: container.style.minWidth
        });
        
        this.actualizarTituloCalendario();
        console.log('✅ Vista diaria renderizada correctamente');
    }

    /**
     * Obtiene las reservas de un día específico
     */
    getReservasDelDia(fecha) {
        // Crear fecha en formato YYYY-MM-DD sin conversión UTC
        const fechaStr = fecha.getFullYear() + '-' + 
                        String(fecha.getMonth() + 1).padStart(2, '0') + '-' + 
                        String(fecha.getDate()).padStart(2, '0');
        
        return this.calendario.reservas.filter(reserva => {
            // Crear fecha de reserva en formato YYYY-MM-DD sin conversión UTC
            const reservaDate = new Date(reserva.fecha_hora_inicio);
            const reservaFecha = reservaDate.getFullYear() + '-' + 
                                String(reservaDate.getMonth() + 1).padStart(2, '0') + '-' + 
                                String(reservaDate.getDate()).padStart(2, '0');
            
            console.log('🔍 Comparando fechas:', {
                fechaCalendario: fechaStr,
                fechaReserva: reservaFecha,
                reservaOriginal: reserva.fecha_hora_inicio,
                reservaParseada: reservaDate.toLocaleString('es-ES')
            });
            
            return reservaFecha === fechaStr && this.aplicarFiltros(reserva);
        });
    }

    /**
     * Obtiene las reservas en una hora específica
     */
    getReservasEnHora(fecha, hora) {
        // Crear fecha en formato YYYY-MM-DD sin conversión UTC
        const fechaStr = fecha.getFullYear() + '-' + 
                        String(fecha.getMonth() + 1).padStart(2, '0') + '-' + 
                        String(fecha.getDate()).padStart(2, '0');
        
        return this.calendario.reservas.filter(reserva => {
            // Crear fecha de reserva en formato YYYY-MM-DD sin conversión UTC
            const reservaDate = new Date(reserva.fecha_hora_inicio);
            const reservaFecha = reservaDate.getFullYear() + '-' + 
                                String(reservaDate.getMonth() + 1).padStart(2, '0') + '-' + 
                                String(reservaDate.getDate()).padStart(2, '0');
            const reservaHora = reservaDate.getHours();
            
            return reservaFecha === fechaStr && reservaHora === hora && this.aplicarFiltros(reserva);
        });
    }

    /**
     * Aplica los filtros del calendario a una reserva
     */
    aplicarFiltros(reserva) {
        console.log(`🔍 Aplicando filtros a reserva ${reserva.id}:`, {
            reserva: reserva,
            filtros: this.calendario.filtros
        });
        
        if (this.calendario.filtros.servicio && reserva.servicio_id != this.calendario.filtros.servicio) {
            console.log(`❌ Reserva ${reserva.id} filtrada por servicio`);
            return false;
        }
        if (this.calendario.filtros.recurso && reserva.recurso_id != this.calendario.filtros.recurso) {
            console.log(`❌ Reserva ${reserva.id} filtrada por recurso`);
            return false;
        }
        console.log(`✅ Reserva ${reserva.id} pasa los filtros`);
        return true;
    }

    /**
     * Verifica si una fecha es hoy
     */
    esHoy(fecha) {
        const hoy = new Date();
        return fecha.toDateString() === hoy.toDateString();
    }

    /**
     * Cierra todos los modales abiertos y limpia el estado del body
     */
    cerrarTodosLosModales() {
        // Cerrar todos los modales de Bootstrap
        const modales = document.querySelectorAll('.modal');
        modales.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });

        // Eliminar todos los backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());

        // Restaurar el estado del body
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';

        console.log('🔒 Todos los modales han sido cerrados');
    }

    /**
     * Función de prueba para verificar el comportamiento de los modales
     */
    testModal() {
        console.log('🧪 Probando modal...');
        
        // Verificar que Bootstrap esté disponible
        if (typeof bootstrap === 'undefined') {
            console.error('❌ Bootstrap no está disponible');
            return;
        }
        
        console.log('✅ Bootstrap disponible:', bootstrap);
        
        // Verificar que el modal existe
        const modalElement = document.getElementById('editServiceModal');
        if (!modalElement) {
            console.error('❌ Modal editServiceModal no encontrado');
            return;
        }
        
        console.log('✅ Modal encontrado:', modalElement);
        
        // Verificar las clases CSS
        console.log('🔍 Clases del modal:', modalElement.className);
        console.log('🔍 Clases del modal-dialog:', modalElement.querySelector('.modal-dialog')?.className);
        
        // Intentar abrir el modal
        try {
            const modal = new bootstrap.Modal(modalElement);
            console.log('✅ Modal creado:', modal);
            modal.show();
            console.log('✅ Modal mostrado');
        } catch (error) {
            console.error('❌ Error al mostrar modal:', error);
        }
    }

    /**
     * Abre un modal de forma optimizada y centrada
     */
    abrirModal(modalId, opciones = {}) {
        const modalElement = document.getElementById(modalId);
        if (!modalElement) {
            console.error(`❌ Modal ${modalId} no encontrado`);
            return null;
        }

        // Configuración por defecto
        const config = {
            backdrop: true,
            keyboard: true,
            focus: true,
            ...opciones
        };

        // Crear y mostrar el modal
        const modal = new bootstrap.Modal(modalElement, config);
        modal.show();

        return modal;
    }

    /**
     * Abre el modal de gestión de precios para un recurso
     */
    gestionarPreciosRecurso(resourceId, resourceName, basePrice) {
        try {
            console.log('💰 Gestionando precios del recurso:', resourceId, resourceName, basePrice);
            
            // Llenar la información del recurso en el modal
            document.getElementById('resourcePricingName').textContent = resourceName;
            document.getElementById('resourcePricingBasePrice').textContent = basePrice.toFixed(2);
            
            // Llenar el formulario de precio base
            document.getElementById('editResourceBasePrice').value = basePrice;
            
            // Cargar las reglas de precio existentes
            this.cargarReglasPrecioRecurso(resourceId);
            
            // Mostrar el modal
            const modal = this.abrirModal('resourcePricingModal');
            
        } catch (error) {
            console.error('❌ Error abriendo gestión de precios:', error);
            this.showAlert('Error al abrir la gestión de precios', 'danger');
        }
    }

    /**
     * Carga las reglas de precio existentes para un recurso
     */
    async cargarReglasPrecioRecurso(resourceId) {
        try {
            console.log('🔄 Cargando reglas de precio para recurso:', resourceId);
            
            // Cargar reglas por hora
            await this.cargarReglasPrecioHora(resourceId);
            
            // Cargar reglas por día
            await this.cargarReglasPrecioDia(resourceId);
            
            // Cargar reglas por temporada
            await this.cargarReglasPrecioTemporada(resourceId);
            
        } catch (error) {
            console.error('❌ Error cargando reglas de precio:', error);
        }
    }

    /**
     * Carga las reglas de precio por hora para un recurso
     */
    async cargarReglasPrecioHora(resourceId) {
        try {
            // Aquí se haría la llamada a la API para obtener las reglas
            // Por ahora, mostrar un mensaje de ejemplo
            const container = document.getElementById('resourceHourlyPriceRules');
            if (container) {
                container.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-clock fa-2x mb-2"></i>
                        <p>No hay reglas de precio por hora configuradas</p>
                        <p class="small">Crea la primera regla usando el formulario</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('❌ Error cargando reglas por hora:', error);
        }
    }

    /**
     * Carga las reglas de precio por día para un recurso
     */
    async cargarReglasPrecioDia(resourceId) {
        try {
            const container = document.getElementById('resourceDailyPriceRules');
            if (container) {
                container.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-calendar-day fa-2x mb-2"></i>
                        <p>No hay reglas de precio por día configuradas</p>
                        <p class="small">Crea la primera regla usando el formulario</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('❌ Error cargando reglas por día:', error);
        }
    }

    /**
     * Carga las reglas de precio por temporada para un recurso
     */
    async cargarReglasPrecioTemporada(resourceId) {
        try {
            const container = document.getElementById('resourceSeasonalPriceRules');
            if (container) {
                container.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-calendar-week fa-2x mb-2"></i>
                        <p>No hay reglas de precio por temporada configuradas</p>
                        <p class="small">Crea la primera regla usando el formulario</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('❌ Error cargando reglas por temporada:', error);
        }
    }

    /**
     * Muestra el detalle de un recurso en un modal
     */
    mostrarDetalleRecurso(resourceId) {
        const resource = this.currentData.resources?.find(r => r.id === resourceId);
        if (!resource) {
            console.error('❌ Recurso no encontrado:', resourceId);
            return;
        }

        const detalle = document.getElementById('infoResourceDetalleModal');
        
        if (detalle) {
            detalle.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-building me-2"></i>Nombre del Recurso</h6>
                        <p class="mb-3">${resource.nombre}</p>
                        
                        <h6><i class="fas fa-tag me-2"></i>Tipo de Recurso</h6>
                        <p class="mb-3">${resource.tipo || 'No especificado'}</p>
                        
                        <h6><i class="fas fa-users me-2"></i>Capacidad</h6>
                        <p class="mb-3">${resource.capacidad || 1} persona(s)</p>
                        
                        <h6><i class="fas fa-euro-sign me-2"></i>Precio Base</h6>
                        <p class="mb-3">€${resource.precio_base ? resource.precio_base.toFixed(2) : '0.00'} /hora</p>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-info-circle me-2"></i>Descripción</h6>
                        <p class="mb-3">${resource.descripcion || 'Sin descripción'}</p>
                        
                        <h6><i class="fas fa-toggle-on me-2"></i>Estado</h6>
                        <span class="badge bg-${resource.disponible ? 'success' : 'danger'} mb-3">
                            <i class="fas fa-${resource.disponible ? 'check' : 'times'} me-1"></i>
                            ${resource.disponible ? 'Disponible' : 'No Disponible'}
                        </span>
                        
                        <h6><i class="fas fa-calendar me-2"></i>Fecha de Creación</h6>
                        <p class="mb-3">${resource.fecha_creacion ? new Date(resource.fecha_creacion).toLocaleDateString('es-ES') : 'No disponible'}</p>
                    </div>
                </div>
                <div class="mt-3">
                    <button class="btn btn-primary btn-sm me-2" onclick="app.editResource(${resource.id})">
                        <i class="fas fa-edit me-1"></i>Editar
                    </button>
                    <button class="btn btn-info btn-sm me-2" onclick="app.gestionarPreciosRecurso(${resource.id}, '${resource.nombre}', ${resource.precio_base || 0})">
                        <i class="fas fa-euro-sign me-1"></i>Gestionar Precios
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="app.deleteResource(${resource.id}, '${resource.nombre}')">
                        <i class="fas fa-trash me-1"></i>Eliminar
                    </button>
                </div>
            `;
            
            // Mostrar el modal usando la función optimizada
            const modal = this.abrirModal('infoResourceModal');
        }
    }

    /**
     * Muestra el detalle de una reserva en un modal
     */
    mostrarDetalleReserva(reservaId) {
        const reserva = this.calendario.reservas.find(r => r.id === reservaId);
        if (!reserva) return;

        const detalle = document.getElementById('infoReservaDetalleModal');
        
        if (detalle) {
            const cliente = this.currentData.clientes?.find(c => c.id === reserva.cliente_id);
            const servicio = this.currentData.services.find(s => s.id === reserva.servicio_id);
            const recurso = this.currentData.resources.find(r => r.id === reserva.recurso_id);
            
            detalle.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-user me-2"></i>Cliente</h6>
                        <p>${cliente ? cliente.nombre : `ID: ${reserva.cliente_id}`}</p>
                        
                        <h6><i class="fas fa-cog me-2"></i>Servicio</h6>
                        <p>${servicio ? servicio.nombre : `ID: ${reserva.servicio_id}`}</p>
                        
                        <h6><i class="fas fa-building me-2"></i>Recurso</h6>
                        <p>${recurso ? recurso.nombre : `ID: ${reserva.recurso_id}`}</p>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-calendar me-2"></i>Fecha y Hora</h6>
                        <p>Inicio: ${new Date(reserva.fecha_hora_inicio).toLocaleString('es-ES')}</p>
                        <p>Fin: ${new Date(reserva.fecha_hora_fin).toLocaleString('es-ES')}</p>
                        
                        <h6><i class="fas fa-info-circle me-2"></i>Estado</h6>
                        <span class="badge bg-${this.getEstadoBadgeColor(reserva.estado)}">${reserva.estado.toUpperCase()}</span>
                        
                        <h6><i class="fas fa-euro-sign me-2"></i>Precio</h6>
                        <p>€${reserva.precio_final || 'N/A'}</p>
                    </div>
                </div>
                <div class="mt-3">
                    <button class="btn btn-primary btn-sm me-2" onclick="app.editReserva(${reserva.id})">
                        <i class="fas fa-edit me-1"></i>Editar
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="app.deleteReserva(${reserva.id}, '${cliente ? cliente.nombre : 'Reserva'}')">
                        <i class="fas fa-trash me-1"></i>Eliminar
                    </button>
                </div>
            `;
            
            // Mostrar el modal usando la función optimizada
            const modal = this.abrirModal('infoReservaModal');
        }
    }

    /**
     * Actualiza el calendario
     */
    async actualizarCalendario() {
        try {
            await this.cargarReservasCalendario();
            this.renderizarCalendario();
            console.log('✅ Calendario actualizado');
        } catch (error) {
            console.error('❌ Error actualizando calendario:', error);
            this.mostrarErrorCalendario('Error al actualizar el calendario');
        }
    }

    /**
     * Muestra un error en el calendario
     */
    mostrarErrorCalendario(mensaje) {
        const container = document.getElementById('calendarioMensual');
        if (container) {
            container.innerHTML = `
                <div class="calendario-cargando">
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>${mensaje}
                    </div>
                </div>
            `;
        }
    }

    /**
     * Configura la búsqueda avanzada de disponibilidad
     */
    configurarBusquedaAvanzada() {
        // Poblar selectores de búsqueda
        this.poblarSelectoresBusqueda();
        
        // Configurar evento de búsqueda
        document.getElementById('btnBuscarDisponibilidad')?.addEventListener('click', () => {
            this.buscarDisponibilidad();
        });
        
        // Configurar fecha por defecto
        const fechaInput = document.getElementById('busquedaFecha');
        if (fechaInput) {
            const hoy = new Date();
            fechaInput.value = hoy.toISOString().split('T')[0];
        }
        
        // Configurar hora por defecto
        const horaInput = document.getElementById('busquedaHora');
        if (horaInput) {
            const ahora = new Date();
            horaInput.value = `${ahora.getHours().toString().padStart(2, '0')}:${ahora.getMinutes().toString().padStart(2, '0')}`;
        }
    }

    /**
     * Configura los formularios de precios de recursos
     */
    configurarFormulariosPreciosRecursos() {
        // Formulario de precio base
        document.getElementById('editResourceBasePriceForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.actualizarPrecioBaseRecurso();
        });

        // Formulario de precio por hora
        document.getElementById('newResourceHourlyPriceForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.crearReglaPrecioHora();
        });

        // Formulario de precio por día
        document.getElementById('newResourceDailyPriceForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.crearReglaPrecioDia();
        });

        // Formulario de precio por temporada
        document.getElementById('newResourceSeasonalPriceForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.crearReglaPrecioTemporada();
        });
    }

    /**
     * Actualiza el precio base de un recurso
     */
    async actualizarPrecioBaseRecurso() {
        try {
            const nuevoPrecio = parseFloat(document.getElementById('editResourceBasePrice').value);
            if (isNaN(nuevoPrecio) || nuevoPrecio < 0) {
                this.showAlert('Por favor, ingresa un precio válido', 'warning');
                return;
            }

            // Aquí se haría la llamada a la API para actualizar el precio base
            console.log('💰 Actualizando precio base del recurso:', nuevoPrecio);
            
            // Por ahora, solo mostrar mensaje de éxito
            this.showAlert('Precio base actualizado correctamente', 'success');
            
            // Actualizar la información mostrada
            document.getElementById('resourcePricingBasePrice').textContent = nuevoPrecio.toFixed(2);
            
        } catch (error) {
            console.error('❌ Error actualizando precio base:', error);
            this.showAlert('Error al actualizar el precio base', 'danger');
        }
    }

    /**
     * Crea una nueva regla de precio por hora
     */
    async crearReglaPrecioHora() {
        try {
            const formData = {
                nombre: document.getElementById('newResourceHourlyPriceName').value,
                hora_inicio: document.getElementById('newResourceHourlyPriceStart').value,
                hora_fin: document.getElementById('newResourceHourlyPriceEnd').value,
                tipo_modificador: document.getElementById('newResourceHourlyPriceModifier').value,
                valor_modificador: parseFloat(document.getElementById('newResourceHourlyPriceValue').value)
            };

            console.log('💰 Creando regla de precio por hora:', formData);
            
            // Aquí se haría la llamada a la API para crear la regla
            // Por ahora, solo mostrar mensaje de éxito
            this.showAlert('Regla de precio por hora creada correctamente', 'success');
            
            // Limpiar formulario
            document.getElementById('newResourceHourlyPriceForm').reset();
            
            // Recargar las reglas
            // this.cargarReglasPrecioHora(resourceId);
            
        } catch (error) {
            console.error('❌ Error creando regla por hora:', error);
            this.showAlert('Error al crear la regla de precio', 'danger');
        }
    }

    /**
     * Crea una nueva regla de precio por día
     */
    async crearReglaPrecioDia() {
        try {
            const diasSeleccionados = [];
            const checkboxes = [
                'newResourceDailyPriceMonday',
                'newResourceDailyPriceTuesday', 
                'newResourceDailyPriceWednesday',
                'newResourceDailyPriceThursday',
                'newResourceDailyPriceFriday',
                'newResourceDailyPriceSaturday',
                'newResourceDailyPriceSunday'
            ];

            checkboxes.forEach(id => {
                const checkbox = document.getElementById(id);
                if (checkbox && checkbox.checked) {
                    diasSeleccionados.push(parseInt(checkbox.value));
                }
            });

            if (diasSeleccionados.length === 0) {
                this.showAlert('Por favor, selecciona al menos un día', 'warning');
                return;
            }

            const formData = {
                nombre: document.getElementById('newResourceDailyPriceName').value,
                dias: diasSeleccionados,
                tipo_modificador: document.getElementById('newResourceDailyPriceModifier').value,
                valor_modificador: parseFloat(document.getElementById('newResourceDailyPriceValue').value)
            };

            console.log('💰 Creando regla de precio por día:', formData);
            
            // Aquí se haría la llamada a la API para crear la regla
            this.showAlert('Regla de precio por día creada correctamente', 'success');
            
            // Limpiar formulario
            document.getElementById('newResourceDailyPriceForm').reset();
            
        } catch (error) {
            console.error('❌ Error creando regla por día:', error);
            this.showAlert('Error al crear la regla de precio', 'danger');
        }
    }

    /**
     * Crea una nueva regla de precio por temporada
     */
    async crearReglaPrecioTemporada() {
        try {
            const formData = {
                nombre: document.getElementById('newResourceSeasonalPriceName').value,
                fecha_inicio: document.getElementById('newResourceSeasonalPriceStart').value,
                fecha_fin: document.getElementById('newResourceSeasonalPriceEnd').value,
                tipo_modificador: document.getElementById('newResourceSeasonalPriceModifier').value,
                valor_modificador: parseFloat(document.getElementById('newResourceSeasonalPriceValue').value)
            };

            console.log('💰 Creando regla de precio por temporada:', formData);
            
            // Aquí se haría la llamada a la API para crear la regla
            this.showAlert('Regla de precio por temporada creada correctamente', 'success');
            
            // Limpiar formulario
            document.getElementById('newResourceSeasonalPriceForm').reset();
            
        } catch (error) {
            console.error('❌ Error creando regla por temporada:', error);
            this.showAlert('Error al crear la regla de precio', 'danger');
        }
    }

    /**
     * Pobla los selectores de búsqueda avanzada
     */
    poblarSelectoresBusqueda() {
        // Selector de servicio
        const selectorServicio = document.getElementById('busquedaServicio');
        if (selectorServicio) {
            selectorServicio.innerHTML = '<option value="">Seleccionar servicio</option>';
            this.currentData.services.forEach(servicio => {
                const option = document.createElement('option');
                option.value = servicio.id;
                option.textContent = servicio.nombre;
                selectorServicio.appendChild(option);
            });
        }

        // Selector de recurso
        const selectorRecurso = document.getElementById('busquedaRecurso');
        if (selectorRecurso) {
            selectorRecurso.innerHTML = '<option value="">Seleccionar recurso</option>';
            this.currentData.resources.forEach(recurso => {
                const option = document.createElement('option');
                option.value = recurso.id;
                option.textContent = recurso.nombre;
                selectorRecurso.appendChild(option);
            });
        }
    }

    /**
     * Busca disponibilidad según los criterios especificados
     */
    async buscarDisponibilidad() {
        const servicio = document.getElementById('busquedaServicio').value;
        const recurso = document.getElementById('busquedaRecurso').value;
        const fecha = document.getElementById('busquedaFecha').value;
        const hora = document.getElementById('busquedaHora').value;

        if (!fecha) {
            this.mostrarMensajeDisponibilidad('Por favor, selecciona una fecha', 'warning');
            return;
        }

        try {
            // Construir parámetros de búsqueda
            const params = new URLSearchParams();
            if (servicio) params.append('servicio_id', servicio);
            if (recurso) params.append('recurso_id', recurso);
            params.append('fecha', fecha);
            if (hora) params.append('hora', hora);

            // Llamar a la API de disponibilidad avanzada
            const response = await this.apiCall(`/reservas/disponibilidad/avanzada?${params.toString()}`);
            
            if (response && response.slots_disponibles && response.slots_disponibles.length > 0) {
                this.mostrarResultadosDisponibilidad(response.slots_disponibles, fecha, hora);
            } else {
                // No hay disponibilidad, generar sugerencias alternativas
                this.mostrarMensajeDisponibilidad('No hay disponibilidad para los criterios especificados. Buscando alternativas...', 'warning');
                
                const sugerencias = await this.generarSugerenciasHorarios(fecha, hora, servicio, recurso);
                this.mostrarSugerenciasHorarios(sugerencias);
            }
        } catch (error) {
            console.error('❌ Error buscando disponibilidad:', error);
            this.mostrarMensajeDisponibilidad('Error al buscar disponibilidad', 'danger');
        }
    }

    /**
     * Muestra los resultados de disponibilidad
     */
    mostrarResultadosDisponibilidad(resultados, fecha, hora) {
        const resultadosDiv = document.getElementById('disponibilidadResultados');
        const resultadosContainer = document.getElementById('resultadosDisponibilidad');
        
        if (!resultadosDiv || !resultadosContainer) return;

        let html = '';
        
        if (resultados.length === 0) {
            html = '<p class="text-muted">No hay disponibilidad para los criterios especificados.</p>';
        } else {
            html = '<div class="row">';
            resultados.forEach(slot => {
                const horaInicio = new Date(slot.hora_inicio).toLocaleTimeString('es-ES', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
                const horaFin = new Date(slot.hora_fin).toLocaleTimeString('es-ES', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
                
                html += `
                    <div class="col-md-6 mb-2">
                        <div class="card border-success">
                            <div class="card-body p-2">
                                <h6 class="card-title mb-1">
                                    <i class="fas fa-clock text-success me-2"></i>${horaInicio} - ${horaFin}
                                </h6>
                                <p class="card-text mb-1">
                                    <strong>Recurso:</strong> ${slot.recurso_nombre || `ID: ${slot.recurso_id}`}
                                </p>
                                <p class="card-text mb-1">
                                    <strong>Servicio:</strong> ${slot.servicio_nombre || `ID: ${slot.servicio_id}`}
                                </p>
                                <p class="card-text mb-0">
                                    <strong>Precio:</strong> €${slot.precio_final || slot.precio_base || 'N/A'}
                                </p>
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        }

        resultadosDiv.innerHTML = html;
        resultadosContainer.style.display = 'block';
        
        console.log(`✅ Resultados de disponibilidad mostrados: ${resultados.length} slots encontrados`);
    }

    /**
     * Muestra un mensaje en el área de disponibilidad
     */
    mostrarMensajeDisponibilidad(mensaje, tipo = 'info') {
        const resultadosDiv = document.getElementById('disponibilidadResultados');
        const resultadosContainer = document.getElementById('resultadosDisponibilidad');
        
        if (resultadosDiv && resultadosContainer) {
            resultadosDiv.innerHTML = `
                <div class="alert alert-${tipo} mb-0" role="alert">
                    <i class="fas fa-info-circle me-2"></i>${mensaje}
                </div>
            `;
            resultadosContainer.style.display = 'block';
        }
    }

    /**
     * Genera sugerencias de horarios alternativos
     */
    async generarSugerenciasHorarios(fecha, hora, servicio, recurso) {
        try {
            // Buscar disponibilidad en fechas cercanas
            const fechasAlternativas = this.generarFechasAlternativas(fecha);
            const sugerencias = [];

            for (const fechaAlt of fechasAlternativas) {
                const params = new URLSearchParams();
                if (servicio) params.append('servicio_id', servicio);
                if (recurso) params.append('recurso_id', recurso);
                params.append('fecha', fechaAlt);
                if (hora) params.append('hora', hora);

                try {
                    const response = await this.apiCall(`/reservas/disponibilidad?${params.toString()}`);
                    if (response && response.length > 0) {
                        sugerencias.push({
                            fecha: fechaAlt,
                            slots: response,
                            diferencia: this.calcularDiferenciaDias(fecha, fechaAlt)
                        });
                    }
                } catch (error) {
                    console.warn(`⚠️ Error buscando disponibilidad para ${fechaAlt}:`, error);
                }
            }

            return sugerencias;
        } catch (error) {
            console.error('❌ Error generando sugerencias:', error);
            return [];
        }
    }

    /**
     * Genera fechas alternativas para buscar disponibilidad
     */
    generarFechasAlternativas(fecha) {
        const fechas = [];
        const fechaObj = new Date(fecha);
        
        // Generar fechas para los próximos 7 días
        for (let i = 1; i <= 7; i++) {
            const fechaAlt = new Date(fechaObj);
            fechaAlt.setDate(fechaAlt.getDate() + i);
            fechas.push(fechaAlt.toISOString().split('T')[0]);
        }
        
        // Generar fechas para los días anteriores (hasta 3 días)
        for (let i = 1; i <= 3; i++) {
            const fechaAlt = new Date(fechaObj);
            fechaAlt.setDate(fechaAlt.getDate() - i);
            fechas.push(fechaAlt.toISOString().split('T')[0]);
        }
        
        return fechas;
    }

    /**
     * Calcula la diferencia en días entre dos fechas
     */
    calcularDiferenciaDias(fecha1, fecha2) {
        const d1 = new Date(fecha1);
        const d2 = new Date(fecha2);
        const diffTime = Math.abs(d2 - d1);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    }

    /**
     * Muestra sugerencias de horarios alternativos
     */
    mostrarSugerenciasHorarios(sugerencias) {
        const resultadosDiv = document.getElementById('disponibilidadResultados');
        const resultadosContainer = document.getElementById('resultadosDisponibilidad');
        
        if (!resultadosDiv || !resultadosContainer) return;

        if (sugerencias.length === 0) {
            resultadosDiv.innerHTML = `
                <div class="alert alert-warning mb-0" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    No hay disponibilidad en fechas cercanas. Te recomendamos contactar directamente para coordinar un horario especial.
                </div>
            `;
        } else {
            let html = `
                <div class="alert alert-info mb-3" role="alert">
                    <i class="fas fa-lightbulb me-2"></i>
                    <strong>Horarios alternativos disponibles:</strong>
                </div>
                <div class="row">
            `;
            
            sugerencias.forEach(sugerencia => {
                const fechaFormateada = new Date(sugerencia.fecha).toLocaleDateString('es-ES', {
                    weekday: 'long',
                    day: 'numeric',
                    month: 'long'
                });
                
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="card border-info">
                            <div class="card-header bg-info text-white">
                                <h6 class="mb-0">
                                    <i class="fas fa-calendar-alt me-2"></i>
                                    ${fechaFormateada}
                                    <span class="badge bg-light text-dark float-end">
                                        ${sugerencia.diferencia === 1 ? 'Mañana' : 
                                          sugerencia.diferencia === -1 ? 'Ayer' : 
                                          sugerencia.diferencia > 0 ? `+${sugerencia.diferencia} días` : 
                                          `${Math.abs(sugerencia.diferencia)} días atrás`}
                                    </span>
                                </h6>
                            </div>
                            <div class="card-body">
                                <p class="text-muted mb-2">${sugerencia.slots.length} slots disponibles</p>
                                ${sugerencia.slots.slice(0, 3).map(slot => {
                                    const horaInicio = new Date(slot.hora_inicio).toLocaleTimeString('es-ES', { 
                                        hour: '2-digit', 
                                        minute: '2-digit' 
                                    });
                                    const horaFin = new Date(slot.hora_fin).toLocaleTimeString('es-ES', { 
                                        hour: '2-digit', 
                                        minute: '2-digit' 
                                    });
                                    return `
                                        <div class="d-flex justify-content-between align-items-center mb-1">
                                            <span><i class="fas fa-clock text-info me-2"></i>${horaInicio} - ${horaFin}</span>
                                            <span class="badge bg-success">€${slot.precio_final || slot.precio_base || 'N/A'}</span>
                                        </div>
                                    `;
                                }).join('')}
                                ${sugerencia.slots.length > 3 ? `<p class="text-muted mb-0">... y ${sugerencia.slots.length - 3} más</p>` : ''}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            resultadosDiv.innerHTML = html;
        }
        
        resultadosContainer.style.display = 'block';
    }

    // ===== FUNCIONES DEL MODAL DE RESERVAS DEL CALENDARIO =====

    /**
     * Abre el modal de reservas desde el calendario
     */
    async abrirModalReservaDesdeCalendario(fechaSeleccionada, hora = null) {
        try {
            console.log('📅 🚀 VERSIÓN 2.9 - Calendario con fechas UTC corregidas:', fechaSeleccionada, 'hora:', hora, new Date().toISOString());
            console.log('🔍 DOM ready state:', document.readyState);
            console.log('🔍 Modal en DOM:', !!document.getElementById('calendarioReservaModal'));
            
            // Verificar que el modal existe
            let modalElement = document.getElementById('calendarioReservaModal');
            if (!modalElement) {
                console.error('❌ Modal no encontrado. Intentando esperar...');
                // Esperar un poco y verificar de nuevo
                await new Promise(resolve => setTimeout(resolve, 100));
                modalElement = document.getElementById('calendarioReservaModal');
                if (!modalElement) {
                    throw new Error('Modal de reservas no encontrado en el DOM después de esperar');
                }
            }
            
            console.log('✅ Modal encontrado en DOM:', modalElement);
            console.log('🔍 Modal HTML:', modalElement.outerHTML.substring(0, 200) + '...');
            
            // Verificar que todos los elementos del modal estén presentes
            const elementosRequeridos = [
                'periodoSeleccionado',
                'calendarioReservaFechaInicio',
                'calendarioReservaFechaFin',
                'calendarioReservaCliente',
                'calendarioReservaServicio',
                'calendarioReservaRecurso'
            ];
            
            const elementosEncontrados = elementosRequeridos.map(id => ({
                id,
                encontrado: !!document.getElementById(id),
                elemento: document.getElementById(id)
            }));
            
            console.log('🔍 Elementos del modal:', elementosEncontrados);
            
            // Verificar que todos los elementos estén presentes
            const elementosFaltantes = elementosEncontrados.filter(el => !el.encontrado);
            if (elementosFaltantes.length > 0) {
                console.error('❌ Elementos faltantes en el modal:', elementosFaltantes.map(el => el.id));
                throw new Error(`Elementos faltantes en el modal: ${elementosFaltantes.map(el => el.id).join(', ')}`);
            }
            
            // Formatear la fecha para mostrar - CORREGIDO para evitar problemas de zona horaria
            console.log('🔍 Fecha seleccionada original:', fechaSeleccionada);
            
            // Crear fecha usando componentes individuales para evitar problemas de zona horaria
            const [year, month, day] = fechaSeleccionada.split('-').map(Number);
            const fecha = new Date(year, month - 1, day); // month - 1 porque JavaScript usa 0-11 para meses
            
            console.log('🔍 Fecha creada localmente:', fecha.toDateString());
            console.log('🔍 Fecha en formato local:', fecha.toLocaleDateString('es-ES'));
            
            let fechaFormateada = fecha.toLocaleDateString('es-ES', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            // Si hay hora específica, agregarla al formato
            if (hora !== null) {
                const horaFormateada = hora.toString().padStart(2, '0') + ':00';
                fechaFormateada += ` a las ${horaFormateada}`;
            }
            
            // Verificar y actualizar el título del modal
            const periodoElement = document.getElementById('periodoSeleccionado');
            if (periodoElement) {
                periodoElement.textContent = fechaFormateada;
            } else {
                console.warn('⚠️ Elemento periodoSeleccionado no encontrado');
            }
            
            // Establecer la fecha de inicio por defecto - CORREGIDO
            const fechaInicio = new Date(year, month - 1, day);
            if (hora !== null) {
                fechaInicio.setHours(hora, 0, 0, 0);
            } else {
                fechaInicio.setHours(9, 0, 0, 0); // 9:00 AM por defecto
            }
            
            // Establecer la fecha de fin por defecto (1 hora después) - TEMPORAL
            const fechaFin = new Date(fechaInicio);
            fechaFin.setHours(fechaInicio.getHours() + 1, 0, 0, 0);
            
            console.log('🔍 Fechas configuradas:', {
                fechaInicio: fechaInicio.toLocaleString('es-ES'),
                fechaFin: fechaFin.toLocaleString('es-ES')
            });
            
            // Formatear fechas para los inputs datetime-local - CORREGIDO
            const fechaInicioStr = fechaInicio.toISOString().slice(0, 16);
            const fechaFinStr = fechaFin.toISOString().slice(0, 16);
            
            console.log('🔍 Fechas para inputs:', { fechaInicioStr, fechaFinStr });
            
            // Verificar y establecer valores en el formulario
            const fechaInicioInput = document.getElementById('calendarioReservaFechaInicio');
            const fechaFinInput = document.getElementById('calendarioReservaFechaFin');
            
            if (fechaInicioInput && fechaFinInput) {
                fechaInicioInput.value = fechaInicioStr;
                fechaFinInput.value = fechaFinStr;
            } else {
                console.warn('⚠️ Inputs de fecha no encontrados');
            }
            
            // Poblar los selectores si no están poblados
            console.log('🔄 Poblando selectores del modal...');
            await this.poblarSelectoresCalendarioReserva();
            console.log('✅ Selectores poblados correctamente');
            
            // Verificar que los selectores estén poblados
            const clienteSelect = document.getElementById('calendarioReservaCliente');
            const servicioSelect = document.getElementById('calendarioReservaServicio');
            const recursoSelect = document.getElementById('calendarioReservaRecurso');
            
            // Configurar event listener para calcular fecha de fin automáticamente cuando cambie el servicio
            if (servicioSelect) {
                // Limpiar event listeners anteriores
                servicioSelect.removeEventListener('change', this._calcularFechaFinHandler);
                
                // Crear nuevo handler
                this._calcularFechaFinHandler = () => this.calcularFechaFinDesdeServicio();
                servicioSelect.addEventListener('change', this._calcularFechaFinHandler);
                
                console.log('✅ Event listener configurado para cálculo automático de fecha de fin');
                
                // EJECUTAR INMEDIATAMENTE si ya hay un servicio seleccionado
                if (servicioSelect.value !== '') {
                    console.log('🚀 Ejecutando cálculo inmediato para servicio ya seleccionado...');
                    setTimeout(() => this.calcularFechaFinDesdeServicio(), 100);
                }
            }
            
            console.log('🔍 Estado de los selectores después de poblar:', {
                cliente: clienteSelect ? clienteSelect.options.length : 'no encontrado',
                servicio: servicioSelect ? servicioSelect.options.length : 'no encontrado',
                recurso: recursoSelect ? recursoSelect.options.length : 'no encontrado'
            });
            
            // Mostrar el modal
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            
            // Configurar event listeners para las opciones de reserva múltiple
            this.configurarOpcionesReservaMultiple();
            
            console.log('✅ Modal de reserva del calendario abierto correctamente');
            console.log('🔍 Elementos del modal verificados:', {
                modal: !!modalElement,
                periodo: !!document.getElementById('periodoSeleccionado'),
                fechaInicio: !!document.getElementById('calendarioReservaFechaInicio'),
                fechaFin: !!document.getElementById('calendarioReservaFechaFin'),
                cliente: !!document.getElementById('calendarioReservaCliente'),
                servicio: !!document.getElementById('calendarioReservaServicio'),
                recurso: !!document.getElementById('calendarioReservaRecurso')
            });
            
        } catch (error) {
            console.error('❌ Error abriendo modal de reserva del calendario:', error);
            this.showAlert('Error al abrir el modal de reserva: ' + error.message, 'danger');
        }
    }

    /**
     * Calcula automáticamente la fecha de fin basándose en el servicio seleccionado
     */
    calcularFechaFinDesdeServicio() {
        try {
            console.log('🔄 Calculando fecha de fin desde servicio seleccionado...');
            
            const servicioSelect = document.getElementById('calendarioReservaServicio');
            const fechaInicioInput = document.getElementById('calendarioReservaFechaInicio');
            const fechaFinInput = document.getElementById('calendarioReservaFechaFin');
            
            if (!servicioSelect || !fechaInicioInput || !fechaFinInput) {
                console.warn('⚠️ Elementos necesarios no encontrados para calcular fecha de fin');
                return;
            }
            
            const selectedOption = servicioSelect.options[servicioSelect.selectedIndex];
            if (!selectedOption || selectedOption.value === '') {
                console.log('🔍 No hay servicio seleccionado');
                return;
            }
            
            console.log('🔍 Servicio seleccionado:', {
                text: selectedOption.text,
                value: selectedOption.value,
                dataDuracion: selectedOption.getAttribute('data-duracion')
            });
            
            const duracionMinutos = parseInt(selectedOption.getAttribute('data-duracion'));
            if (!duracionMinutos || isNaN(duracionMinutos)) {
                console.warn('⚠️ Duración del servicio no disponible:', selectedOption.getAttribute('data-duracion'));
                return;
            }
            
            const fechaInicioStr = fechaInicioInput.value;
            console.log('🔍 Fecha de inicio del input:', fechaInicioStr);
            
            const fechaInicio = new Date(fechaInicioStr);
            if (isNaN(fechaInicio.getTime())) {
                console.warn('⚠️ Fecha de inicio inválida:', fechaInicioStr);
                return;
            }
            
            console.log('🔍 Fecha de inicio parseada:', {
                original: fechaInicioStr,
                parsed: fechaInicio.toLocaleString('es-ES'),
                minutos: fechaInicio.getMinutes(),
                hora: fechaInicio.getHours()
            });
            
            // Calcular fecha de fin sumando la duración del servicio
            const fechaFin = new Date(fechaInicio);
            fechaFin.setMinutes(fechaInicio.getMinutes() + duracionMinutos);
            
            console.log('🔍 Cálculo de fecha de fin:', {
                fechaInicio: fechaInicio.toLocaleString('es-ES'),
                duracionMinutos: duracionMinutos,
                minutosInicio: fechaInicio.getMinutes(),
                minutosFinales: fechaInicio.getMinutes() + duracionMinutos,
                fechaFin: fechaFin.toLocaleString('es-ES')
            });
            
            // Formatear para el input datetime-local - SIN conversión UTC
            const fechaFinStr = fechaFin.getFullYear() + '-' + 
                               String(fechaFin.getMonth() + 1).padStart(2, '0') + '-' + 
                               String(fechaFin.getDate()).padStart(2, '0') + 'T' +
                               String(fechaFin.getHours()).padStart(2, '0') + ':' +
                               String(fechaFin.getMinutes()).padStart(2, '0');
            
            console.log('🔍 Conversión sin UTC:', {
                fechaFin_toISOString: fechaFin.toISOString().slice(0, 16),
                fechaFin_local: fechaFinStr
            });
            
            fechaFinInput.value = fechaFinStr;
            
            console.log('✅ Fecha de fin calculada automáticamente:', {
                servicio: selectedOption.text,
                duracion: duracionMinutos + ' minutos',
                fechaInicio: fechaInicio.toLocaleString('es-ES'),
                fechaFin: fechaFin.toLocaleString('es-ES'),
                fechaFinInput: fechaFinStr
            });
            
        } catch (error) {
            console.error('❌ Error calculando fecha de fin:', error);
        }
    }
    
    /**
     * Configura las opciones de reserva múltiple
     */
    configurarOpcionesReservaMultiple() {
        const reservaMultipleDias = document.getElementById('reservaMultipleDias');
        const reservaRecurrente = document.getElementById('reservaRecurrente');
        const reservaBloque = document.getElementById('reservaBloque');
        const configuracionMultiple = document.getElementById('configuracionMultiple');
        
        if (reservaMultipleDias) {
            reservaMultipleDias.addEventListener('change', (e) => {
                if (e.target.checked) {
                    configuracionMultiple.style.display = 'block';
                    // Deshabilitar otras opciones
                    reservaRecurrente.checked = false;
                    reservaBloque.checked = false;
                } else {
                    configuracionMultiple.style.display = 'none';
                }
            });
        }
        
        if (reservaRecurrente) {
            reservaRecurrente.addEventListener('change', (e) => {
                if (e.target.checked) {
                    configuracionMultiple.style.display = 'block';
                    // Deshabilitar otras opciones
                    reservaMultipleDias.checked = false;
                    reservaBloque.checked = false;
                } else {
                    configuracionMultiple.style.display = 'none';
                }
            });
        }
        
        if (reservaBloque) {
            reservaBloque.addEventListener('change', (e) => {
                if (e.target.checked) {
                    // Deshabilitar otras opciones
                    reservaMultipleDias.checked = false;
                    reservaRecurrente.checked = false;
                    configuracionMultiple.style.display = 'none';
                }
            });
        }
    }

    /**
     * Pobla los selectores del modal de reservas del calendario
     */
    async poblarSelectoresCalendarioReserva() {
        try {
            console.log('🚀 VERSIÓN ACTUALIZADA - Poblando selectores del calendario', new Date().toISOString());
            
            // Verificar si ya están poblados
            const clienteSelect = document.getElementById('calendarioReservaCliente');
            const servicioSelect = document.getElementById('calendarioReservaServicio');
            const recursoSelect = document.getElementById('calendarioReservaRecurso');
            
            if (!clienteSelect || !servicioSelect || !recursoSelect) {
                console.warn('⚠️ Algunos selectores del modal no se encontraron');
                return;
            }
            
            // Poblar selector de clientes
            if (clienteSelect.options.length <= 1) {
                await this.poblarSelectorClientesCalendario('calendarioReservaCliente');
            }
            
            // Poblar selector de servicios
            if (servicioSelect.options.length <= 1) {
                await this.poblarSelectorServiciosCalendario('calendarioReservaServicio');
            }
            
            // Poblar selector de recursos
            if (recursoSelect.options.length <= 1) {
                await this.poblarSelectorRecursosCalendario('calendarioReservaRecurso');
            }
            
        } catch (error) {
            console.error('❌ Error poblando selectores del modal de reservas:', error);
        }
    }
    
    /**
     * Pobla el selector de clientes para el modal del calendario
     */
    async poblarSelectorClientesCalendario(selectorId) {
        try {
            const clienteSelect = document.getElementById(selectorId);
            if (!clienteSelect) return;
            
            clienteSelect.innerHTML = '<option value="">Seleccionar cliente...</option>';
            const clientes = await this.apiCall('/clientes/');
            if (clientes) {
                clientes.forEach(cliente => {
                    clienteSelect.innerHTML += `
                        <option value="${cliente.id}">${cliente.nombre} - ${cliente.email}</option>`;
                });
                console.log('✅ Selector de clientes poblado:', clientes.length, 'clientes');
            }
        } catch (error) {
            console.error('❌ Error poblando selector de clientes:', error);
        }
    }
    
    /**
     * Pobla el selector de servicios para el modal del calendario
     */
    async poblarSelectorServiciosCalendario(selectorId) {
        try {
            const servicioSelect = document.getElementById(selectorId);
            if (!servicioSelect) return;
            
            servicioSelect.innerHTML = '<option value="">Seleccionar servicio...</option>';
            if (this.currentData && this.currentData.services) {
                this.currentData.services.forEach(service => {
                    servicioSelect.innerHTML += `
                        <option value="${service.id}" data-duracion="${service.duracion_minutos}">${service.nombre} - €${service.precio_base} (${service.duracion_minutos} min)</option>`;
                });
                console.log('✅ Selector de servicios poblado:', this.currentData.services.length, 'servicios');
            } else {
                console.warn('⚠️ No hay datos de servicios disponibles');
            }
        } catch (error) {
            console.error('❌ Error poblando selector de servicios:', error);
        }
    }
    
    /**
     * Pobla el selector de recursos para el modal del calendario
     */
    async poblarSelectorRecursosCalendario(selectorId) {
        try {
            const recursoSelect = document.getElementById(selectorId);
            if (!recursoSelect) return;
            
            recursoSelect.innerHTML = '<option value="">Seleccionar recurso...</option>';
            if (this.currentData && this.currentData.resources) {
                this.currentData.resources.forEach(resource => {
                    if (resource.disponible) {
                        recursoSelect.innerHTML += `
                            <option value="${resource.id}">${resource.nombre} (${resource.tipo})</option>`;
                    }
                });
                console.log('✅ Selector de recursos poblado:', this.currentData.resources.length, 'recursos');
            } else {
                console.warn('⚠️ No hay datos de recursos disponibles');
            }
        } catch (error) {
            console.error('❌ Error poblando selector de recursos:', error);
        }
    }

    /**
     * Crea una reserva desde el modal del calendario
     */
    async crearReservaDesdeCalendario() {
        try {
            console.log('🚀 VERSIÓN 2.1 - Creando reserva desde calendario (Variables corregidas)', new Date().toISOString());
            
            // Validar campos obligatorios
            const clienteId = document.getElementById('calendarioReservaCliente').value;
            const servicioId = document.getElementById('calendarioReservaServicio').value;
            const recursoId = document.getElementById('calendarioReservaRecurso').value;
            const fechaInicio = document.getElementById('calendarioReservaFechaInicio').value;
            const fechaFin = document.getElementById('calendarioReservaFechaFin').value;
            const estado = document.getElementById('calendarioReservaEstado').value;
            
            console.log('🔍 Valores del formulario:', { clienteId, servicioId, recursoId, fechaInicio, fechaFin, estado });
            
            if (!clienteId || !servicioId || !recursoId || !fechaInicio || !fechaFin) {
                this.showCalendarioReservaMessage('Por favor completa todos los campos obligatorios', 'warning');
                return;
            }
            
            // Validar que la fecha de fin sea posterior a la de inicio
            const fechaInicioObj = new Date(fechaInicio);
            const fechaFinObj = new Date(fechaFin);
            
            if (fechaFinObj <= fechaInicioObj) {
                this.showCalendarioReservaMessage('La fecha de fin debe ser posterior a la fecha de inicio', 'warning');
                return;
            }
            
            // Crear objeto formData con los valores del formulario
            const formData = {
                cliente_id: parseInt(clienteId),
                servicio_id: parseInt(servicioId),
                recurso_id: parseInt(recursoId),
                fecha_hora_inicio: fechaInicio,
                fecha_hora_fin: fechaFin,
                estado: estado,
                participantes: 1, // Por defecto
                notas: `Reserva creada desde calendario - ${new Date().toLocaleString()}`
            };
            
            console.log('📋 Datos del formulario preparados:', formData);
            console.log('🔍 Validaciones completadas - Procediendo a crear reserva...');
            
            // Verificar si es una reserva múltiple
            const reservaMultipleDias = document.getElementById('reservaMultipleDias').checked;
            const reservaRecurrente = document.getElementById('reservaRecurrente').checked;
            const reservaBloque = document.getElementById('reservaBloque').checked;
            
            console.log('🔍 Opciones seleccionadas:', { reservaMultipleDias, reservaRecurrente, reservaBloque });
            
            if (reservaMultipleDias || reservaRecurrente) {
                // Crear múltiples reservas
                await this.crearReservasMultiples(formData, reservaMultipleDias, reservaRecurrente);
            } else {
                // Crear reserva única
                await this.crearReservaUnica(formData);
            }
            
            // Cerrar el modal inmediatamente
            const modal = bootstrap.Modal.getInstance(document.getElementById('calendarioReservaModal'));
            if (modal) {
                modal.hide();
                // Forzar la eliminación del backdrop si existe
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
                // Restaurar el scroll del body
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
            
            // Limpiar el formulario
            document.getElementById('calendarioReservaForm').reset();
            
            // Actualizar el calendario
            await this.actualizarCalendario();
            
            // Mostrar mensaje de éxito
            this.showAlert('Reserva(s) creada(s) exitosamente desde el calendario', 'success');
            
        } catch (error) {
            console.error('❌ Error creando reserva desde calendario:', error);
            this.showCalendarioReservaMessage('Error al crear la reserva', 'danger');
        }
    }

    /**
     * Crea una reserva única
     */
    async crearReservaUnica(formData) {
        try {
            console.log('💾 Creando reserva única:', formData);
            console.log('🚀 Llamando a API /reservas/ con método POST...');
            
            const newReserva = await this.apiCall('/reservas/', 'POST', formData);
            
            console.log('✅ Respuesta de la API:', newReserva);
            
            if (newReserva) {
                this.showCalendarioReservaMessage('Reserva creada exitosamente', 'success');
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('❌ Error creando reserva única:', error);
            this.showCalendarioReservaMessage('Error al crear la reserva', 'danger');
            return false;
        }
    }

    /**
     * Crea múltiples reservas
     */
    async crearReservasMultiples(formData, esMultipleDias, esRecurrente) {
        try {
            console.log('💾 Creando reservas múltiples:', { formData, esMultipleDias, esRecurrente });
            
            let reservasCreadas = 0;
            let reservasFallidas = 0;
            
            if (esMultipleDias) {
                const diasAdicionales = parseInt(document.getElementById('diasAdicionales').value) || 1;
                const resultado = await this.crearReservasConsecutivas(formData, diasAdicionales);
                reservasCreadas += resultado.creadas;
                reservasFallidas += resultado.fallidas;
            }
            
            if (esRecurrente) {
                const tipoRecurrencia = document.getElementById('tipoRecurrencia').value;
                const resultado = await this.crearReservasRecurrentes(formData, tipoRecurrencia);
                reservasCreadas += resultado.creadas;
                reservasFallidas += resultado.fallidas;
            }
            
            // Mostrar resumen
            if (reservasFallidas === 0) {
                this.showCalendarioReservaMessage(`${reservasCreadas} reserva(s) creada(s) exitosamente`, 'success');
            } else {
                this.showCalendarioReservaMessage(`${reservasCreadas} reserva(s) creada(s), ${reservasFallidas} fallida(s)`, 'warning');
            }
            
        } catch (error) {
            console.error('❌ Error creando reservas múltiples:', error);
            this.showCalendarioReservaMessage('Error al crear las reservas múltiples', 'danger');
        }
    }

    /**
     * Crea reservas en días consecutivos
     */
    async crearReservasConsecutivas(formData, diasAdicionales) {
        let reservasCreadas = 0;
        let reservasFallidas = 0;
        
        for (let i = 0; i <= diasAdicionales; i++) {
            try {
                const fechaInicio = new Date(formData.fecha_hora_inicio);
                const fechaFin = new Date(formData.fecha_hora_fin);
                
                // Calcular duración en milisegundos
                const duracion = fechaFin - fechaInicio;
                
                // Crear nueva fecha para este día
                const nuevaFechaInicio = new Date(fechaInicio);
                nuevaFechaInicio.setDate(fechaInicio.getDate() + i);
                
                const nuevaFechaFin = new Date(nuevaFechaInicio);
                nuevaFechaFin.setTime(nuevaFechaInicio.getTime() + duracion);
                
                const nuevaReserva = {
                    ...formData,
                    fecha_hora_inicio: nuevaFechaInicio.toISOString(),
                    fecha_hora_fin: nuevaFechaFin.toISOString()
                };
                
                const resultado = await this.apiCall('/reservas/', 'POST', nuevaReserva);
                if (resultado) {
                    reservasCreadas++;
                } else {
                    reservasFallidas++;
                }
                
            } catch (error) {
                console.error(`❌ Error creando reserva para día ${i}:`, error);
                reservasFallidas++;
            }
        }
        
        return { creadas: reservasCreadas, fallidas: reservasFallidas };
    }

    /**
     * Crea reservas recurrentes
     */
    async crearReservasRecurrentes(formData, tipoRecurrencia) {
        let reservasCreadas = 0;
        let reservasFallidas = 0;
        
        // Crear 4 reservas recurrentes por defecto
        const numeroReservas = 4;
        
        for (let i = 1; i <= numeroReservas; i++) {
            try {
                const fechaInicio = new Date(formData.fecha_hora_inicio);
                const fechaFin = new Date(formData.fecha_hora_fin);
                
                // Calcular duración en milisegundos
                const duracion = fechaFin - fechaInicio;
                
                // Crear nueva fecha según el tipo de recurrencia
                const nuevaFechaInicio = new Date(fechaInicio);
                const nuevaFechaFin = new Date(fechaInicio);
                
                switch (tipoRecurrencia) {
                    case 'diaria':
                        nuevaFechaInicio.setDate(fechaInicio.getDate() + i);
                        nuevaFechaFin.setDate(fechaInicio.getDate() + i);
                        break;
                    case 'semanal':
                        nuevaFechaInicio.setDate(fechaInicio.getDate() + (i * 7));
                        nuevaFechaFin.setDate(fechaInicio.getDate() + (i * 7));
                        break;
                    case 'mensual':
                        nuevaFechaInicio.setMonth(fechaInicio.getMonth() + i);
                        nuevaFechaFin.setMonth(fechaInicio.getMonth() + i);
                        break;
                }
                
                nuevaFechaFin.setTime(nuevaFechaInicio.getTime() + duracion);
                
                const nuevaReserva = {
                    ...formData,
                    fecha_hora_inicio: nuevaFechaInicio.toISOString(),
                    fecha_hora_fin: nuevaFechaFin.toISOString()
                };
                
                const resultado = await this.apiCall('/reservas/', 'POST', nuevaReserva);
                if (resultado) {
                    reservasCreadas++;
                } else {
                    reservasFallidas++;
                }
                
            } catch (error) {
                console.error(`❌ Error creando reserva recurrente ${i}:`, error);
                reservasFallidas++;
            }
        }
        
        return { creadas: reservasCreadas, fallidas: reservasFallidas };
    }

    /**
     * Muestra mensajes en el modal de reservas del calendario
     */
    showCalendarioReservaMessage(message, type) {
        const messageArea = document.getElementById('calendarioReservaMessageArea');
        const messageElement = document.getElementById('calendarioReservaMessage');
        const messageText = document.getElementById('calendarioReservaMessageText');
        
        if (messageArea && messageElement && messageText) {
            messageElement.className = `alert alert-${type}`;
            messageText.textContent = message;
            messageArea.style.display = 'block';
            
            // Ocultar mensaje después de 5 segundos
            setTimeout(() => {
                messageArea.style.display = 'none';
            }, 5000);
        }
    }

    /**
     * Limpia los mensajes del modal de reservas del calendario
     */
    clearCalendarioReservaMessage() {
        const messageArea = document.getElementById('calendarioReservaMessageArea');
        if (messageArea) {
            messageArea.style.display = 'none';
        }
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PreciosDinamicosApp();
});

// Versión del archivo para forzar recarga del caché
console.log('📝 JavaScript cargado - Versión 3.0 (Sistema de Precios Integrado):', new Date().toISOString());

// ========================================
// SPRINT 5: GESTIÓN DE PAGOS E INTEGRACIONES
// ========================================

// Variables globales para Sprint 5
let pagosData = [];
let integracionesData = [];
let notificacionesData = [];
let webhooksData = [];
let googleCalendarData = [];

// ========================================
// FUNCIONES DE GESTIÓN DE PAGOS
// ========================================

/**
 * Cargar todos los pagos del sistema
 */
async function cargarPagos() {
    try {
        showLoading('pagosContainer');
        
        const response = await fetch('/api/pagos/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const pagos = await response.json();
        pagosData = pagos;
        displayPagosList(pagos);
        
    } catch (error) {
        console.error('❌ Error cargando pagos:', error);
        showError('pagosContainer', 'Error al cargar los pagos');
    }
}

/**
 * Mostrar lista de pagos en el contenedor
 */
function displayPagosList(pagos) {
    const container = document.getElementById('pagosContainer');
    
    if (!pagos || pagos.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-credit-card fa-3x mb-3"></i>
                <h5>No hay pagos registrados</h5>
                <p>Comienza creando tu primer pago</p>
            </div>
        `;
        return;
    }
    
    const pagosHTML = pagos.map(pago => `
        <div class="card mb-3 payment-card" data-pago-id="${pago.id}">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-2">
                        <div class="payment-status-badge ${getPaymentStatusClass(pago.estado)}">
                            <i class="fas ${getPaymentStatusIcon(pago.estado)} me-2"></i>
                            ${pago.estado}
                        </div>
                    </div>
                    <div class="col-md-3">
                        <h6 class="mb-1">Pago #${pago.id}</h6>
                        <small class="text-muted">
                            <i class="fas fa-calendar me-1"></i>
                            ${formatDate(pago.fecha_creacion)}
                        </small>
                    </div>
                    <div class="col-md-2">
                        <strong class="text-primary">${pago.monto} ${pago.moneda}</strong>
                    </div>
                    <div class="col-md-2">
                        <span class="badge bg-secondary">
                            <i class="fas fa-credit-card me-1"></i>
                            ${pago.metodo_pago}
                        </span>
                    </div>
                    <div class="col-md-3 text-end">
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="verDetallePago(${pago.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success me-1" onclick="generarFactura(${pago.id})">
                            <i class="fas fa-file-invoice"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" onclick="solicitarReembolso(${pago.id})">
                            <i class="fas fa-undo"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = pagosHTML;
}

/**
 * Obtener clase CSS para el estado del pago
 */
function getPaymentStatusClass(estado) {
    const statusClasses = {
        'pendiente': 'bg-warning',
        'procesando': 'bg-info',
        'completado': 'bg-success',
        'fallido': 'bg-danger',
        'cancelado': 'bg-secondary',
        'reembolsado': 'bg-warning'
    };
    return statusClasses[estado] || 'bg-secondary';
}

/**
 * Obtener icono para el estado del pago
 */
function getPaymentStatusIcon(estado) {
    const statusIcons = {
        'pendiente': 'fa-clock',
        'procesando': 'fa-spinner',
        'completado': 'fa-check-circle',
        'fallido': 'fa-times-circle',
        'cancelado': 'fa-ban',
        'reembolsado': 'fa-undo'
    };
    return statusIcons[estado] || 'fa-question-circle';
}

/**
 * Crear nuevo pago
 */
async function crearNuevoPago() {
    try {
        const formData = {
            reserva_id: parseInt(document.getElementById('nuevoPagoReserva').value),
            cliente_id: parseInt(document.getElementById('nuevoPagoCliente').value),
            monto: parseFloat(document.getElementById('nuevoPagoMonto').value),
            moneda: document.getElementById('nuevoPagoMoneda').value,
            metodo_pago: document.getElementById('nuevoPagoMetodo').value,
            descripcion: document.getElementById('nuevoPagoDescripcion').value
        };
        
        const response = await fetch('/api/pagos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al crear el pago');
        }
        
        const nuevoPago = await response.json();
        console.log('✅ Pago creado exitosamente:', nuevoPago);
        
        // Cerrar modal y recargar lista
        cerrarTodosLosModales();
        cargarPagos();
        
        // Mostrar mensaje de éxito
        showSuccess('Pago creado exitosamente');
        
    } catch (error) {
        console.error('❌ Error creando pago:', error);
        showError('Error al crear el pago: ' + error.message);
    }
}

/**
 * Cargar resumen de pagos
 */
async function cargarResumenPagos() {
    try {
        const response = await fetch('/api/pagos/resumen/general');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const resumen = await response.json();
        mostrarResumenPagos(resumen);
        
    } catch (error) {
        console.error('❌ Error cargando resumen de pagos:', error);
        showError('Error al cargar el resumen de pagos');
    }
}

/**
 * Mostrar resumen de pagos en un modal
 */
function mostrarResumenPagos(resumen) {
    // Crear modal dinámico para mostrar el resumen
    const modalHTML = `
        <div class="modal fade" id="resumenPagosModal" tabindex="-1">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-chart-bar me-2"></i>Resumen de Pagos
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card text-center mb-3">
                                    <div class="card-body">
                                        <h3 class="text-success">${resumen.total_pagos || 0}</h3>
                                        <p class="mb-0">Total de Pagos</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card text-center mb-3">
                                    <div class="card-body">
                                        <h3 class="text-primary">${resumen.monto_total || 0}€</h3>
                                        <p class="mb-0">Monto Total</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-12">
                                <h6>Estados de Pagos:</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>Estado</th>
                                                <th>Cantidad</th>
                                                <th>Monto</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${Object.entries(resumen.estados || {}).map(([estado, data]) => `
                                                <tr>
                                                    <td>
                                                        <span class="badge ${getPaymentStatusClass(estado)}">${estado}</span>
                                                    </td>
                                                    <td>${data.cantidad || 0}</td>
                                                    <td>${data.monto || 0}€</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Agregar modal al DOM y mostrarlo
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('resumenPagosModal'));
    modal.show();
    
    // Limpiar modal del DOM cuando se cierre
    document.getElementById('resumenPagosModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// ========================================
// FUNCIONES DE GESTIÓN DE INTEGRACIONES
// ========================================

/**
 * Cargar todas las integraciones del sistema
 */
async function cargarIntegraciones() {
    try {
        showLoading('integracionesContainer');
        
        const response = await fetch('/api/integraciones/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const integraciones = await response.json();
        integracionesData = integraciones;
        displayIntegracionesList(integraciones);
        
    } catch (error) {
        console.error('❌ Error cargando integraciones:', error);
        showError('integracionesContainer', 'Error al cargar las integraciones');
    }
}

/**
 * Mostrar lista de integraciones
 */
function displayIntegracionesList(integraciones) {
    const container = document.getElementById('integracionesContainer');
    
    if (!integraciones || integraciones.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-plug fa-3x mb-3"></i>
                <h5>No hay integraciones configuradas</h5>
                <p>Comienza configurando tu primera integración</p>
            </div>
            `;
        return;
    }
    
    const integracionesHTML = integraciones.map(integracion => `
        <div class="card mb-3 integration-card" data-integracion-id="${integracion.id}">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-2">
                        <div class="integration-type-badge">
                            <i class="fas ${getIntegrationTypeIcon(integracion.tipo)} me-2"></i>
                            ${integracion.tipo}
                        </div>
                    </div>
                    <div class="col-md-3">
                        <h6 class="mb-1">${integracion.nombre}</h6>
                        <small class="text-muted">${integracion.descripcion || 'Sin descripción'}</small>
                    </div>
                    <div class="col-md-2">
                        <span class="badge ${getIntegrationStatusClass(integracion.estado)}">
                            ${integracion.estado}
                        </span>
                    </div>
                    <div class="col-md-2">
                        <small class="text-muted">
                            <i class="fas fa-calendar me-1"></i>
                            ${formatDate(integracion.created_at)}
                        </small>
                    </div>
                    <div class="col-md-3 text-end">
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editarIntegracion(${integracion.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info me-1" onclick="probarIntegracion(${integracion.id})">
                            <i class="fas fa-play"></i>
                            </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="eliminarIntegracion(${integracion.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = integracionesHTML;
}

/**
 * Obtener icono para el tipo de integración
 */
function getIntegrationTypeIcon(tipo) {
    const typeIcons = {
        'email': 'fa-envelope',
        'sms': 'fa-sms',
        'whatsapp': 'fa-whatsapp',
        'google_calendar': 'fa-calendar',
        'stripe': 'fa-credit-card',
        'paypal': 'fa-paypal'
    };
    return typeIcons[tipo] || 'fa-plug';
}

/**
 * Obtener clase CSS para el estado de la integración
 */
function getIntegrationStatusClass(estado) {
    const statusClasses = {
        'activa': 'bg-success',
        'inactiva': 'bg-secondary',
        'error': 'bg-danger',
        'configurando': 'bg-warning'
    };
    return statusClasses[estado] || 'bg-secondary';
}

/**
 * Crear nueva integración
 */
async function crearNuevaIntegracion() {
    try {
        const formData = {
            nombre: document.getElementById('nuevaIntegracionNombre').value,
            tipo: document.getElementById('nuevaIntegracionTipo').value,
            estado: document.getElementById('nuevaIntegracionEstado').value,
            descripcion: document.getElementById('nuevaIntegracionDescripcion').value,
            webhook_url: document.getElementById('nuevaIntegracionWebhook').value,
            configuracion: document.getElementById('nuevaIntegracionConfig').value
        };
        
        const response = await fetch('/api/integraciones/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al crear la integración');
        }
        
        const nuevaIntegracion = await response.json();
        console.log('✅ Integración creada exitosamente:', nuevaIntegracion);
        
        // Cerrar modal y recargar lista
        cerrarTodosLosModales();
        cargarIntegraciones();
        
        // Mostrar mensaje de éxito
        showSuccess('Integración creada exitosamente');
        
    } catch (error) {
        console.error('❌ Error creando integración:', error);
        showError('Error al crear la integración: ' + error.message);
    }
}

/**
 * Cargar estado de las integraciones
 */
async function cargarEstadoIntegraciones() {
    try {
        const response = await fetch('/api/integraciones/estado/general');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const estado = await response.json();
        mostrarEstadoIntegraciones(estado);
        
    } catch (error) {
        console.error('❌ Error cargando estado de integraciones:', error);
        showError('Error al cargar el estado de las integraciones');
    }
}

/**
 * Mostrar estado de las integraciones
 */
function mostrarEstadoIntegraciones(estado) {
    showSuccess(`Estado de integraciones: ${estado.total_integraciones} total, ${estado.integraciones_activas} activas`);
}

/**
 * Procesar notificaciones pendientes
 */
async function procesarNotificacionesPendientes() {
    try {
        const response = await fetch('/api/integraciones/notificaciones/procesar-pendientes', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const resultado = await response.json();
        showSuccess(resultado.mensaje);
        
        // Recargar notificaciones si estamos en esa tab
        if (document.getElementById('notificacionesList').classList.contains('show')) {
            cargarNotificaciones();
        }
        
    } catch (error) {
        console.error('❌ Error procesando notificaciones:', error);
        showError('Error al procesar las notificaciones pendientes');
    }
}

// ========================================
// FUNCIONES AUXILIARES
// ========================================

/**
 * Mostrar estado de carga
 */
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p>Cargando...</p>
            </div>
        `;
    }
}

/**
 * Mostrar error
 */
function showError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }
}

/**
 * Mostrar mensaje de éxito
 */
function showSuccess(message) {
    // Crear toast de éxito
    const toastHTML = `
        <div class="toast align-items-center text-white bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // Agregar toast al DOM y mostrarlo
    document.body.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.querySelector('.toast:last-child');
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Limpiar toast del DOM cuando se oculte
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

/**
 * Formatear fecha
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ========================================
// INICIALIZACIÓN DE SPRINT 5
// ========================================

/**
 * Inicializar funcionalidades de Sprint 5
 */
function initSprint5() {
    console.log('🚀 Inicializando Sprint 5: Integraciones y Pagos...');
    
    // Cargar datos iniciales cuando se active la tab correspondiente
    document.getElementById('pagos-tab').addEventListener('click', function() {
        if (pagosData.length === 0) {
            cargarPagos();
        }
    });
    
    document.getElementById('integraciones-tab').addEventListener('click', function() {
        if (integracionesData.length === 0) {
            cargarIntegraciones();
        }
    });
    
    // Configurar filtros de pagos
    document.getElementById('filtroEstadoPago').addEventListener('change', filtrarPagos);
    document.getElementById('filtroMetodoPago').addEventListener('change', filtrarPagos);
    document.getElementById('filtroFechaDesde').addEventListener('change', filtrarPagos);
    document.getElementById('filtroFechaHasta').addEventListener('change', filtrarPagos);
    
    // Configurar cálculo automático de total en factura
    document.getElementById('nuevaFacturaIVA').addEventListener('input', calcularTotalFactura);
    document.getElementById('nuevaFacturaSubtotal').addEventListener('input', calcularTotalFactura);
    
    console.log('✅ Sprint 5 inicializado correctamente');
}

/**
 * Filtrar pagos según los criterios seleccionados
 */
function filtrarPagos() {
    const estado = document.getElementById('filtroEstadoPago').value;
    const metodo = document.getElementById('filtroMetodoPago').value;
    const fechaDesde = document.getElementById('filtroFechaDesde').value;
    const fechaHasta = document.getElementById('filtroFechaHasta').value;
    
    let pagosFiltrados = pagosData;
    
    if (estado) {
        pagosFiltrados = pagosFiltrados.filter(pago => pago.estado === estado);
    }
    
    if (metodo) {
        pagosFiltrados = pagosFiltrados.filter(pago => pago.metodo_pago === metodo);
    }
    
    if (fechaDesde) {
        pagosFiltrados = pagosFiltrados.filter(pago => 
            new Date(pago.fecha_creacion) >= new Date(fechaDesde)
        );
    }
    
    if (fechaHasta) {
        pagosFiltrados = pagosFiltrados.filter(pago => 
            new Date(pago.fecha_creacion) <= new Date(fechaHasta)
        );
    }
    
    displayPagosList(pagosFiltrados);
}

/**
 * Calcular total de factura automáticamente
 */
function calcularTotalFactura() {
    const subtotal = parseFloat(document.getElementById('nuevaFacturaSubtotal').value) || 0;
    const iva = parseFloat(document.getElementById('nuevaFacturaIVA').value) || 0;
    
    const total = subtotal * (1 + iva / 100);
    document.getElementById('nuevaFacturaTotal').value = total.toFixed(2);
}

// Inicializar Sprint 5 cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Esperar a que se inicialice la aplicación principal
    setTimeout(initSprint5, 1000);
});
