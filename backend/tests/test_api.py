import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.api.app import NetworkAPI


class TestAPI:
    @pytest.fixture
    def api(self):
        return NetworkAPI()

    @pytest.fixture
    def client(self, api):
        return api.app.test_client()

    def test_get_topology(self, client):
        response = client.get('/api/topology')
        assert response.status_code == 200
        data = response.get_json()
        assert 'nodes' in data
        assert 'links' in data
        assert 'spanning_tree' in data
        assert 'root_node' in data

    def test_get_nodes(self, client):
        response = client.get('/api/topology/nodes')
        assert response.status_code == 200
        data = response.get_json()
        assert 'nodes' in data
        assert isinstance(data['nodes'], list)
        assert len(data['nodes']) == 4

    def test_get_links(self, client):
        response = client.get('/api/topology/links')
        assert response.status_code == 200
        data = response.get_json()
        assert 'links' in data
        assert isinstance(data['links'], list)
        assert len(data['links']) == 6

    def test_get_spanning_tree(self, client):
        response = client.get('/api/topology/spanning-tree')
        assert response.status_code == 200
        data = response.get_json()
        assert 'root_node' in data
        assert 'link_count' in data
        assert 'node_count' in data
        assert 'links' in data

    def test_reset_topology(self, client):
        response = client.post('/api/topology/reset')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_fail_node(self, client):
        response = client.get('/api/topology/nodes')
        nodes = response.get_json()['nodes']
        if nodes:
            node_id = nodes[0]['node_id']
            response = client.post(f'/api/nodes/{node_id}/fail')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'

    def test_recover_node(self, client):
        response = client.get('/api/topology/nodes')
        nodes = response.get_json()['nodes']
        if nodes:
            node_id = nodes[0]['node_id']
            response = client.post(f'/api/nodes/{node_id}/fail')
            response = client.post(f'/api/nodes/{node_id}/recover')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'

    def test_toggle_link(self, client):
        response = client.get('/api/topology/links')
        links = response.get_json()['links']
        if links:
            link_id = links[0]['link_id']
            response = client.post(f'/api/links/{link_id}/toggle')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'

    def test_link_up(self, client):
        response = client.get('/api/topology/links')
        links = response.get_json()['links']
        if links:
            link_id = links[0]['link_id']
            response = client.post(f'/api/links/{link_id}/up')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'

    def test_link_down(self, client):
        response = client.get('/api/topology/links')
        links = response.get_json()['links']
        if links:
            link_id = links[0]['link_id']
            response = client.post(f'/api/links/{link_id}/down')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'

    def test_run_scenario_link_failure(self, client):
        response = client.post('/api/test/scenario/link_failure')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_run_scenario_link_recovery(self, client):
        response = client.post('/api/test/scenario/link_recovery')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_run_scenario_node_failure(self, client):
        response = client.post('/api/test/scenario/node_failure')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_get_test_status(self, client):
        response = client.get('/api/test/status')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert 'scenarios' in data
        assert isinstance(data['scenarios'], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
