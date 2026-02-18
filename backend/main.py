import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api.app import NetworkAPI
from backend.utils.logger import get_logger


if __name__ == '__main__':
    logger = get_logger(log_dir='logs')
    logger.startup('BackendServer')

    api = NetworkAPI()
    print("Backend API: http://localhost:5002")
    print(f"Log file: {logger.get_log_file_path()}")

    api.run(host='0.0.0.0', port=5002, debug=False)
