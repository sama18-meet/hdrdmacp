# roce_client.py

import pyverbs.device as d
from pyverbs.pd import PD
from pyverbs.cq import CQ
from pyverbs.mr import MR
from pyverbs.qp import QP, QPCap, QPInitAttr
from pyverbs.addr import AH, AHAttr
import pyverbs.enums as e
from utils import log, read_file, file_exists, get_file_size
from config import SERVER_IP, ROCE_DEVICE_NAME, FILE_PATH, CHUNK_SIZE


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

    # Transition QP to INIT, RTR, and RTS states
    log("Transitioning QP to INIT, RTR, and RTS states...")
    qp.to_init()
    qp.to_rtr()
    qp.to_rts()

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
