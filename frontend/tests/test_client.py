import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from frontend.gui.client import APIClient


class TestAPIClient:
    def setup_method(self):
        self.client = APIClient()
        self.client.enable_mock()

    def test_get_topology(self):
        result = self.client.get_topology()
        assert 'nodes' in result
        assert 'links' in result
        assert 'spanning_tree' in result

    def test_reset_topology(self):
        result = self.client.reset_topology()
        assert 'status' in result
        assert result['status'] == 'success'

    def test_get_nodes(self):
        result = self.client.get_nodes()
        assert 'nodes' in result
        assert isinstance(result['nodes'], list)

    def test_get_links(self):
        result = self.client.get_links()
        assert 'links' in result
        assert isinstance(result['links'], list)

    def test_get_spanning_tree(self):
        result = self.client.get_spanning_tree()
        assert 'root_node' in result
        assert 'link_count' in result
        assert 'node_count' in result

    def test_fail_node(self):
        result = self.client.fail_node('test_node_id')
        assert 'status' in result
        assert result['status'] == 'success'

    def test_recover_node(self):
        result = self.client.recover_node('test_node_id')
        assert 'status' in result
        assert result['status'] == 'success'

    def test_toggle_link(self):
        result = self.client.toggle_link('test_link_id')
        assert 'status' in result
        assert result['status'] == 'success'

    def test_link_up(self):
        result = self.client.link_up('test_link_id')
        assert 'status' in result
        assert result['status'] == 'success'

    def test_link_down(self):
        result = self.client.link_down('test_link_id')
        assert 'status' in result
        assert result['status'] == 'success'

    def test_run_scenario(self):
        result = self.client.run_scenario('link_failure')
        assert 'status' in result
        assert result['status'] == 'success'

    def test_get_test_status(self):
        result = self.client.get_test_status()
        assert 'status' in result
        assert 'scenarios' in result
        assert isinstance(result['scenarios'], list)


class TestAutomationScenarios:
    def setup_method(self):
        self.client = APIClient()
        self.client.enable_mock()

    def test_scenario_link_failure(self):
        result = self.client.run_scenario('link_failure')
        assert result['status'] == 'success'
        assert 'message' in result

    def test_scenario_link_recovery(self):
        result = self.client.run_scenario('link_recovery')
        assert result['status'] == 'success'
        assert 'message' in result

    def test_scenario_node_failure(self):
        result = self.client.run_scenario('node_failure')
        assert result['status'] == 'success'
        assert 'message' in result

    def test_full_automation_flow(self):
        self.client.reset_topology()
        result = self.client.get_topology()
        assert 'nodes' in result

        result = self.client.run_scenario('link_failure')
        assert result['status'] == 'success'

        result = self.client.run_scenario('link_recovery')
        assert result['status'] == 'success'

        result = self.client.run_scenario('node_failure')
        assert result['status'] == 'success'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
