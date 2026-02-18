import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.gui.client import APIClient
from frontend.gui.main import NetworkGUI
from frontend.gui.logger import get_gui_logger


if __name__ == '__main__':
    logger = get_gui_logger(log_dir='logs')
    logger.info('Frontend starting')

    client = APIClient(base_url='http://localhost:5002')
    gui = NetworkGUI(client)

    print("GUI: http://localhost:5002 (backend required)")
    print(f"Log: {logger.get_log_file_path()}")

    gui.run()
