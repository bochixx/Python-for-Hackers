import socket
import sys
import argparse
import threading
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(
        description="Networking tool")
    
    parser.add_argument(
        "-l", "--listen", 
        action="store_true", 
        help="listen on [host]:[port] for incoming connections")
    
    parser.add_argument(
        "-e", "--execute",
        metavar="FILE", 
        help="execute the given file upon receiving a connection")
    
    parser.add_argument(
        "-c", "--command", 
        action="store_true", 
        help="initialize a command shell")
    
    parser.add_argument(
        "-u", "--upload", 
        metavar="DEST", 
        help="upon receiving connection upload a file and write to [dest]")
    
    parser.add_argument(
        "-t", "--target", 
        metavar="TARGET", 
        help="target host IP")
    
    parser.add_argument(
        "-p", "--port", 
        type=int,
        metavar="PORT", 
        help="target port")
    
    return parser, parser.parse_args()


def client_sender(buffer, target, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connecting to the taget host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer.encode())
        
        while True:
            # Waiting for data back
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                if not data:
                    print("[*] Connection closed by server")
                    return
                recv_len = len(data)
                response += data.decode()

                if recv_len < 4096:
                    break

            print(response)

            # Waiting for more input
            buffer = input("")
            buffer += "\n"

            # Now sending the data back
            client.send(buffer.encode())

    except:
        print("[*] Exception! Exiting...")
        client.close()
            

def server_loop(args):
    # if no target is defined then we listen on all interfaces
    if not args.target:
        args.target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((args.target,args.port))
    server.listen(3)
    #print("Listening on %s:%d" % (args.target, args.port))

    while True:
        client_socket, addr = server.accept()       # accept() -> (socket object, address info)
        print(client_socket, addr)
        
        # spin off a new thread to handle new client
        client_thread = threading.Thread(
            target=client_handler,
            args=(client_socket,args))
        client_thread.start()


def run_cmd(cmd):
    # trim the newline
    cmd = cmd.strip()

    # run the command and get the o/p back
    try:
        # subprocess provides a powerful process-creation interface that gives you 
        # a number of ways to start and interact with client programs
        #  In this case, we’re simply running whatever command we pass in
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        # print("Failed to exec command :(")
        output = str(e).encode()

    # send the o/p back to the client
    return output
    
# logic to do file uploads, command execution, and our shell
def client_handler(client_socket, args):
    try:
        # Check for file upload
        if args.upload:
            # read in all the bytes and write to our destination
            file_buffer = b""

            # keep reading till the end
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                else:
                    file_buffer += data

            # now we take these bytes and try to write them out
            try:
                file_descriptor = open(args.upload, "wb")
                file_descriptor.write(file_buffer)
                file_descriptor.close()

                # acknowledge that we wrote the file out
                client_socket.send(f"Successfully saved file to {args.upload}\r\n".encode())
            except:
                client_socket.send(f"Failed to save file to {args.upload}\r\n".encode())
        
        # Checking for command execution
        if args.execute:
            # run the command
            output = run_cmd(args.execute)
            client_socket.send(output)

        # Now we go into another loop if a command shell was requested
        if args.command:
            while True:
                # Show a simple prompt
                client_socket.send(b"<bochi:#>")

                # now we receive until we see a ENTER key
                cmd_buffer = b""
                while b"\n" not in cmd_buffer:
                    cmd_buffer += client_socket.recv(1024)
                
                # send back the cmd o/p
                response = run_cmd(cmd_buffer.decode())
                client_socket.send(response)
    finally:
        client_socket.close()


def main():
    parser, args = parse_args()
    
    # if no args were passed:
    if len(sys.argv[1:]) == 0:
        print("No Arguments passed :(\n")
        parser.print_help()
        sys.exit(0)

    # Client Mode:
    if not args.listen and args.target and args.port:
        buffer = sys.stdin.read()
        client_sender(buffer, args.target, args.port)

    # Server Mode:
    if args.listen:
        if not args.port:
            print("[*] Port number required in listen mode")
            sys.exit(1)
        server_loop(args)


if __name__ == "__main__":
    main()