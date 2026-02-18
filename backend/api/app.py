from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.core.topology import Topology
from backend.core.node import Node
from backend.core.link import Link
from backend.core.stp import STPCalculator
from backend.utils.logger import get_logger
import time


class NetworkAPI:
    def __init__(self):
        self.logger = get_logger(log_dir='logs')
        self.logger.startup('NetworkAPI')

        self.app = Flask(__name__)
        CORS(self.app)
        self.topology = Topology()
        self.stp_calculator = STPCalculator(self.topology)
        self.last_topology_change = 0
        self.topology_change_cooldown = 1.0

        self._setup_4_node_full_mesh()
        self.stp_calculator.update_and_apply()
        self._setup_routes()

    def _setup_routes(self):
        self.app.add_url_rule('/api/topology', view_func=self.get_topology, methods=['GET'])
        self.app.add_url_rule('/api/topology/reset', view_func=self.reset_topology, methods=['POST'])
        self.app.add_url_rule('/api/topology/nodes', view_func=self.get_nodes, methods=['GET'])
        self.app.add_url_rule('/api/topology/links', view_func=self.get_links, methods=['GET'])
        self.app.add_url_rule('/api/topology/spanning-tree', view_func=self.get_spanning_tree, methods=['GET'])
        self.app.add_url_rule('/api/nodes/<node_id>/fail', view_func=self.fail_node, methods=['POST'])
        self.app.add_url_rule('/api/nodes/<node_id>/recover', view_func=self.recover_node, methods=['POST'])
        self.app.add_url_rule('/api/links/<link_id>/toggle', view_func=self.toggle_link, methods=['POST'])
        self.app.add_url_rule('/api/links/<link_id>/up', view_func=self.link_up, methods=['POST'])
        self.app.add_url_rule('/api/links/<link_id>/down', view_func=self.link_down, methods=['POST'])
        self.app.add_url_rule('/api/test/scenario/<scenario_name>', view_func=self.run_scenario, methods=['POST'])
        self.app.add_url_rule('/api/test/status', view_func=self.get_test_status, methods=['GET'])
        self.app.add_url_rule('/api/debug/status', view_func=self.debug_status, methods=['GET'])
        self.app.add_url_rule('/api/debug/nodes/<node_id>', view_func=self.debug_node, methods=['GET'])
        self.app.add_url_rule('/api/debug/links/<link_id>', view_func=self.debug_link, methods=['GET'])
        self.app.add_url_rule('/api/debug/logs', view_func=self.debug_logs, methods=['GET'])

    def _log_request(self, endpoint: str, method: str = 'GET'):
        self.logger.api_request(method, endpoint)

    def _log_response(self, endpoint: str, status_code: int, method: str = 'GET'):
        self.logger.api_response(method, endpoint, status_code)

    def get_topology(self):
        self._log_request('/api/topology', 'GET')
        result = jsonify(self.topology.to_dict())
        self._log_response('/api/topology', 200, 'GET')
        return result

    def reset_topology(self):
        self._log_request('/api/topology/reset', 'POST')
        self._setup_4_node_full_mesh()
        self.stp_calculator.update_and_apply()
        self.logger.topology_change('reset', {'node_count': 4, 'link_count': 6})
        self._log_response('/api/topology/reset', 200, 'POST')
        return jsonify({'status': 'success', 'message': 'Topology reset'})

    def get_nodes(self):
        self._log_request('/api/topology/nodes', 'GET')
        nodes = [n.to_dict() for n in self.topology.get_all_nodes()]
        self._log_response('/api/topology/nodes', 200, 'GET')
        return jsonify({'nodes': nodes})

    def get_links(self):
        self._log_request('/api/topology/links', 'GET')
        links = [l.to_dict() for l in self.topology.get_all_links()]
        self._log_response('/api/topology/links', 200, 'GET')
        return jsonify({'links': links})

    def get_spanning_tree(self):
        self._log_request('/api/topology/spanning-tree', 'GET')
        result = jsonify(self.stp_calculator.get_spanning_tree_info())
        self._log_response('/api/topology/spanning-tree', 200, 'GET')
        return result

    def fail_node(self, node_id):
        self._log_request(f'/api/nodes/{node_id}/fail', 'POST')
        node = self.topology.get_node(node_id)
        if node:
            node.set_failed()
            self._recalculate_stp()
            self.logger.node_event(node_id, 'failed', {'node_name': node.node_name})
            self._log_response(f'/api/nodes/{node_id}/fail', 200, 'POST')
            return jsonify({'status': 'success', 'message': f'Node {node.node_name} failed'})
        self._log_response(f'/api/nodes/{node_id}/fail', 404, 'POST')
        return jsonify({'status': 'error', 'message': 'Node not found'}), 404

    def recover_node(self, node_id):
        self._log_request(f'/api/nodes/{node_id}/recover', 'POST')
        node = self.topology.get_node(node_id)
        if node:
            node.set_active()
            self._recalculate_stp()
            self.logger.node_event(node_id, 'recovered', {'node_name': node.node_name})
            self._log_response(f'/api/nodes/{node_id}/recover', 200, 'POST')
            return jsonify({'status': 'success', 'message': f'Node {node.node_name} recovered'})
        self._log_response(f'/api/nodes/{node_id}/recover', 404, 'POST')
        return jsonify({'status': 'error', 'message': 'Node not found'}), 404

    def toggle_link(self, link_id):
        self._log_request(f'/api/links/{link_id}/toggle', 'POST')
        link = self.topology.get_link(link_id)
        if link:
            if link.is_up():
                link.set_state(link.state.__class__.DOWN)
                state = 'DOWN'
            else:
                link.set_state(link.state.__class__.UP)
                state = 'UP'
            self._recalculate_stp()
            self.logger.link_event(link_id, f'toggled_to_{state}')
            self._log_response(f'/api/links/{link_id}/toggle', 200, 'POST')
            return jsonify({'status': 'success', 'message': f'Link {link_id} toggled'})
        self._log_response(f'/api/links/{link_id}/toggle', 404, 'POST')
        return jsonify({'status': 'error', 'message': 'Link not found'}), 404

    def link_up(self, link_id):
        self._log_request(f'/api/links/{link_id}/up', 'POST')
        link = self.topology.get_link(link_id)
        if link:
            link.set_state(link.state.__class__.UP)
            self._recalculate_stp()
            self.logger.link_event(link_id, 'up')
            self._log_response(f'/api/links/{link_id}/up', 200, 'POST')
            return jsonify({'status': 'success', 'message': f'Link {link_id} up'})
        self._log_response(f'/api/links/{link_id}/up', 404, 'POST')
        return jsonify({'status': 'error', 'message': 'Link not found'}), 404

    def link_down(self, link_id):
        self._log_request(f'/api/links/{link_id}/down', 'POST')
        link = self.topology.get_link(link_id)
        if link:
            link.set_state(link.state.__class__.DOWN)
            self._recalculate_stp()
            self.logger.link_event(link_id, 'down')
            self._log_response(f'/api/links/{link_id}/down', 200, 'POST')
            return jsonify({'status': 'success', 'message': f'Link {link_id} down'})
        self._log_response(f'/api/links/{link_id}/down', 404, 'POST')
        return jsonify({'status': 'error', 'message': 'Link not found'}), 404

    def run_scenario(self, scenario_name):
        self._log_request(f'/api/test/scenario/{scenario_name}', 'POST')
        if scenario_name == 'link_failure':
            result = self.topology.inject_link_failure('Node1', 'Node2')
            if result:
                self._recalculate_stp()
                self.logger.scenario_execution('link_failure', 'success')
                self._log_response(f'/api/test/scenario/{scenario_name}', 200, 'POST')
                return jsonify({'status': 'success', 'message': 'Link failure scenario executed'})
        elif scenario_name == 'link_recovery':
            result = self.topology.inject_link_recovery('Node1', 'Node2')
            if result:
                self._recalculate_stp()
                self.logger.scenario_execution('link_recovery', 'success')
                self._log_response(f'/api/test/scenario/{scenario_name}', 200, 'POST')
                return jsonify({'status': 'success', 'message': 'Link recovery scenario executed'})
        elif scenario_name == 'node_failure':
            result = self.topology.inject_node_failure('Node3')
            if result:
                self._recalculate_stp()
                self.logger.scenario_execution('node_failure', 'success')
                self._log_response(f'/api/test/scenario/{scenario_name}', 200, 'POST')
                return jsonify({'status': 'success', 'message': 'Node failure scenario executed'})
        self.logger.scenario_execution(scenario_name, 'failed')
        self._log_response(f'/api/test/scenario/{scenario_name}', 400, 'POST')
        return jsonify({'status': 'error', 'message': 'Unknown scenario'}), 400

    def get_test_status(self):
        self._log_request('/api/test/status', 'GET')
        result = jsonify({
            'status': 'ready',
            'scenarios': ['link_failure', 'link_recovery', 'node_failure']
        })
        self._log_response('/api/test/status', 200, 'GET')
        return result

    def debug_status(self):
        self._log_request('/api/debug/status', 'GET')
        nodes = self.topology.get_all_nodes()
        links = self.topology.get_all_links()
        
        active_nodes = sum(1 for n in nodes if n.state.value == 'ACTIVE')
        failed_nodes = len(nodes) - active_nodes
        up_links = sum(1 for l in links if l.state.value == 'UP')
        down_links = sum(1 for l in links if l.state.value == 'DOWN')
        
        result = jsonify({
            'topology': {
                'total_nodes': len(nodes),
                'active_nodes': active_nodes,
                'failed_nodes': failed_nodes,
                'total_links': len(links),
                'up_links': up_links,
                'down_links': down_links,
                'spanning_tree_links': len(self.topology.spanning_tree_links)
            },
            'root_node': {
                'node_id': self.topology.root_node.id if self.topology.root_node else None,
                'node_name': self.topology.root_node.node_name if self.topology.root_node else None
            },
            'stp': self.stp_calculator.get_spanning_tree_info(),
            'timestamp': time.time()
        })
        self._log_response('/api/debug/status', 200, 'GET')
        return result

    def debug_node(self, node_id):
        self._log_request(f'/api/debug/nodes/{node_id}', 'GET')
        node = self.topology.get_node(node_id)
        if not node:
            self._log_response(f'/api/debug/nodes/{node_id}', 404, 'GET')
            return jsonify({'status': 'error', 'message': 'Node not found'}), 404
        
        connected_links = []
        for link in self.topology.get_all_links():
            nodes = link.get_connected_nodes()
            if node_id in nodes:
                other_node_id = nodes[0] if nodes[1] == node_id else nodes[1]
                other_node = self.topology.get_node(other_node_id)
                connected_links.append({
                    'link_id': link.link_id,
                    'state': link.state.value,
                    'connected_to': other_node.node_name if other_node else other_node_id,
                    'bandwidth': link.bandwidth,
                    'latency': link.latency,
                    'is_in_spanning_tree': link.link_id in self.topology.spanning_tree_links
                })
        
        result = jsonify({
            'node': node.to_dict(),
            'ports': {str(p.port_id): {
                'port_id': p.port_id,
                'state': p.state.value,
                'node_id': p.node_id
            } for p in node.ports.values()},
            'connected_links': connected_links,
            'is_root': node.is_root,
            'root_path_cost': node.root_path_cost,
            'parent_port': node.parent_port.port_id if node.parent_port else None
        })
        self._log_response(f'/api/debug/nodes/{node_id}', 200, 'GET')
        return result

    def debug_link(self, link_id):
        self._log_request(f'/api/debug/links/{link_id}', 'GET')
        link = self.topology.get_link(link_id)
        if not link:
            self._log_response(f'/api/debug/links/{link_id}', 404, 'GET')
            return jsonify({'status': 'error', 'message': 'Link not found'}), 404
        
        nodes = link.get_connected_nodes()
        node1 = self.topology.get_node(nodes[0]) if len(nodes) > 0 else None
        node2 = self.topology.get_node(nodes[1]) if len(nodes) > 1 else None
        
        result = jsonify({
            'link': link.to_dict(),
            'endpoints': {
                'node1': {
                    'node_id': nodes[0] if len(nodes) > 0 else None,
                    'node_name': node1.node_name if node1 else None,
                    'port_id': link.port1.port_id if link.port1 else None
                },
                'node2': {
                    'node_id': nodes[1] if len(nodes) > 1 else None,
                    'node_name': node2.node_name if node2 else None,
                    'port_id': link.port2.port_id if link.port2 else None
                }
            },
            'lacp': {
                'success_count': link.lacp_success_count,
                'fail_count': link.lacp_fail_count,
                'last_lacp_time': link.last_lacp_time
            },
            'is_in_spanning_tree': link_id in self.topology.spanning_tree_links,
            'created_at': link.created_at
        })
        self._log_response(f'/api/debug/links/{link_id}', 200, 'GET')
        return result

    def debug_logs(self):
        self._log_request('/api/debug/logs', 'GET')
        import os
        log_dir = 'logs'
        logs = []
        
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            lines = f.readlines()[-100:]
                            logs.append({
                                'filename': filename,
                                'size': os.path.getsize(filepath),
                                'last_100_lines': [line.strip() for line in lines]
                            })
                    except Exception as e:
                        logs.append({
                            'filename': filename,
                            'error': str(e)
                        })
        
        result = jsonify({
            'log_directory': os.path.abspath(log_dir),
            'logs': logs
        })
        self._log_response('/api/debug/logs', 200, 'GET')
        return result

    def _setup_4_node_full_mesh(self):
        self.topology = Topology()

        node1 = Node("Node1")
        node2 = Node("Node2")
        node3 = Node("Node3")
        node4 = Node("Node4")

        node1.add_port(1)
        node1.add_port(2)
        node1.add_port(3)
        node2.add_port(1)
        node2.add_port(2)
        node2.add_port(3)
        node3.add_port(1)
        node3.add_port(2)
        node3.add_port(3)
        node4.add_port(1)
        node4.add_port(2)
        node4.add_port(3)

        self.topology.add_node(node1)
        self.topology.add_node(node2)
        self.topology.add_node(node3)
        self.topology.add_node(node4)

        def connect(n1, n2, p1, p2):
            link = Link(n1.get_port(p1), n2.get_port(p2), 1000, 1)
            self.topology.add_link(link)

        connect(node1, node2, 1, 1)
        connect(node1, node3, 2, 1)
        connect(node1, node4, 3, 1)
        connect(node2, node3, 2, 2)
        connect(node2, node4, 3, 2)
        connect(node3, node4, 3, 3)

        self.stp_calculator = STPCalculator(self.topology)

    def _recalculate_stp(self):
        current_time = time.time()
        if current_time - self.last_topology_change < self.topology_change_cooldown:
            return
        self.last_topology_change = current_time
        self.stp_calculator.update_and_apply()

        root_name = self.topology.root_node.node_name if self.topology.root_node else 'None'
        link_count = len(self.topology.spanning_tree_links)
        self.logger.stp_recalculation(root_name, link_count)

    def run(self, host='0.0.0.0', port=5000, debug=False):
        self.logger.info(f"Starting server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
