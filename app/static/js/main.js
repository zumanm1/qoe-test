/**
 * Mobile Network QoE Web Application
 * Main JavaScript functionality
 */

// Global socket instance
let socket;

// Initialize Socket.IO connection
function initializeSocket() {
    if (typeof io !== 'undefined') {
        socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to server');
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
        });
        
        socket.on('kpi_update', function(data) {
            console.log('KPI update received:', data);
            updateDashboardData(data);
        });
        
        socket.on('alert', function(data) {
            console.log('Alert received:', data);
            showNotification(data.message, data.severity);
        });
    }
}

// Show browser notification
function showNotification(message, severity = 'info') {
    // Map severity to Bootstrap alert classes
    const severityMap = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'info',
        'info': 'info'
    };
    const alertClass = severityMap[severity] || 'info';
    
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${alertClass} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to notification area if it exists
    const notificationArea = document.getElementById('notification-area');
    if (notificationArea) {
        notificationArea.appendChild(alertDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => {
                alertDiv.remove();
            }, 150);
        }, 5000);
    }
}

// Update dashboard with new data
function updateDashboardData(data) {
    // This would be implemented for specific dashboard elements
}

// QoE Simulation functionality
const qoeSimulation = {
    // Current parameter values
    params: {},
    
    // Default parameter values
    defaultParams: {
        download_speed: 10.0,
        upload_speed: 5.0,
        latency: 50.0,
        packet_loss: 1.0,
        jitter: 10.0,
        bandwidth_utilization: 60.0,
        connection_stability: 90.0,
        signal_strength: -65.0,
        frequency_band: 2100,
        tower_distance: 1.0
    },
    
    // Initialize sliders and form controls
    initializeControls: function() {
        const sliders = document.querySelectorAll('.param-slider');
        if (sliders.length === 0) return;
        
        // Initialize all sliders
        sliders.forEach(slider => {
            const paramName = slider.dataset.param;
            const valueDisplay = document.getElementById(`${paramName}-value`);
            const initialValue = parseFloat(slider.value);
            
            // Store initial value
            this.params[paramName] = initialValue;
            
            // Update display on change
            slider.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value);
                this.params[paramName] = value;
                
                if (valueDisplay) {
                    // Add units if specified
                    const unit = slider.dataset.unit || '';
                    valueDisplay.textContent = value + unit;
                }
                
                // Calculate QoE if auto-calculate is enabled
                if (document.getElementById('auto-calculate').checked) {
                    this.calculateQoE();
                }
            });
        });
        
        // Set up calculate button
        const calculateBtn = document.getElementById('calculate-qoe-btn');
        if (calculateBtn) {
            calculateBtn.addEventListener('click', () => this.calculateQoE());
        }
        
        // Set up reset button
        const resetBtn = document.getElementById('reset-params-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetParams());
        }
        
        // Set up save scenario button
        const saveBtn = document.getElementById('save-scenario-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveScenario());
        }
    },
    
    // Calculate QoE based on current parameters
    calculateQoE: function() {
        // Show loading state
        const qoeDisplay = document.getElementById('qoe-score');
        if (qoeDisplay) {
            qoeDisplay.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
        }
        
        // Make API call to calculate QoE
        fetch('/simulation/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.params)
        })
        .then(response => response.json())
        .then(data => {
            this.displayResults(data);
        })
        .catch(error => {
            console.error('Error calculating QoE:', error);
            showNotification('Error calculating QoE. Please try again.', 'high');
        });
    },
    
    // Display QoE calculation results
    displayResults: function(data) {
        // Update QoE score
        const qoeDisplay = document.getElementById('qoe-score');
        if (qoeDisplay && data.qoe_score !== undefined) {
            qoeDisplay.textContent = Math.round(data.qoe_score);
            
            // Update gauge
            const gauge = document.getElementById('qoe-gauge-fill');
            if (gauge) {
                gauge.style.background = `conic-gradient(var(--mobile-blue) ${data.qoe_score}%, transparent 0%)`;
            }
            
            // Update score color
            if (data.qoe_score >= 80) {
                qoeDisplay.className = 'qoe-score-display text-success';
            } else if (data.qoe_score >= 60) {
                qoeDisplay.className = 'qoe-score-display text-warning';
            } else {
                qoeDisplay.className = 'qoe-score-display text-danger';
            }
        }
        
        // Update domain impacts
        if (data.domain_impacts) {
            Object.keys(data.domain_impacts).forEach(domain => {
                const impact = data.domain_impacts[domain];
                const domainElement = document.getElementById(`${domain}-impact`);
                if (domainElement) {
                    domainElement.textContent = Math.round(impact);
                    const progressBar = document.getElementById(`${domain}-progress`);
                    if (progressBar) {
                        progressBar.style.width = `${impact}%`;
                        
                        // Update progress bar color
                        progressBar.className = 'progress-bar';
                        if (impact >= 80) {
                            progressBar.classList.add('bg-success');
                        } else if (impact >= 60) {
                            progressBar.classList.add('bg-warning');
                        } else {
                            progressBar.classList.add('bg-danger');
                        }
                    }
                }
            });
        }
        
        // Update performance metrics
        if (data.metrics) {
            Object.keys(data.metrics).forEach(metric => {
                const value = data.metrics[metric];
                const metricElement = document.getElementById(`metric-${metric}`);
                if (metricElement) {
                    metricElement.textContent = value;
                }
            });
        }
        
        // Update recommendations
        const recommendationsContainer = document.getElementById('recommendations-container');
        if (recommendationsContainer && data.recommendations) {
            recommendationsContainer.innerHTML = '';
            
            if (data.recommendations.length === 0) {
                recommendationsContainer.innerHTML = '<div class="alert alert-info">No optimization recommendations at this time.</div>';
            } else {
                data.recommendations.forEach(rec => {
                    const recHtml = `
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title">${rec.title}</h5>
                                <p class="card-text">${rec.description}</p>
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="badge bg-primary">${rec.domain}</span>
                                    <span>Expected improvement: +${rec.impact_score}%</span>
                                </div>
                            </div>
                        </div>
                    `;
                    recommendationsContainer.innerHTML += recHtml;
                });
            }
        }
        
        // Show results section if hidden
        const resultsSection = document.getElementById('results-section');
        if (resultsSection && resultsSection.classList.contains('d-none')) {
            resultsSection.classList.remove('d-none');
        }
    },
    
    // Reset parameters to defaults
    resetParams: function() {
        const sliders = document.querySelectorAll('.param-slider');
        
        sliders.forEach(slider => {
            const paramName = slider.dataset.param;
            const defaultValue = this.defaultParams[paramName] || 0;
            
            // Reset slider value
            slider.value = defaultValue;
            this.params[paramName] = defaultValue;
            
            // Update display
            const valueDisplay = document.getElementById(`${paramName}-value`);
            if (valueDisplay) {
                const unit = slider.dataset.unit || '';
                valueDisplay.textContent = defaultValue + unit;
            }
        });
        
        // Calculate with new defaults if auto-calculate is on
        if (document.getElementById('auto-calculate').checked) {
            this.calculateQoE();
        }
    },
    
    // Save current scenario
    saveScenario: function() {
        const nameInput = document.getElementById('scenario-name');
        const descInput = document.getElementById('scenario-description');
        
        if (!nameInput || !nameInput.value.trim()) {
            showNotification('Please enter a scenario name', 'warning');
            return;
        }
        
        // Get QoE score if available
        const qoeDisplay = document.getElementById('qoe-score');
        const qoeScore = qoeDisplay ? parseFloat(qoeDisplay.textContent) : null;
        
        // Prepare data
        const scenarioData = {
            name: nameInput.value.trim(),
            description: descInput ? descInput.value.trim() : '',
            parameters: this.params,
            test_results: {
                qoe_score: qoeScore,
                download_speed: this.params.download_speed,
                upload_speed: this.params.upload_speed,
                latency: this.params.latency,
                jitter: this.params.jitter,
                packet_loss: this.params.packet_loss
            }
        };
        
        // Make API call to save scenario
        fetch('/simulation/api/scenarios', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(scenarioData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'info');
                
                // Optionally reload scenarios list
                this.loadSavedScenarios();
            } else {
                showNotification(data.error || 'Failed to save scenario', 'high');
            }
        })
        .catch(error => {
            console.error('Error saving scenario:', error);
            showNotification('Error saving scenario. Please try again.', 'high');
        });
    },
    
    // Load saved scenarios
    loadSavedScenarios: function() {
        const scenariosContainer = document.getElementById('saved-scenarios');
        if (!scenariosContainer) return;
        
        // Show loading indicator
        scenariosContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
        
        // Fetch scenarios
        fetch('/simulation/api/scenarios')
            .then(response => response.json())
            .then(data => {
                scenariosContainer.innerHTML = '';
                
                if (data.length === 0) {
                    scenariosContainer.innerHTML = '<div class="alert alert-info">No saved scenarios yet.</div>';
                    return;
                }
                
                // Create scenario items
                data.forEach(scenario => {
                    const scenarioItem = document.createElement('div');
                    scenarioItem.className = 'list-group-item list-group-item-action';
                    scenarioItem.innerHTML = `
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">${scenario.name}</h5>
                            <small>${new Date(scenario.created_at).toLocaleDateString()}</small>
                        </div>
                        <p class="mb-1">${scenario.description || 'No description'}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small>
                                ${scenario.is_baseline ? '<span class="badge bg-primary">Baseline</span>' : ''}
                            </small>
                            <div>
                                <button class="btn btn-sm btn-outline-primary load-scenario-btn" data-id="${scenario.id}">Load</button>
                                <a href="/simulation/scenarios/${scenario.id}" class="btn btn-sm btn-outline-secondary">View</a>
                            </div>
                        </div>
                    `;
                    scenariosContainer.appendChild(scenarioItem);
                    
                    // Add event listener to load button
                    const loadBtn = scenarioItem.querySelector('.load-scenario-btn');
                    loadBtn.addEventListener('click', () => this.loadScenario(scenario.id));
                });
            })
            .catch(error => {
                console.error('Error loading scenarios:', error);
                scenariosContainer.innerHTML = '<div class="alert alert-danger">Failed to load scenarios.</div>';
            });
    },
    
    // Load a specific scenario
    loadScenario: function(scenarioId) {
        fetch(`/simulation/api/scenarios/${scenarioId}`)
            .then(response => response.json())
            .then(data => {
                const parameters = data.parameters;
                
                // Update sliders with scenario parameters
                Object.keys(parameters).forEach(param => {
                    const slider = document.querySelector(`.param-slider[data-param="${param}"]`);
                    if (slider) {
                        slider.value = parameters[param];
                        this.params[param] = parameters[param];
                        
                        // Update display
                        const valueDisplay = document.getElementById(`${param}-value`);
                        if (valueDisplay) {
                            const unit = slider.dataset.unit || '';
                            valueDisplay.textContent = parameters[param] + unit;
                        }
                    }
                });
                
                // Calculate QoE with loaded parameters
                this.calculateQoE();
                
                // Update name field
                const nameInput = document.getElementById('scenario-name');
                if (nameInput) {
                    nameInput.value = `Copy of ${data.name}`;
                }
                
                // Update description field
                const descInput = document.getElementById('scenario-description');
                if (descInput) {
                    descInput.value = data.description;
                }
                
                showNotification(`Scenario "${data.name}" loaded successfully`, 'info');
            })
            .catch(error => {
                console.error('Error loading scenario:', error);
                showNotification('Error loading scenario. Please try again.', 'high');
            });
    }
};

// Document ready equivalent
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO
    initializeSocket();
    
    // Initialize QoE simulation if on simulation page
    if (document.getElementById('qoe-simulation-form')) {
        qoeSimulation.initializeControls();
        qoeSimulation.loadSavedScenarios();
    }
});
