import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import matplotlib

backends_to_try = ['MacOSX', 'TkAgg', 'Qt5Agg', 'QtAgg']
for backend in backends_to_try:
    try:
        matplotlib.use(backend, force=True)
        break
    except Exception:
        continue

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.widgets as widgets
import networkx as nx
from typing import Dict, Optional
from frontend.gui.client import APIClient
from frontend.gui.logger import get_gui_logger

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class NetworkGUI:
    def __init__(self, client: APIClient):
        self.client = client
        self.logger = get_gui_logger(log_dir='logs')
        self.fig = None
        self.ax_main = None
        self.ax_controls = None
        self.ax_info = None
        self.ax_legend = None
        self.pos = None
        self.selected_link = None
        self.selected_node = None
        self.buttons = {}
        self.topology_data = None

    def setup(self):
        self.logger.gui_event('setup_start')
        self.fig = plt.figure(figsize=(14, 10))
        gs = self.fig.add_gridspec(2, 2, hspace=0.15, wspace=0.15,
                                    height_ratios=[2, 1], width_ratios=[2, 1])

        self.ax_main = self.fig.add_subplot(gs[0, 0])
        self.ax_legend = self.fig.add_subplot(gs[0, 1])
        self.ax_controls = self.fig.add_subplot(gs[1, 0])
        self.ax_info = self.fig.add_subplot(gs[1, 1])

        self.ax_legend.axis('off')
        self.ax_controls.axis('off')
        self.ax_info.axis('off')

        self._create_buttons()
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        self.logger.gui_event('setup_complete')

    def _create_buttons(self):
        button_width = 0.03
        button_height = 0.015
        button_x_start = 0.05
        button_y_start = 0.28
        button_spacing_x = 0.035
        button_spacing_y = 0.022

        controls = [
            ('toggle_link', 'Toggle', '#ffaa44'),
            ('fail_node', 'Fail', '#ff4444'),
            ('recover_node', 'Recover', '#44ff44'),
            ('reset', 'Reset', '#4488ff'),
            ('scenario1', 'S1:Link', '#ff8844'),
            ('scenario2', 'S2:LinkR', '#88ff44'),
            ('scenario3', 'S3:Node', '#ff4488'),
        ]

        current_x = button_x_start
        current_y = button_y_start

        for i, (btn_id, label, color) in enumerate(controls):
            ax_btn = self.fig.add_axes([current_x, current_y, button_width, button_height])
            btn = widgets.Button(ax_btn, label, color=color)
            btn.label.set_fontsize(6)
            btn.on_clicked(self._get_button_handler(btn_id))
            self.buttons[btn_id] = btn
            current_x += button_spacing_x
            if i == 3:
                current_x = button_x_start
                current_y -= button_spacing_y

    def _get_button_handler(self, btn_id: str):
        def handler(event):
            self._handle_button(btn_id)
        return handler

    def _handle_button(self, btn_id: str):
        self.logger.user_action('button_click', {'button': btn_id})

        if btn_id == 'toggle_link' and self.selected_link:
            result = self.client.toggle_link(self.selected_link)
            self.logger.api_response('POST', f'/api/links/{self.selected_link}/toggle', result.get('status', 'unknown'))
            self._refresh_topology()
        elif btn_id == 'fail_node' and self.selected_node:
            result = self.client.fail_node(self.selected_node)
            self.logger.api_response('POST', f'/api/nodes/{self.selected_node}/fail', result.get('status', 'unknown'))
            self._refresh_topology()
        elif btn_id == 'recover_node' and self.selected_node:
            result = self.client.recover_node(self.selected_node)
            self.logger.api_response('POST', f'/api/nodes/{self.selected_node}/recover', result.get('status', 'unknown'))
            self._refresh_topology()
        elif btn_id == 'reset':
            result = self.client.reset_topology()
            self.logger.api_response('POST', '/api/topology/reset', result.get('status', 'unknown'))
            self._refresh_topology()
        elif btn_id == 'scenario1':
            result = self.client.run_scenario('link_failure')
            self.logger.api_response('POST', '/api/test/scenario/link_failure', result.get('status', 'unknown'))
            self._refresh_topology()
        elif btn_id == 'scenario2':
            result = self.client.run_scenario('link_recovery')
            self.logger.api_response('POST', '/api/test/scenario/link_recovery', result.get('status', 'unknown'))
            self._refresh_topology()
        elif btn_id == 'scenario3':
            result = self.client.run_scenario('node_failure')
            self.logger.api_response('POST', '/api/test/scenario/node_failure', result.get('status', 'unknown'))
            self._refresh_topology()
        self.draw()

    def _on_click(self, event):
        if event.inaxes != self.ax_main:
            return
        if event.button != 1:
            return

        x, y = event.xdata, event.ydata
        tolerance = 0.15

        self.selected_link = None
        for link_data in self.topology_data.get('links', {}).values():
            link_id = link_data.get('link_id', '')
            nodes = link_data.get('nodes', [])
            if len(nodes) < 2:
                continue
            n1_id, n2_id = nodes[0], nodes[1]
            if n1_id not in self.pos or n2_id not in self.pos:
                continue
            x1, y1 = self.pos[n1_id]
            x2, y2 = self.pos[n2_id]
            dist = self._point_to_line_dist(x, y, x1, y1, x2, y2)
            if dist < tolerance:
                self.selected_link = link_id
                break

        self.selected_node = None
        for node_id, node_data in self.topology_data.get('nodes', {}).items():
            if node_id not in self.pos:
                continue
            nx_pos, ny_pos = self.pos[node_id]
            dist = ((x - nx_pos) ** 2 + (y - ny_pos) ** 2) ** 0.5
            if dist < 0.25:
                self.selected_node = node_id
                break

        if self.selected_node or self.selected_link:
            self.logger.gui_event('selection', {'node': self.selected_node, 'link': self.selected_link})

        self.draw()

    def _point_to_line_dist(self, px, py, x1, y1, x2, y2):
        line_len = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if line_len == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_len ** 2)))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        return ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5

    def _refresh_topology(self):
        self.logger.api_call('GET', '/api/topology')
        self.topology_data = self.client.get_topology()
        self._setup_layout()
        self.logger.api_response('GET', '/api/topology', 'success')

    def _setup_layout(self):
        nodes = self.topology_data.get('nodes', {})
        positions = {}

        layout_4 = {
            'Node1': (-1, 1),
            'Node2': (1, 1),
            'Node3': (-1, -1),
            'Node4': (1, -1)
        }

        for node_id, node_data in nodes.items():
            node_name = node_data.get('node_name', '')
            if node_name in layout_4:
                positions[node_id] = layout_4[node_name]

        self.pos = positions

    def _get_node_color(self, node_data: dict) -> str:
        state = node_data.get('state', '')
        is_root = node_data.get('is_root', False)
        if state == 'FAILED':
            return '#ff4444'
        if is_root:
            return '#44ff44'
        return '#4488ff'

    def _get_link_color(self, link_data: dict, is_st: bool) -> str:
        state = link_data.get('state', '')
        if state == 'DOWN':
            return '#888888'
        if is_st:
            return '#44ff44'
        return '#cccccc'

    def draw(self):
        self.ax_main.clear()

        G = nx.Graph()
        node_labels = {}
        node_colors = []
        node_sizes = []

        for node_id, node_data in self.topology_data.get('nodes', {}).items():
            G.add_node(node_id)
            node_name = node_data.get('node_name', '')
            state = "✓" if node_data.get('state') == 'ACTIVE' else "✗"
            root = " (Root)" if node_data.get('is_root') else ""
            node_labels[node_id] = f"{node_name}\n{state}{root}"
            node_colors.append(self._get_node_color(node_data))
            node_sizes.append(4500 if self.selected_node == node_id else 3500)

        edge_colors = []
        edge_widths = []
        st_links = set(self.topology_data.get('spanning_tree', []))

        for link_id, link_data in self.topology_data.get('links', {}).items():
            nodes = link_data.get('nodes', [])
            if len(nodes) < 2:
                continue
            n1_id, n2_id = nodes[0], nodes[1]
            G.add_edge(n1_id, n2_id)
            is_st = link_id in st_links
            base_color = self._get_link_color(link_data, is_st)
            if self.selected_link == link_id:
                edge_colors.append('#ffff00')
            else:
                edge_colors.append(base_color)
            edge_widths.append(6 if self.selected_link == link_id else (4 if is_st else 2))

        nx.draw_networkx_nodes(G, self.pos, ax=self.ax_main, node_color=node_colors,
                               node_size=node_sizes, edgecolors='black', linewidths=2)
        nx.draw_networkx_edges(G, self.pos, ax=self.ax_main, edge_color=edge_colors,
                               width=edge_widths)
        nx.draw_networkx_labels(G, self.pos, node_labels, ax=self.ax_main,
                                font_size=12, font_weight='bold')

        self._draw_legend()
        self._update_info()

        self.ax_main.set_title("Dynamic Self-Healing Loop-Free Network", fontsize=14, fontweight='bold')
        self.ax_main.axis('off')

        plt.draw()

    def _draw_legend(self):
        self.ax_legend.clear()
        self.ax_legend.axis('off')

        legend_elements = [
            mpatches.Patch(color='#4488ff', label='Normal Node'),
            mpatches.Patch(color='#44ff44', label='Root Node'),
            mpatches.Patch(color='#ff4444', label='Failed Node'),
            mpatches.Patch(color='#44ff44', label='Spanning Tree Link'),
            mpatches.Patch(color='#cccccc', label='Backup Link'),
            mpatches.Patch(color='#888888', label='Failed Link'),
            mpatches.Patch(color='#ffff00', label='Selected Item')
        ]
        self.ax_legend.legend(handles=legend_elements, loc='center',
                              fontsize=10, title='Legend')

    def _update_info(self):
        self.ax_info.clear()
        self.ax_info.axis('off')

        info_text = "=" * 25 + "\n"
        info_text += "    Information Panel\n"
        info_text += "=" * 25 + "\n\n"

        if self.selected_node:
            node_data = self.topology_data.get('nodes', {}).get(self.selected_node, {})
            info_text += f"[Selected Node]\n"
            info_text += f"  Name: {node_data.get('node_name', '?')}\n"
            info_text += f"  State: {node_data.get('state', '?')}\n"
            info_text += f"  Root: {'Yes' if node_data.get('is_root') else 'No'}\n\n"

        if self.selected_link:
            link_data = self.topology_data.get('links', {}).get(self.selected_link, {})
            nodes = link_data.get('nodes', [])
            if len(nodes) >= 2:
                n1_data = self.topology_data.get('nodes', {}).get(nodes[0], {})
                n2_data = self.topology_data.get('nodes', {}).get(nodes[1], {})
                info_text += f"[Selected Link]\n"
                info_text += f"  {n1_data.get('node_name', '?')} <-> {n2_data.get('node_name', '?')}\n"
                info_text += f"  State: {link_data.get('state', '?')}\n"
                info_text += f"  BW: {link_data.get('bandwidth', 0)} Mbps\n"
                is_st = self.selected_link in self.topology_data.get('spanning_tree', [])
                info_text += f"  ST: {'Yes' if is_st else 'No'}\n\n"

        info_text += "=" * 25 + "\n"
        info_text += "    Instructions\n"
        info_text += "=" * 25 + "\n"
        info_text += "• Click node/link to select\n"
        info_text += "• Yellow = selected\n"

        self.ax_info.text(0.05, 0.95, info_text,
                         transform=self.ax_info.transAxes,
                         verticalalignment='top',
                         fontsize=9,
                         family='monospace')

    def run(self):
        self.logger.info('GUI starting')
        self.setup()
        self._refresh_topology()
        self.draw()
        print(f"GUI started. Log: {self.logger.get_log_file_path()}")
        plt.show()
