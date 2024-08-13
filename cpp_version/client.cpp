#include <infiniband/verbs.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <string.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#include <memory>
#include <random>
#include <fstream>

#include <sys/stat.h>
#include <unistd.h>
#include <string>
#include "rdma_context.h"



std::string parse_arguments(int argc, char **argv, uint16_t *tcp_port)
{
    if (argc < 3) {
        printf("usage: %s <tcp_port> <file_name>\n", argv[0]);
        exit(1);
    }
    *tcp_port = atoi(argv[1]);
    std::string filename(argv[2]);
    return filename;
}


int main(int argc, char *argv[]) {
    uint16_t tcp_port;

    std::string filename = parse_arguments(argc, argv, &tcp_port);

    if (!tcp_port) {
        printf("usage: %s <tcp port>\n", argv[0]);
        exit(1);
    }

    std::ifstream f(filename.c_str());
    if (!f.good()) { // file exists
        printf("file doesnot exist\n");
    }

    auto client = std::make_unique<rdma_client_context>(tcp_port);
    
    bool file_sent = client->send_file(1, filename);

    return 0;
}
