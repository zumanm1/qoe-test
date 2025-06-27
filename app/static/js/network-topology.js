/**
 * Mobile Network QoE Tool - Network Topology Visualization
 * Uses D3.js for interactive network visualization
 */

class NetworkTopologyVisualization {
    constructor(containerId) {
        this.containerId = containerId;
        this.width = document.getElementById(containerId).clientWidth;
        this.height = 600;
        this.simulation = null;
        this.svg = null;
        this.link = null;
        this.node = null;
        this.nodeTypes = {
            'cell_tower': { color: '#3498db', icon: 'fa-broadcast-tower' },
            'router': { color: '#2ecc71', icon: 'fa-router' },
            'switch': { color: '#e67e22', icon: 'fa-network-wired' },
            'server': { color: '#9b59b6', icon: 'fa-server' },
            'gateway': { color: '#f1c40f', icon: 'fa-door-open' }
        };
        this.domainColors = {
            'ran': '#3498db',
            'transport': '#2ecc71',
            'core': '#9b59b6',
            'internet': '#e67e22'
        };
    }

    // Initialize the visualization
    init() {
        // Create SVG container
        this.svg = d3.select(`#${this.containerId}`)
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('class', 'network-topology-svg');

        // Add zoom functionality
        const zoom = d3.zoom()
            .scaleExtent([0.5, 5])
            .on('zoom', (event) => {
                this.svg.select('g').attr('transform', event.transform);
            });

        this.svg.call(zoom);

        // Create container for all elements
        const container = this.svg.append('g');

        // Add legend
        this.createLegend();
    }

    // Create a legend for the visualization
    createLegend() {
        const legend = this.svg.append('g')
            .attr('class', 'legend')
            .attr('transform', 'translate(20, 20)');

        // Domain colors
        const domains = Object.keys(this.domainColors);
        domains.forEach((domain, i) => {
            const g = legend.append('g')
                .attr('transform', `translate(0, ${i * 20})`);

            g.append('rect')
                .attr('width', 10)
                .attr('height', 10)
                .attr('fill', this.domainColors[domain]);

            g.append('text')
                .attr('x', 15)
                .attr('y', 10)
                .text(domain.toUpperCase())
                .attr('font-size', '12px');
        });

        // Node types
        const nodeTypes = Object.keys(this.nodeTypes);
        nodeTypes.forEach((type, i) => {
            const g = legend.append('g')
                .attr('transform', `translate(100, ${i * 20})`);

            g.append('circle')
                .attr('r', 5)
                .attr('fill', this.nodeTypes[type].color);

            g.append('text')
                .attr('x', 10)
                .attr('y', 5)
                .text(type.replace('_', ' '))
                .attr('font-size', '12px');
        });
    }

    // Load network data from API
    loadData() {
        // In a real implementation, this would fetch from an API
        fetch('/api/network/topology')
            .then(response => response.json())
            .then(data => {
                this.renderNetwork(data);
            })
            .catch(error => {
                console.error('Error loading network data:', error);
                this.loadMockData(); // Fallback to mock data
            });
    }

    // Load mock data for demonstration
    loadMockData() {
        const mockData = {
            nodes: [
                { id: 'ct1', name: 'Cell Tower A1', type: 'cell_tower', domain: 'ran', status: 'healthy' },
                { id: 'ct2', name: 'Cell Tower A2', type: 'cell_tower', domain: 'ran', status: 'warning' },
                { id: 'ct3', name: 'Cell Tower B1', type: 'cell_tower', domain: 'ran', status: 'critical' },
                { id: 'r1', name: 'Edge Router 1', type: 'router', domain: 'transport', status: 'healthy' },
                { id: 'r2', name: 'Core Router 1', type: 'router', domain: 'core', status: 'healthy' },
                { id: 'sw1', name: 'Switch 1', type: 'switch', domain: 'transport', status: 'healthy' },
                { id: 'sw2', name: 'Switch 2', type: 'switch', domain: 'transport', status: 'warning' },
                { id: 's1', name: 'Application Server', type: 'server', domain: 'core', status: 'healthy' },
                { id: 'gw1', name: 'Internet Gateway', type: 'gateway', domain: 'internet', status: 'healthy' }
            ],
            links: [
                { source: 'ct1', target: 'r1', status: 'healthy' },
                { source: 'ct2', target: 'r1', status: 'healthy' },
                { source: 'ct3', target: 'r1', status: 'critical' },
                { source: 'r1', target: 'sw1', status: 'healthy' },
                { source: 'r1', target: 'sw2', status: 'warning' },
                { source: 'sw1', target: 'r2', status: 'healthy' },
                { source: 'sw2', target: 'r2', status: 'warning' },
                { source: 'r2', target: 's1', status: 'healthy' },
                { source: 'r2', target: 'gw1', status: 'healthy' }
            ]
        };

        this.renderNetwork(mockData);
    }

    // Render the network visualization
    renderNetwork(data) {
        const container = this.svg.select('g');

        // Define arrow markers for links
        container.append('defs').selectAll('marker')
            .data(['end'])      
            .enter().append('marker')    
            .attr('id', d => d)
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 15)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#999');

        // Create links
        this.link = container.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(data.links)
            .enter().append('line')
            .attr('stroke-width', 2)
            .attr('marker-end', 'url(#end)')
            .attr('class', d => `link link-status-${d.status}`);

        // Create nodes
        this.node = container.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(data.nodes)
            .enter().append('g')
            .attr('class', 'node')
            .call(d3.drag()
                .on('start', this.dragStarted.bind(this))
                .on('drag', this.dragged.bind(this))
                .on('end', this.dragEnded.bind(this)));

        // Node circles
        this.node.append('circle')
            .attr('r', 8)
            .attr('fill', d => this.nodeTypes[d.type]?.color || '#999')
            .attr('class', d => `node-status-${d.status}`);

        // Node labels
        this.node.append('text')
            .attr('dy', -12)
            .attr('text-anchor', 'middle')
            .text(d => d.name)
            .attr('font-size', '10px');

        // Set up force simulation
        this.simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(20))
            .on('tick', this.ticked.bind(this));
    }

    // Update positions on simulation tick
    ticked() {
        this.link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        this.node
            .attr('transform', d => `translate(${d.x}, ${d.y})`);
    }

    // Drag handlers
    dragStarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    dragEnded(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // Update node statuses based on alerts or KPIs
    updateNodeStatus(nodeId, status) {
        this.node.filter(d => d.id === nodeId)
            .select('circle')
            .attr('class', `node-status-${status}`);
    }

    // Update link statuses
    updateLinkStatus(source, target, status) {
        this.link.filter(d => d.source.id === source && d.target.id === target)
            .attr('class', `link link-status-${status}`);
    }

    // Highlight path from source to target
    highlightPath(path) {
        // Reset all nodes and links
        this.node.select('circle').classed('highlighted', false);
        this.link.classed('highlighted', false);

        // Highlight nodes in path
        path.nodes.forEach(nodeId => {
            this.node.filter(d => d.id === nodeId)
                .select('circle')
                .classed('highlighted', true);
        });

        // Highlight links in path
        for (let i = 0; i < path.nodes.length - 1; i++) {
            const sourceId = path.nodes[i];
            const targetId = path.nodes[i + 1];
            
            this.link.filter(d => 
                (d.source.id === sourceId && d.target.id === targetId) ||
                (d.source.id === targetId && d.target.id === sourceId)
            ).classed('highlighted', true);
        }
    }
}

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize topology visualization if the container exists
    const topologyContainer = document.getElementById('network-topology');
    if (topologyContainer) {
        const topology = new NetworkTopologyVisualization('network-topology');
        topology.init();
        topology.loadData();
        
        // Store instance for potential external access
        window.networkTopology = topology;
    }
});
