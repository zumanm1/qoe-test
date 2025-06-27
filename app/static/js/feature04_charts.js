document.addEventListener('DOMContentLoaded', function() {
    let radarChart, domainImpactChart;

    const commonOptions = {
        plugins: {
            legend: {
                display: false
            }
        },
        maintainAspectRatio: false,
    };

    // --- 1. CHART INITIALIZATION ---

    // Performance Radar Chart
    const radarCtx = document.getElementById('performanceRadarChart');
    if (radarCtx) {
        radarChart = new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: ['Throughput', 'Reliability', 'Latency', 'Jitter', 'Integrity'],
                datasets: [{
                    label: 'Network Performance',
                    data: [85, 92, 78, 88, 95], // Initial data
                    backgroundColor: 'rgba(138, 43, 226, 0.2)',
                    borderColor: 'rgba(138, 43, 226, 1)',
                    pointBackgroundColor: 'rgba(138, 43, 226, 1)',
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.2)' },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' },
                        pointLabels: { color: '#fff', font: { size: 12 } },
                        ticks: {
                            color: '#000',
                            backdropColor: 'rgba(255, 255, 255, 0.8)',
                            stepSize: 20
                        },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }

    // Domain Impact Analysis Chart
    const barCtx = document.getElementById('domainImpactChart');
    if (barCtx) {
        domainImpactChart = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: ['Radio Access', 'Transport', 'Core', 'Packet Core', 'Application'],
                datasets: [{
                    label: 'Impact on QoE',
                    data: [25, 68, 80, 41, 53], // Initial data
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(153, 102, 255, 0.6)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                ...commonOptions,
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#fff' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#fff' }
                    }
                }
            }
        });
    }

    // Performance Trends Chart (static for now)
    const trendsCtx = document.getElementById('performanceTrendsChart');
    if (trendsCtx) {
        new Chart(trendsCtx, {
            type: 'scatter',
            data: {
                datasets: [
                    { label: 'QoE Score', data: [{x: 1, y: 56}], backgroundColor: 'rgb(0, 255, 127)' },
                    { label: 'Download (Mbps)', data: [{x: 2, y: 90}], backgroundColor: 'rgb(54, 162, 235)' },
                    { label: 'Latency (ms)', data: [{x: 3, y: 32}], backgroundColor: 'rgb(255, 99, 132)' }
                ]
            },
            options: {
                ...commonOptions,
                scales: {
                    x: { display: false },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#fff' }
                    }
                }
            }
        });
    }

    // --- 2. INTERACTIVE LOGIC ---

    function getDashboardState() {
        const state = {};
        const controls = document.querySelectorAll('.form-range, .form-select, .form-check-input');
        controls.forEach(control => {
            if (control.type === 'checkbox') {
                state[control.id] = control.checked;
            } else {
                state[control.id] = control.value;
            }
        });
        return state;
    }

    async function updateDashboard() {
        const state = getDashboardState();
        try {
            const response = await fetch('/feature04/api/qoe_impact/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(state)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // Update UI elements
            document.getElementById('qoeScoreValue').textContent = data.qoe_score;
            document.getElementById('downloadSpeed').textContent = `${data.kpis.download_speed} Mbps`;
            document.getElementById('uploadSpeed').textContent = `${data.kpis.upload_speed} Mbps`;
            document.getElementById('latencyValue').textContent = `${data.kpis.latency} ms`;
            document.getElementById('jitterValue').textContent = `${data.kpis.jitter} ms`;
            document.getElementById('packetLossValue').textContent = `${data.kpis.packet_loss} %`;

            // Update charts
            if (radarChart) {
                radarChart.data.datasets[0].data = data.radar_data;
                radarChart.update();
            }
            if (domainImpactChart) {
                domainImpactChart.data.datasets[0].data = data.domain_impact_data;
                domainImpactChart.update();
            }
            
        } catch (error) {
            console.error("Could not update dashboard:", error);
        }
    }

    // --- 3. EVENT LISTENERS ---

    // Update slider labels in real-time
    const sliders = document.querySelectorAll('input[type="range"].form-range');
    sliders.forEach(slider => {
        const label = slider.previousElementSibling;
        if (label && label.htmlFor === slider.id) {
            const originalText = label.textContent.split(':')[0];
            const updateLabel = () => { label.textContent = `${originalText}: ${slider.value}`; };
            updateLabel(); // Set initial value
            slider.addEventListener('input', updateLabel);
        }
    });

    // Add event listeners to all controls to trigger a full dashboard update
    const allControls = document.querySelectorAll('.form-range, .form-select, .form-check-input');
    allControls.forEach(control => {
        control.addEventListener('input', updateDashboard);
    });
});
