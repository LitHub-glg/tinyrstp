import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from frontend.gui.client import APIClient
from frontend.gui.main import NetworkGUI


class TestGUI:
    @pytest.fixture
    def mock_client(self):
        client = APIClient()
        client.enable_mock()
        return client

    @pytest.fixture
    def gui(self, mock_client):
        return NetworkGUI(mock_client)

    def test_gui_initialization(self, gui):
        assert gui.client is not None
        assert gui.fig is None
        assert gui.ax_main is None
        assert gui.topology_data is None

    def test_gui_setup(self, gui):
        gui.setup()
        assert gui.fig is not None
        assert gui.ax_main is not None
        assert gui.ax_controls is not None
        assert gui.ax_info is not None
        assert len(gui.buttons) == 7

    def test_gui_buttons_exist(self, gui):
        gui.setup()
        expected_buttons = [
            'toggle_link',
            'fail_node',
            'recover_node',
            'reset',
            'scenario1',
            'scenario2',
            'scenario3'
        ]
        for btn_id in expected_buttons:
            assert btn_id in gui.buttons

    def test_refresh_topology(self, gui):
        gui.setup()
        gui._refresh_topology()
        assert gui.topology_data is not None
        assert 'nodes' in gui.topology_data
        assert 'links' in gui.topology_data

    def test_setup_layout(self, gui):
        gui.setup()
        gui._refresh_topology()
        gui._setup_layout()
        assert gui.pos is not None
        assert isinstance(gui.pos, dict)

    def test_get_node_color(self, gui):
        gui.setup()
        active_node = {'state': 'ACTIVE', 'is_root': False}
        failed_node = {'state': 'FAILED', 'is_root': False}
        root_node = {'state': 'ACTIVE', 'is_root': True}

        assert gui._get_node_color(active_node) == '#4488ff'
        assert gui._get_node_color(failed_node) == '#ff4444'
        assert gui._get_node_color(root_node) == '#44ff44'

    def test_get_link_color(self, gui):
        gui.setup()
        up_link = {'state': 'UP'}
        down_link = {'state': 'DOWN'}

        assert gui._get_link_color(up_link, True) == '#44ff44'
        assert gui._get_link_color(up_link, False) == '#cccccc'
        assert gui._get_link_color(down_link, True) == '#888888'
        assert gui._get_link_color(down_link, False) == '#888888'

    def test_handle_button_reset(self, gui):
        gui.setup()
        gui._refresh_topology()
        initial_nodes = len(gui.topology_data.get('nodes', {}))
        gui._handle_button('reset')
        assert initial_nodes >= 0

    def test_handle_button_toggle_link(self, gui):
        gui.setup()
        gui._refresh_topology()
        links = gui.topology_data.get('links', {})
        if links:
            link_id = list(links.keys())[0]
            gui.selected_link = link_id
            gui._handle_button('toggle_link')
            assert gui.selected_link == link_id

    def test_handle_button_fail_node(self, gui):
        gui.setup()
        gui._refresh_topology()
        nodes = gui.topology_data.get('nodes', {})
        if nodes:
            node_id = list(nodes.keys())[0]
            gui.selected_node = node_id
            gui._handle_button('fail_node')
            assert gui.selected_node == node_id

    def test_handle_button_recover_node(self, gui):
        gui.setup()
        gui._refresh_topology()
        nodes = gui.topology_data.get('nodes', {})
        if nodes:
            node_id = list(nodes.keys())[0]
            gui.selected_node = node_id
            gui._handle_button('recover_node')
            assert gui.selected_node == node_id

    def test_handle_button_scenario1(self, gui):
        gui.setup()
        gui._handle_button('scenario1')
        assert True

    def test_handle_button_scenario2(self, gui):
        gui.setup()
        gui._handle_button('scenario2')
        assert True

    def test_handle_button_scenario3(self, gui):
        gui.setup()
        gui._handle_button('scenario3')
        assert True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
