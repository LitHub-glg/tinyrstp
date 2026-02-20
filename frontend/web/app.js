const API_BASE = 'http://localhost:5002';

let topologyData = null;
let selectedNode = null;
let selectedLink = null;
let nodePositions = {};
let demoRunning = false;
let demoSteps = [];

const canvas = document.getElementById('networkCanvas');
const ctx = canvas.getContext('2d');

const colors = {
    normalNode: '#4488ff',
    rootNode: '#44ff44',
    failedNode: '#ff4444',
    stLink: '#44ff44',
    backupLink: '#cccccc',
    failedLink: '#888888',
    selected: '#ffff00',
    text: '#ffffff',
    textDark: '#000000'
};

function resizeCanvas() {
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
    draw();
}

window.addEventListener('resize', resizeCanvas);

function setStatus(text, type = '') {
    const statusEl = document.getElementById('statusText');
    statusEl.textContent = text;
    statusEl.className = type;
}

function updateLastUpdate() {
    const el = document.getElementById('lastUpdate');
    const now = new Date();
    el.textContent = `Last update: ${now.toLocaleTimeString()}`;
}

async function fetchTopology() {
    try {
        setStatus('Loading...', 'loading');
        const response = await fetch(`${API_BASE}/api/topology`);
        if (!response.ok) throw new Error('Failed to fetch topology');
        topologyData = await response.json();
        calculateNodePositions();
        draw();
        updateLastUpdate();
        setStatus('Ready');
    } catch (error) {
        console.error('Error fetching topology:', error);
        setStatus('Error: Cannot connect to server', 'error');
    }
}

function calculateNodePositions() {
    if (!topologyData || !topologyData.nodes) return;
    
    const layout = {
        'Node1': { x: -1, y: 1 },
        'Node2': { x: 1, y: 1 },
        'Node3': { x: -1, y: -1 },
        'Node4': { x: 1, y: -1 }
    };
    
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;
    const centerX = canvasWidth / 2;
    const centerY = canvasHeight / 2;
    const scale = Math.min(canvasWidth, canvasHeight) * 0.3;
    
    for (const [nodeId, nodeData] of Object.entries(topologyData.nodes)) {
        const nodeName = nodeData.node_name;
        if (layout[nodeName]) {
            nodePositions[nodeId] = {
                x: centerX + layout[nodeName].x * scale,
                y: centerY - layout[nodeName].y * scale
            };
        }
    }
}

function draw() {
    if (!topologyData) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    drawLinks();
    drawNodes();
}

function drawLinks() {
    if (!topologyData.links) return;
    
    const stLinks = new Set(topologyData.spanning_tree || []);
    
    for (const [linkId, linkData] of Object.entries(topologyData.links)) {
        const nodes = linkData.nodes;
        if (nodes.length < 2) continue;
        
        const n1Pos = nodePositions[nodes[0]];
        const n2Pos = nodePositions[nodes[1]];
        if (!n1Pos || !n2Pos) continue;
        
        const isST = stLinks.has(linkId);
        const isSelected = selectedLink === linkId;
        const isDown = linkData.state === 'DOWN';
        
        let color;
        if (isSelected) {
            color = colors.selected;
        } else if (isDown) {
            color = colors.failedLink;
        } else if (isST) {
            color = colors.stLink;
        } else {
            color = colors.backupLink;
        }
        
        const lineWidth = isSelected ? 6 : (isST ? 4 : 2);
        
        ctx.beginPath();
        ctx.moveTo(n1Pos.x, n1Pos.y);
        ctx.lineTo(n2Pos.x, n2Pos.y);
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth;
        ctx.stroke();
    }
}

function drawNodes() {
    if (!topologyData.nodes) return;
    
    for (const [nodeId, nodeData] of Object.entries(topologyData.nodes)) {
        const pos = nodePositions[nodeId];
        if (!pos) continue;
        
        const isSelected = selectedNode === nodeId;
        const isRoot = nodeData.is_root;
        const isFailed = nodeData.state === 'FAILED';
        
        let color;
        if (isFailed) {
            color = colors.failedNode;
        } else if (isRoot) {
            color = colors.rootNode;
        } else {
            color = colors.normalNode;
        }
        
        const radius = isSelected ? 35 : 30;
        
        if (isSelected) {
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, radius + 5, 0, Math.PI * 2);
            ctx.fillStyle = colors.selected;
            ctx.fill();
        }
        
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        ctx.fillStyle = '#000';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        const nodeName = nodeData.node_name || '';
        const state = nodeData.state === 'ACTIVE' ? 'OK' : 'FL';
        const rootLabel = isRoot ? ' (R)' : '';
        
        ctx.fillText(nodeName, pos.x, pos.y - 8);
        ctx.font = '10px Arial';
        ctx.fillText(`${state}${rootLabel}`, pos.x, pos.y + 10);
    }
}

function getClickedNode(x, y) {
    const tolerance = 40;
    
    for (const [nodeId, pos] of Object.entries(nodePositions)) {
        const dist = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2);
        if (dist < tolerance) {
            return nodeId;
        }
    }
    return null;
}

function getClickedLink(x, y) {
    const tolerance = 15;
    
    for (const [linkId, linkData] of Object.entries(topologyData.links || {})) {
        const nodes = linkData.nodes;
        if (nodes.length < 2) continue;
        
        const n1Pos = nodePositions[nodes[0]];
        const n2Pos = nodePositions[nodes[1]];
        if (!n1Pos || !n2Pos) continue;
        
        const dist = pointToLineDistance(x, y, n1Pos.x, n1Pos.y, n2Pos.x, n2Pos.y);
        if (dist < tolerance) {
            return linkId;
        }
    }
    return null;
}

function pointToLineDistance(px, py, x1, y1, x2, y2) {
    const lineLen = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    if (lineLen === 0) return Math.sqrt((px - x1) ** 2 + (py - y1) ** 2);
    
    const t = Math.max(0, Math.min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (lineLen ** 2)));
    const projX = x1 + t * (x2 - x1);
    const projY = y1 + t * (y2 - y1);
    
    return Math.sqrt((px - projX) ** 2 + (py - projY) ** 2);
}

canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    selectedNode = getClickedNode(x, y);
    if (!selectedNode) {
        selectedLink = getClickedLink(x, y);
    } else {
        selectedLink = null;
    }
    
    updateInfoPanel();
    draw();
});

function updateInfoPanel() {
    const infoContent = document.getElementById('infoContent');
    let html = '';
    
    if (selectedNode) {
        const nodeData = topologyData.nodes[selectedNode];
        if (nodeData) {
            html += `
                <div class="info-section">
                    <h4>[Selected Node]</h4>
                    <div class="info-row">
                        <span class="info-label">Name:</span>
                        <span class="info-value">${nodeData.node_name || '?'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">State:</span>
                        <span class="info-value">${nodeData.state || '?'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Root:</span>
                        <span class="info-value">${nodeData.is_root ? 'Yes' : 'No'}</span>
                    </div>
                </div>
            `;
        }
    }
    
    if (selectedLink) {
        const linkData = topologyData.links[selectedLink];
        if (linkData && linkData.nodes.length >= 2) {
            const n1Data = topologyData.nodes[linkData.nodes[0]] || {};
            const n2Data = topologyData.nodes[linkData.nodes[1]] || {};
            const isST = (topologyData.spanning_tree || []).includes(selectedLink);
            
            html += `
                <div class="info-section">
                    <h4>[Selected Link]</h4>
                    <div class="info-row">
                        <span class="info-label">Nodes:</span>
                        <span class="info-value">${n1Data.node_name || '?'} <-> ${n2Data.node_name || '?'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">State:</span>
                        <span class="info-value">${linkData.state || '?'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Bandwidth:</span>
                        <span class="info-value">${linkData.bandwidth || 0} Mbps</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Spanning Tree:</span>
                        <span class="info-value">${isST ? 'Yes' : 'No'}</span>
                    </div>
                </div>
            `;
        }
    }
    
    if (!html) {
        html = '<p class="placeholder">Click on a node or link to see details</p>';
    }
    
    infoContent.innerHTML = html;
}

async function apiCall(method, endpoint) {
    try {
        setStatus('Processing...', 'loading');
        const response = await fetch(`${API_BASE}${endpoint}`, { method });
        const result = await response.json();
        await fetchTopology();
        return result;
    } catch (error) {
        console.error('API Error:', error);
        setStatus('Error: ' + error.message, 'error');
        return null;
    }
}

function findLinkByNodes(node1Name, node2Name) {
    for (const [linkId, linkData] of Object.entries(topologyData.links || {})) {
        const nodes = linkData.nodes;
        if (nodes.length < 2) continue;
        const n1 = topologyData.nodes[nodes[0]];
        const n2 = topologyData.nodes[nodes[1]];
        if (n1 && n2) {
            if ((n1.node_name === node1Name && n2.node_name === node2Name) ||
                (n1.node_name === node2Name && n2.node_name === node1Name)) {
                return linkId;
            }
        }
    }
    return null;
}

function findNodeByName(nodeName) {
    for (const [nodeId, nodeData] of Object.entries(topologyData.nodes || {})) {
        if (nodeData.node_name === nodeName) {
            return nodeId;
        }
    }
    return null;
}

// Link Control Buttons
document.getElementById('btnLinkDown').addEventListener('click', () => {
    if (selectedLink) apiCall('POST', `/api/links/${selectedLink}/down`);
    else alert('Please select a link first');
});

document.getElementById('btnLinkUp').addEventListener('click', () => {
    if (selectedLink) apiCall('POST', `/api/links/${selectedLink}/up`);
    else alert('Please select a link first');
});

document.getElementById('btnLinkToggle').addEventListener('click', () => {
    if (selectedLink) apiCall('POST', `/api/links/${selectedLink}/toggle`);
    else alert('Please select a link first');
});

// Node Control Buttons
document.getElementById('btnNodeFail').addEventListener('click', () => {
    if (selectedNode) apiCall('POST', `/api/nodes/${selectedNode}/fail`);
    else alert('Please select a node first');
});

document.getElementById('btnNodeRecover').addEventListener('click', () => {
    if (selectedNode) apiCall('POST', `/api/nodes/${selectedNode}/recover`);
    else alert('Please select a node first');
});

// System Button
document.getElementById('btnReset').addEventListener('click', () => {
    apiCall('POST', '/api/topology/reset');
});

// Demo Button - Composite Failure Scenario
document.getElementById('btnDemo').addEventListener('click', async () => {
    if (demoRunning) return;
    
    demoRunning = true;
    setButtonsDisabled(true);
    setStatus('Demo Running...', 'demo');
    
    const demoStatusEl = document.getElementById('demoStatus');
    const demoProgressEl = document.getElementById('demoProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    demoProgressEl.style.display = 'block';
    
    const steps = [
        {
            title: 'Step 1: Initial State',
            desc: 'All nodes and links are operational. Network is stable.',
            action: async () => {
                await apiCall('POST', '/api/topology/reset');
            },
            expected: '4 active nodes, 6 UP links, spanning tree formed'
        },
        {
            title: 'Step 2: Link Failure (Node1-Node2)',
            desc: 'Injecting failure on the link between Node1 and Node2.',
            action: async () => {
                const linkId = findLinkByNodes('Node1', 'Node2');
                if (linkId) await apiCall('POST', `/api/links/${linkId}/down`);
            },
            expected: 'Link goes DOWN, spanning tree recalculates'
        },
        {
            title: 'Step 3: Node Failure (Node3)',
            desc: 'Injecting failure on Node3. This affects multiple links.',
            action: async () => {
                const nodeId = findNodeByName('Node3');
                if (nodeId) await apiCall('POST', `/api/nodes/${nodeId}/fail`);
            },
            expected: 'Node3 becomes FAILED, 3 links affected'
        },
        {
            title: 'Step 4: Observe Network State',
            desc: 'Network has adapted to failures. Remaining nodes stay connected.',
            action: async () => {
                await fetchTopology();
            },
            expected: '3 active nodes, spanning tree maintains connectivity'
        },
        {
            title: 'Step 5: Recover Node3',
            desc: 'Restoring Node3 to active state.',
            action: async () => {
                const nodeId = findNodeByName('Node3');
                if (nodeId) await apiCall('POST', `/api/nodes/${nodeId}/recover`);
            },
            expected: 'Node3 recovers, links restored'
        },
        {
            title: 'Step 6: Recover Link (Node1-Node2)',
            desc: 'Restoring the link between Node1 and Node2.',
            action: async () => {
                const linkId = findLinkByNodes('Node1', 'Node2');
                if (linkId) await apiCall('POST', `/api/links/${linkId}/up`);
            },
            expected: 'Link goes UP, spanning tree optimizes'
        },
        {
            title: 'Step 7: Final State',
            desc: 'All failures recovered. Network returns to optimal state.',
            action: async () => {
                await fetchTopology();
            },
            expected: '4 active nodes, 6 UP links, optimal spanning tree'
        }
    ];
    
    let html = '';
    for (let i = 0; i < steps.length; i++) {
        html += `
            <div class="demo-step" id="demo-step-${i}">
                <div class="step-title">${steps[i].title}</div>
                <div class="step-desc">${steps[i].desc}</div>
                <div class="step-result" id="step-result-${i}">Expected: ${steps[i].expected}</div>
            </div>
        `;
    }
    demoStatusEl.innerHTML = html;
    
    for (let i = 0; i < steps.length; i++) {
        const stepEl = document.getElementById(`demo-step-${i}`);
        stepEl.classList.add('active');
        
        progressFill.style.width = `${((i + 1) / steps.length) * 100}%`;
        progressText.textContent = `Step ${i + 1}/${steps.length}`;
        
        await steps[i].action();
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const resultEl = document.getElementById(`step-result-${i}`);
        resultEl.textContent = 'Completed: ' + steps[i].expected;
        
        stepEl.classList.remove('active');
        stepEl.classList.add('completed');
    }
    
    progressFill.style.width = '100%';
    progressText.textContent = 'Demo Complete!';
    setStatus('Demo Complete', 'demo');
    
    setTimeout(() => {
        demoRunning = false;
        setButtonsDisabled(false);
        setStatus('Ready');
    }, 2000);
});

function setButtonsDisabled(disabled) {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        if (btn.id !== 'btnDemo') {
            btn.disabled = disabled;
        }
    });
}

resizeCanvas();
fetchTopology();

setInterval(() => {
    if (!demoRunning) {
        fetchTopology();
    }
}, 5000);
