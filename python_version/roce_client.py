# roce_client.py
import pyverbs.device as d
from pyverbs.pd import PD
from pyverbs.cq import CQ
from pyverbs.mr import MR
from pyverbs.qp import QP, QPCap, QPInitAttr, QPAttr
import pyverbs.enums as e
from utils import log, read_file, file_exists, get_file_size
from config import SERVER_IP, SERVER_PORT, ROCE_DEVICE_NAME, FILE_PATH, CHUNK_SIZE
import socket
import json
import struct

def send_data(sock, data):
    serialized_data = json.dumps(data).encode('utf-8')
    sock.sendall(struct.pack('!I', len(serialized_data)))
    sock.sendall(serialized_data)

def receive_data(sock):
    data_len = struct.unpack('!I', sock.recv(4))[0]
    return json.loads(sock.recv(data_len).decode('utf-8'))

def main():
    # Check if the file exists
    if not file_exists(FILE_PATH):
        log(f"File {FILE_PATH} does not exist.")
        return
    
    # Initialize RDMA context
    log("Initializing RDMA context...")
    ctx = d.Context(name=ROCE_DEVICE_NAME)
    
    # Allocate Protection Domain (PD)
    log("Allocating Protection Domain (PD)...")
    pd = PD(ctx)
    
    # Create Completion Queue (CQ)
    log("Creating Completion Queue (CQ)...")
    cq = CQ(ctx, 10)
    
    # Register Memory Region (MR)
    log("Registering Memory Region (MR)...")
    buffer = bytearray(CHUNK_SIZE)
    mr = MR(pd, buffer, e.IBV_ACCESS_LOCAL_WRITE)
    
    # Create Queue Pair (QP)
    log("Creating Queue Pair (QP)...")
    cap = QPCap(max_send_wr=1, max_recv_wr=1, max_send_sge=1, max_recv_sge=1)
    qp_init_attr = QPInitAttr(cap=cap, qp_type=e.IBV_QPT_RC, scq=cq, rcq=cq)
    qp = QP(pd, qp_init_attr)
    
    # Get local QP number and LID
    local_qp_num = qp.qp_num
    local_lid = ctx.query_port(1).lid
    
    # Set up TCP socket for exchanging information
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        
        # Receive remote QP info
        remote_info = receive_data(s)
        remote_qp_num = remote_info["qp_num"]
        remote_lid = remote_info["lid"]
        
        # Send local QP info
        send_data(s, {"qp_num": local_qp_num, "lid": local_lid})
    
    # Transition QP to INIT
    log("Transitioning QP to INIT...")
    init_attr = QPAttr()
    init_attr.qp_state = e.IBV_QPS_INIT
    init_attr.port_num = 1
    init_attr.pkey_index = 0
    init_attr.qp_access_flags = e.IBV_ACCESS_LOCAL_WRITE | e.IBV_ACCESS_REMOTE_READ | e.IBV_ACCESS_REMOTE_WRITE
    qp.to_init(init_attr)
    
    # Transition QP to RTR
    log("Transitioning QP to RTR...")
    rtr_attr = QPAttr()
    rtr_attr.qp_state = e.IBV_QPS_RTR
    rtr_attr.path_mtu = e.IBV_MTU_1024
    rtr_attr.dest_qp_num = remote_qp_num
    rtr_attr.rq_psn = 0
    rtr_attr.max_dest_rd_atomic = 1
    rtr_attr.min_rnr_timer = 12
    rtr_attr.ah_attr.is_global = 0
    rtr_attr.ah_attr.dlid = remote_lid
    rtr_attr.ah_attr.sl = 0
    rtr_attr.ah_attr.src_path_bits = 0
    rtr_attr.ah_attr.port_num = 1
    qp.to_rtr(rtr_attr)
    
    # Transition QP to RTS
    log("Transitioning QP to RTS...")
    rts_attr = QPAttr()
    rts_attr.qp_state = e.IBV_QPS_RTS
    rts_attr.timeout = 14
    rts_attr.retry_cnt = 7
    rts_attr.rnr_retry = 7
    rts_attr.sq_psn = 0
    rts_attr.max_rd_atomic = 1
    qp.to_rts(rts_attr)
    
    # Send file data
    log(f"Sending file {FILE_PATH}...")
    total_size = get_file_size(FILE_PATH)
    total_sent = 0
    for chunk in read_file(FILE_PATH, CHUNK_SIZE):
        mr.write(0, chunk)  # Write chunk to the memory region
        log(f"Posting send request for {len(chunk)} bytes.")
        qp.post_send(mr)
        # Poll for completion
        wc = cq.poll()
        if wc and wc[0].status == e.IBV_WC_SUCCESS:
            sent_bytes = len(chunk)
            total_sent += sent_bytes
            log(f"Sent {sent_bytes} bytes. Total sent: {total_sent}/{total_size} bytes.")
        else:
            log("Send request failed or no completion detected.")
            break
    log("File sent successfully.")
    
    # Clean up RDMA resources
    log("Cleaning up RDMA resources...")
    qp.close()
    cq.close()
    pd.close()
    ctx.close()
    log("RDMA resources cleaned up.")

if __name__ == "__main__":
    main()
