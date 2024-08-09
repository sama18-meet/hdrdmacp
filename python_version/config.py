# config.py

# General Configurations
SERVER_IP = "192.168.1.1"  # Server IP address (used in TCP/IP applications)
CLIENT_IP = "192.168.1.2"  # Client IP address (used in TCP/IP applications)
SERVER_PORT = 5000         # Common port for both RoCE and TCP/IP applications
FILE_PATH = "data/testfile.dat"  # Path to the file to be transferred
CHUNK_SIZE = 1024 * 1024   # 1MB chunks for file transfer

# RoCE Configurations
ROCE_DEVICE_NAME = "mlx5_0"  # Name of the RDMA device

# Performance Monitoring
MONITOR_INTERVAL = 1  # Interval (seconds) for performance monitoring
