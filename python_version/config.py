# config.py

# General Configurations
SERVER_IP = "5.5.5.4"  # Server IP address (used in TCP/IP applications)
CLIENT_IP = "5.5.5.1"  # Client IP address (used in TCP/IP applications)
SERVER_PORT = 5000         # Common port for both RoCE and TCP/IP applications
FILE_PATH = "/root/RDMA_proj/hdrdmacp_forked/python_version/file2"  # Path to the file to be transferred
CHUNK_SIZE = 1024 * 1024   # 1MB chunks for file transfer

# RoCE Configurations
ROCE_DEVICE_NAME = "mlx5_1"  # Name of the RDMA device

# Performance Monitoring
MONITOR_INTERVAL = 1  # Interval (seconds) for performance monitoring
