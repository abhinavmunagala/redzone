#!/usr/bin/env python3
"""
RedZone UI Server
Serves the visualization dashboard and handles reconnaissance API
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys

sys.path.insert(0, str(Path(__file__).parent))

from services.reconnaissance.service import ReconnaissanceService


class RedZoneHandler(BaseHTTPRequestHandler):
    """HTTP request handler for RedZone UI."""

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        if path == '/' or path == '/dashboard':
            self.serve_dashboard()
        elif path == '/api/recon':
            self.handle_recon_request(query_params)
        elif path == '/api/status':
            self.send_status()
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/scan':
            self.handle_scan_request()
        else:
            self.send_error(404)

    def serve_dashboard(self):
        """Serve the RedZone dashboard UI."""
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RedZone - Reconnaissance Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0e27 0%, #0f1419 50%, #1a0f2e 100%);
            color: #e0e0e0;
            font-family: 'Courier New', monospace;
            overflow: hidden;
            height: 100vh;
        }
        .container { display: flex; height: 100vh; width: 100%; }
        .sidebar {
            width: 300px;
            background: rgba(10, 14, 39, 0.95);
            border-right: 2px solid #00d9ff;
            overflow-y: auto;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.1);
        }
        .logo {
            font-size: 18px;
            font-weight: bold;
            color: #ff0055;
            margin-bottom: 20px;
            text-shadow: 0 0 10px #ff0055;
            letter-spacing: 2px;
        }
        .domain-input {
            margin-bottom: 20px;
        }
        .domain-input input {
            width: 100%;
            padding: 10px;
            background: rgba(0, 217, 255, 0.1);
            border: 1px solid #00d9ff;
            color: #00d9ff;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
        }
        .domain-input button {
            width: 100%;
            padding: 10px;
            background: #00d9ff;
            color: #0a0e27;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
            font-family: monospace;
            transition: all 0.3s;
        }
        .domain-input button:hover {
            background: #00ff88;
            box-shadow: 0 0 15px #00ff88;
        }
        .stats-box {
            background: rgba(0, 217, 255, 0.05);
            border: 1px solid #00d9ff;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 12px;
        }
        .stat-label { color: #888; }
        .stat-value {
            color: #00d9ff;
            font-weight: bold;
        }
        .stat-value.high { color: #00ff88; }
        .stat-value.medium { color: #ffaa00; }
        .section-title {
            color: #00ff88;
            font-size: 13px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 10px;
            text-shadow: 0 0 5px #00ff88;
            border-bottom: 1px solid rgba(0, 255, 136, 0.3);
            padding-bottom: 5px;
        }
        .asset-list {
            max-height: 200px;
            overflow-y: auto;
            font-size: 11px;
        }
        .asset-item {
            padding: 8px;
            background: rgba(0, 217, 255, 0.05);
            border-left: 2px solid #00d9ff;
            margin-bottom: 5px;
            cursor: pointer;
            transition: all 0.2s;
            border-radius: 2px;
        }
        .asset-item:hover {
            background: rgba(0, 217, 255, 0.15);
            border-left: 2px solid #00ff88;
        }
        .asset-item.high-conf {
            border-left: 2px solid #00ff88;
            color: #00ff88;
        }
        .asset-item.med-conf {
            border-left: 2px solid #ffaa00;
            color: #ffaa00;
        }
        .canvas {
            flex: 1;
            position: relative;
            background: radial-gradient(circle at 50% 50%, rgba(0, 217, 255, 0.05) 0%, transparent 50%);
            overflow: hidden;
        }
        #graph {
            width: 100%;
            height: 100%;
            position: relative;
        }
        svg { width: 100%; height: 100%; }
        .node-circle {
            cursor: pointer;
            stroke-width: 2px;
            transition: all 0.2s;
        }
        .node-circle:hover {
            filter: drop-shadow(0 0 10px currentColor);
            stroke-width: 3px;
        }
        .link {
            stroke: rgba(0, 217, 255, 0.3);
            stroke-width: 1px;
            pointer-events: none;
        }
        .node-label {
            font-size: 10px;
            pointer-events: none;
            text-anchor: middle;
            fill: #e0e0e0;
            text-shadow: 0 0 3px rgba(0, 0, 0, 0.8);
        }
        .details-panel {
            width: 350px;
            background: rgba(10, 14, 39, 0.95);
            border-left: 2px solid #ff0055;
            overflow-y: auto;
            padding: 20px;
            box-shadow: 0 0 20px rgba(255, 0, 85, 0.1);
        }
        .detail-title {
            font-size: 14px;
            color: #ff0055;
            font-weight: bold;
            margin-bottom: 15px;
            text-shadow: 0 0 10px #ff0055;
        }
        .detail-item {
            background: rgba(255, 0, 85, 0.05);
            border: 1px solid rgba(255, 0, 85, 0.2);
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
            font-size: 11px;
        }
        .detail-label {
            color: #888;
            font-size: 10px;
            margin-bottom: 3px;
            text-transform: uppercase;
        }
        .detail-value {
            color: #e0e0e0;
            word-break: break-all;
        }
        .confidence-badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
            margin-left: 5px;
        }
        .confidence-badge.high {
            background: #00ff88;
            color: #0a0e27;
        }
        .confidence-badge.medium {
            background: #ffaa00;
            color: #0a0e27;
        }
        .toolbar {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(10, 14, 39, 0.95);
            border: 1px solid #00d9ff;
            border-radius: 4px;
            padding: 10px;
            z-index: 1000;
        }
        .toolbar button {
            background: transparent;
            border: 1px solid #00d9ff;
            color: #00d9ff;
            padding: 8px 12px;
            margin: 5px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            font-family: monospace;
            transition: all 0.2s;
        }
        .toolbar button:hover {
            background: #00d9ff;
            color: #0a0e27;
        }
        .tooltip {
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: #00d9ff;
            padding: 10px 15px;
            border-radius: 4px;
            font-size: 11px;
            pointer-events: none;
            border: 1px solid #00d9ff;
            white-space: nowrap;
            box-shadow: 0 0 15px rgba(0, 217, 255, 0.3);
        }
        .loading {
            text-align: center;
            color: #00d9ff;
            padding: 20px;
        }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(0, 217, 255, 0.3);
            border-top-color: #00d9ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="logo">🎯 DAC - REDZONE</div>
            <div style="font-size: 9px; color: #00d9ff; margin-bottom: 15px; opacity: 0.7;">Dark Attack Console</div>

            <div class="domain-input">
                <input type="text" id="domainInput" placeholder="example.com" value="">
                <button id="scanBtn">SCAN</button>
            </div>

            <div class="stats-box">
                <div class="stat-item">
                    <span class="stat-label">Subdomains:</span>
                    <span class="stat-value" id="statTotal">-</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">High Conf:</span>
                    <span class="stat-value high" id="statHigh">-</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Medium Conf:</span>
                    <span class="stat-value medium" id="statMedium">-</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Unique IPs:</span>
                    <span class="stat-value" id="statIps">-</span>
                </div>
            </div>

            <div class="section-title">🌐 SUBDOMAINS</div>
            <div class="asset-list" id="assetList"></div>

            <div class="section-title">🗺️ INFRASTRUCTURE</div>
            <div class="asset-list" id="asnList"></div>
        </div>

        <div class="canvas">
            <div id="graph"></div>
            <div class="toolbar">
                <button id="resetBtn">↺ Reset</button>
                <button id="exportBtn">⬇ Export</button>
            </div>
            <div id="tooltip" class="tooltip" style="display: none;"></div>
        </div>

        <div class="details-panel">
            <div class="detail-title" id="detailTitle">SELECT NODE</div>
            <div id="detailContent" style="color: #888;">Click on a node to view details</div>
        </div>
    </div>

    <script>
        let currentData = null;
        let simulation = null;
        const colors = {
            highConf: '#00ff88',
            medConf: '#ffaa00',
            ip: '#00d9ff',
            asn: '#ff0055',
            link: 'rgba(0, 217, 255, 0.2)'
        };

        function buildGraphData(reconData) {
            const nodes = [];
            const links = [];

            const rootNode = {
                id: reconData.domain,
                type: 'domain',
                label: reconData.domain,
                radius: 15
            };
            nodes.push(rootNode);

            reconData.subdomains.forEach((sub) => {
                const confidence = sub.confidence;
                const nodeType = confidence >= 0.8 ? 'high' : confidence >= 0.6 ? 'medium' : 'low';

                const node = {
                    id: sub.host,
                    type: 'subdomain',
                    label: sub.host.replace('.' + reconData.domain, ''),
                    fullHost: sub.host,
                    confidence: confidence,
                    sources: sub.sources,
                    nodeType: nodeType,
                    radius: 8
                };
                nodes.push(node);

                links.push({
                    source: reconData.domain,
                    target: sub.host,
                    type: 'subdomain'
                });
            });

            reconData.asn_info.forEach(asn => {
                const node = {
                    id: asn.asn,
                    type: 'asn',
                    label: asn.asn,
                    org: asn.org,
                    radius: 10
                };
                nodes.push(node);

                links.push({
                    source: reconData.domain,
                    target: asn.asn,
                    type: 'asn'
                });
            });

            return { nodes, links };
        }

        function updateStats(reconData) {
            const total = reconData.subdomains.length;
            const high = reconData.subdomains.filter(s => s.confidence >= 0.8).length;
            const medium = reconData.subdomains.filter(s => s.confidence < 0.8 && s.confidence >= 0.6).length;
            const ips = reconData.ips ? reconData.ips.length : 0;

            document.getElementById('statTotal').textContent = total;
            document.getElementById('statHigh').textContent = high;
            document.getElementById('statMedium').textContent = medium;
            document.getElementById('statIps').textContent = ips;

            const assetList = document.getElementById('assetList');
            assetList.innerHTML = reconData.subdomains.map(sub => {
                const confClass = sub.confidence >= 0.8 ? 'high-conf' : 'med-conf';
                const confPercent = (sub.confidence * 100).toFixed(0);
                return `<div class="asset-item ${confClass}">${sub.host} <span style="font-size: 9px; opacity: 0.7;">${confPercent}%</span></div>`;
            }).join('');

            const asnList = document.getElementById('asnList');
            asnList.innerHTML = reconData.asn_info.map(asn =>
                `<div class="asset-item">${asn.asn}: ${asn.org}</div>`
            ).join('');
        }

        function renderGraph(graphData) {
            const svg = d3.select('#graph').selectAll('*').remove();
            const width = document.querySelector('.canvas').clientWidth;
            const height = document.querySelector('.canvas').clientHeight;

            const svgElement = d3.select('#graph').append('svg')
                .attr('width', width)
                .attr('height', height);

            const g = svgElement.append('g');
            const zoom = d3.zoom().on('zoom', (event) => {
                g.attr('transform', event.transform);
            });
            svgElement.call(zoom);

            simulation = d3.forceSimulation(graphData.nodes)
                .force('link', d3.forceLink(graphData.links)
                    .id(d => d.id)
                    .distance(d => d.type === 'subdomain' ? 80 : 100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collide', d3.forceCollide().radius(d => d.radius + 10));

            const link = g.append('g')
                .selectAll('line')
                .data(graphData.links)
                .join('line')
                .attr('class', 'link')
                .attr('stroke', d => d.type === 'asn' ? colors.asn : colors.link);

            const node = g.append('g')
                .selectAll('circle')
                .data(graphData.nodes)
                .join('circle')
                .attr('class', 'node-circle')
                .attr('r', d => d.radius)
                .attr('fill', d => {
                    if (d.type === 'domain') return colors.asn;
                    if (d.type === 'asn') return colors.asn;
                    if (d.type === 'ip') return colors.ip;
                    if (d.nodeType === 'high') return colors.highConf;
                    if (d.nodeType === 'medium') return colors.medConf;
                    return colors.ip;
                })
                .attr('stroke', d => d.type === 'domain' ? '#fff' : 'rgba(255,255,255,0.3)');

            const labels = g.append('g')
                .selectAll('text')
                .data(graphData.nodes)
                .join('text')
                .attr('class', 'node-label')
                .attr('dy', '.3em')
                .text(d => d.label);

            node.on('click', (event, d) => selectNode(d.id));

            simulation.on('tick', () => {
                link.attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node.attr('cx', d => d.x)
                    .attr('cy', d => d.y);

                labels.attr('x', d => d.x)
                    .attr('y', d => d.y);
            });

            setTimeout(() => {
                const bounds = g.node().getBBox();
                const scale = Math.min(width / (bounds.width + 100), height / (bounds.height + 100));
                const tx = (width - (bounds.width + 100) * scale) / 2;
                const ty = (height - (bounds.height + 100) * scale) / 2;
                svgElement.transition().duration(750)
                    .call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
            }, 100);
        }

        function selectNode(nodeId) {
            const detailTitle = document.getElementById('detailTitle');
            const detailContent = document.getElementById('detailContent');

            const node = currentData.nodes.find(n => n.id === nodeId);
            if (!node) return;

            detailTitle.innerHTML = `📍 ${node.label}`;

            let html = '';
            if (node.type === 'subdomain') {
                const conf = (node.confidence * 100).toFixed(1);
                html = `
                    <div class="detail-item">
                        <div class="detail-label">Type</div>
                        <div class="detail-value">Subdomain</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Host</div>
                        <div class="detail-value">${node.fullHost}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Confidence</div>
                        <div class="detail-value">${conf}% ${conf >= 80 ? '<span class="confidence-badge high">HIGH</span>' : '<span class="confidence-badge medium">MEDIUM</span>'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Sources</div>
                        <div class="detail-value">${node.sources.join(', ')}</div>
                    </div>
                `;
            } else if (node.type === 'asn') {
                html = `
                    <div class="detail-item">
                        <div class="detail-label">Type</div>
                        <div class="detail-value">Autonomous System</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">ASN</div>
                        <div class="detail-value">${node.id}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Organization</div>
                        <div class="detail-value">${node.org}</div>
                    </div>
                `;
            }

            detailContent.innerHTML = html;
        }

        async function scanDomain() {
            const domain = document.getElementById('domainInput').value.trim();
            if (!domain) return;

            document.getElementById('graph').innerHTML = '<div class="loading"><div class="spinner"></div><br>Scanning...</div>';
            document.getElementById('statTotal').textContent = '-';
            document.getElementById('statHigh').textContent = '-';
            document.getElementById('statMedium').textContent = '-';
            document.getElementById('statIps').textContent = '-';

            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ domain })
                });

                if (!response.ok) throw new Error('Scan failed');

                const data = await response.json();
                currentData = buildGraphData(data);
                updateStats(data);
                renderGraph(currentData);
            } catch (error) {
                document.getElementById('graph').innerHTML = `<div class="loading" style="color: #ff0055;">Error: ${error.message}</div>`;
            }
        }

        document.getElementById('scanBtn').addEventListener('click', scanDomain);
        document.getElementById('domainInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') scanDomain();
        });

        document.getElementById('resetBtn').addEventListener('click', () => {
            if (simulation) {
                const width = document.querySelector('.canvas').clientWidth;
                const height = document.querySelector('.canvas').clientHeight;
                d3.select('svg').transition().duration(750)
                    .call(d3.zoom().transform, d3.zoomIdentity.translate(0, 0).scale(1));
            }
        });

        document.getElementById('exportBtn').addEventListener('click', () => {
            const json = JSON.stringify(currentData, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'redzone-recon.json';
            a.click();
        });
    </script>
</body>
</html>'''

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def handle_scan_request(self):
        """Handle reconnaissance scan request."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body)
            domain = data.get('domain', 'example.com').strip().lower()

            # Run reconnaissance
            service = ReconnaissanceService(active_probing=False)
            results = service.passive_recon_premium(domain)

            # Consolidate subdomains from all sources
            all_subdomains = {}
            for sub in results["subdomains"].get("amass", []):
                host = sub.get("host", "")
                if host not in all_subdomains:
                    all_subdomains[host] = {
                        "confidence": sub.get("confidence", 0.8),
                        "sources": []
                    }
                all_subdomains[host]["sources"].append("amass")

            for sub in results["subdomains"].get("sn1per", []):
                host = sub.get("host", "")
                if host not in all_subdomains:
                    all_subdomains[host] = {
                        "confidence": sub.get("confidence", 0.6),
                        "sources": []
                    }
                all_subdomains[host]["sources"].append("sn1per")

            # Format response
            response = {
                "domain": domain,
                "timestamp": datetime.utcnow().isoformat(),
                "subdomains": [
                    {
                        "host": host,
                        "confidence": info.get("confidence", 0.5),
                        "sources": info.get("sources", [])
                    }
                    for host, info in all_subdomains.items()
                ],
                "asn_info": [
                    {
                        "asn": asn.get("asn", ""),
                        "org": asn.get("org", asn.get("organization", "")),
                        "country": asn.get("country", "")
                    }
                    for asn in results["asn_info"]
                ],
                "ips": results["all_hosts"]
            }

            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def handle_recon_request(self, query_params):
        """Handle general reconnaissance request."""
        domain = query_params.get('domain', ['example.com'])[0].strip().lower()

        service = ReconnaissanceService(active_probing=False)
        results = service.passive_recon_premium(domain)

        response = {
            "domain": domain,
            "summary": {
                "total_subdomains": len(results["all_hosts"]),
                "techniques_used": results["techniques"]
            },
            "data": results
        }

        self.send_json_response(response)

    def send_status(self):
        """Send server status."""
        response = {
            "status": "online",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
        self.send_json_response(response)

    def send_json_response(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error(self, code):
        """Send error response."""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": f"HTTP {code}"}).encode())

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def run_server(port=8000):
    """Run the RedZone server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, RedZoneHandler)

    print(f"""
    ╔════════════════════════════════════════╗
    ║     🎯 RedZone Reconnaissance UI      ║
    ║          Server Running 🚀            ║
    ╚════════════════════════════════════════╝

    📍 URL:  http://localhost:{port}

    Commands:
      • Visit dashboard at http://localhost:{port}
      • API endpoint:    http://localhost:{port}/api/recon?domain=example.com

    Press Ctrl+C to stop
    """)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped")
        httpd.server_close()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
