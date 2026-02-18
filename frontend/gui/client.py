import requests
from typing import Dict, Optional


class APIClient:
    def __init__(self, base_url: str = 'http://localhost:5002'):
        self.base_url = base_url
        self.mock_mode = False
        self.mock_data = {}

    def enable_mock(self):
        self.mock_mode = True
        self.mock_data = {
            'topology': {
                'nodes': {},
                'links': {},
                'spanning_tree': [],
                'root_node': None
            },
            'spanning_tree': {
                'root_node': None,
                'link_count': 0,
                'node_count': 0,
                'links': []
            }
        }

    def disable_mock(self):
        self.mock_mode = False

    def get_topology(self) -> Dict:
        if self.mock_mode:
            return self.mock_data.get('topology', {})
        response = requests.get(f'{self.base_url}/api/topology')
        response.raise_for_status()
        return response.json()

    def reset_topology(self) -> Dict:
        if self.mock_mode:
            return {'status': 'success', 'message': 'Topology reset (mock)'}
        response = requests.post(f'{self.base_url}/api/topology/reset')
        response.raise_for_status()
        return response.json()

    def get_nodes(self) -> Dict:
        if self.mock_mode:
            return {'nodes': list(self.mock_data.get('topology', {}).get('nodes', {}).values())}
        response = requests.get(f'{self.base_url}/api/topology/nodes')
        response.raise_for_status()
        return response.json()

    def get_links(self) -> Dict:
        if self.mock_mode:
            return {'links': list(self.mock_data.get('topology', {}).get('links', {}).values())}
        response = requests.get(f'{self.base_url}/api/topology/links')
        response.raise_for_status()
        return response.json()

    def get_spanning_tree(self) -> Dict:
        if self.mock_mode:
            return self.mock_data.get('spanning_tree', {})
        response = requests.get(f'{self.base_url}/api/topology/spanning-tree')
        response.raise_for_status()
        return response.json()

    def fail_node(self, node_id: str) -> Dict:
        if self.mock_mode:
            return {'status': 'success', 'message': f'Node {node_id} failed (mock)'}
        response = requests.post(f'{self.base_url}/api/nodes/{node_id}/fail')
        response.raise_for_status()
        return response.json()

    def recover_node(self, node_id: str) -> Dict:
        if self.mock_mode:
            return {'status': 'success', 'message': f'Node {node_id} recovered (mock)'}
        response = requests.post(f'{self.base_url}/api/nodes/{node_id}/recover')
        response.raise_for_status()
        return response.json()

    def toggle_link(self, link_id: str) -> Dict:
        if self.mock_mode:
            return {'status': 'success', 'message': f'Link {link_id} toggled (mock)'}
        response = requests.post(f'{self.base_url}/api/links/{link_id}/toggle')
        response.raise_for_status()
        return response.json()

    def link_up(self, link_id: str) -> Dict:
        if self.mock_mode:
            return {'status': 'success', 'message': f'Link {link_id} up (mock)'}
        response = requests.post(f'{self.base_url}/api/links/{link_id}/up')
        response.raise_for_status()
        return response.json()

    def link_down(self, link_id: str) -> Dict:
        if self.mock_mode:
            return {'status': 'success', 'message': f'Link {link_id} down (mock)'}
        response = requests.post(f'{self.base_url}/api/links/{link_id}/down')
        response.raise_for_status()
        return response.json()

    def run_scenario(self, scenario_name: str) -> Dict:
        if self.mock_mode:
            return {'status': 'success', 'message': f'Scenario {scenario_name} executed (mock)'}
        response = requests.post(f'{self.base_url}/api/test/scenario/{scenario_name}')
        response.raise_for_status()
        return response.json()

    def get_test_status(self) -> Dict:
        if self.mock_mode:
            return {'status': 'ready', 'scenarios': ['link_failure', 'link_recovery', 'node_failure']}
        response = requests.get(f'{self.base_url}/api/test/status')
        response.raise_for_status()
        return response.json()
