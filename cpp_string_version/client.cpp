#include <infiniband/verbs.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <string.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#include <memory>
#include <random>
#include "rdma_context.h"


void parse_arguments(int argc, char **argv, uint16_t *tcp_port)
{
    if (argc < 2) {
        printf("usage: %s <tcp_port>\n", argv[0]);
        exit(1);
    }
    *tcp_port = atoi(argv[1]);
}


int main(int argc, char *argv[]) {
    uint16_t tcp_port;

    parse_arguments(argc, argv, &tcp_port);
    if (!tcp_port) {
        printf("usage: %s <tcp port>\n", argv[0]);
        exit(1);
    }

    auto client = std::make_unique<rdma_client_context>(tcp_port);
    
    char *file_content = "hello rdma world!";
    bool file_sent = client->send_file(1, file_content);

    return 0;
}
