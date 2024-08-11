# roce_server.py

import pyverbs.device as d
from pyverbs.pd import PD
from pyverbs.cq import CQ
from pyverbs.mr import MR
from pyverbs.qp import QP, QPCap, QPInitAttr
import pyverbs.enums as e
from utils import log, write_file
from config import SERVER_IP, SERVER_PORT, ROCE_DEVICE_NAME, FILE_PATH, CHUNK_SIZE

def main():
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
    mr = MR(pd, CHUNK_SIZE, e.IBV_ACCESS_LOCAL_WRITE)  # Register the memory region


    # Create Queue Pair (QP)
    log("Creating Queue Pair (QP)...")
    cap = QPCap(max_send_wr=1, max_recv_wr=1, max_send_sge=1, max_recv_sge=1)
    qp_init_attr = QPInitAttr(cap=cap, qp_type=e.IBV_QPT_RC, scq=cq, rcq=cq)
    qp = QP(pd, qp_init_attr)

    # Transition QP to RTR
    log("Transitioning QP to RTR...")
    rtr_attr = QPAttr()
    rtr_attr.qp_state = e.IBV_QPS_RTR
    rtr_attr.path_mtu = e.IBV_MTU_1024
    rtr_attr.dest_qp_num = 0  # Set this to the destination QP number
    rtr_attr.rq_psn = 0
    rtr_attr.max_dest_rd_atomic = 1
    rtr_attr.min_rnr_timer = 12
    qp.to_rtr(rtr_attr)

    # Post Receive Work Request
    log("Posting Receive Work Request...")
    qp.post_recv(mr)

    # Wait for incoming connection and receive data
    log("Waiting for incoming data...")
    wc = cq.poll()
    if wc and wc[0].status == e.IBV_WC_SUCCESS:
        data_length = wc[0].byte_len
        received_data = bytes(mr.read(0, data_length))
        log(f"Received {data_length} bytes of data.")

        # Write received data to file
        if received_data:
            write_file(FILE_PATH, received_data)
            log(f"File received successfully and saved to {FILE_PATH}.")
    else:
        log("No data received or error occurred.")

    # Clean up RDMA resources
    log("Cleaning up RDMA resources...")
    qp.close()
    cq.close()
    pd.close()
    ctx.close()
    log("RDMA resources cleaned up.")

if __name__ == "__main__":
    main()
