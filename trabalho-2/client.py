#!/usr/bin/env python

import socket
import hashlib


TCP_IP = '127.0.0.1'
TCP_PORT = 6000
BUFFER_SIZE = 2048

def request_file(sock: socket):
    filename = input("Inform the name of the file: ")
    message = f"GET /{filename}"
    sock.send(message.encode())

    try:
        first_request = True
        confirmation_data = sock.recv(BUFFER_SIZE).decode("utf-8")
        print(confirmation_data)
        filename = filename.replace(".txt", "_client.txt")
        
        with open(filename, 'wb') as file:
            last_packet = b''
            while True:
                if (last_packet and not last_packet.startswith(b"RETRANSMIT")) or first_request:
                    data = sock.recv(BUFFER_SIZE)
                    first_request = False
                else:
                    sock.send(b"RETRANSMIT")
                    data = sock.recv(BUFFER_SIZE)
                
                if data == b"END_OF_FILE":
                    print("CLIENT INFO: FILE RECEIVED SUCCESSFULY")
                    return
                
                message = data.decode("utf-8").split("_")
                text = message[0].encode("utf-8")
                received_hash = message[1]
                generated_hash = hashlib.sha256(message[0].encode("utf-8")).hexdigest()
                
                if received_hash == generated_hash:
                    file.write(text)
                    print("CLIENT INFO: CHUNK RECEIVED SUCCESSFULY.")
                    sock.send(b"SUCCESS")
                    last_packet = text
                else:
                    print("CLIENT ERROR: INCOMPATIBLE CHUNK HASH VALUES. REQUESTING RETRANSMISSION...")
                    last_packet = b"RETRANSMIT"
                    sock.send(b"RETRANSMIT")
                
                print("RECEIVED HASH: ", received_hash)
                print("GENERATED HASH:", generated_hash)
    except socket.timeout:
        print("CLIENT ERROR: CONNECTINON TIMED OUT.")
        sock.close()
        return

    sock.close()

def handle_conversation(sock:socket):
    data = sock.recv(BUFFER_SIZE)
    print(data.decode())
    client_message = input("message: ")
    message = f"Chat: {client_message}"
    sock.send(message.encode())
    while True:
        try:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                print("CLIENT INFO: NO RESPONSE FROM THE SERVER")
                break
            elif data == (b"Chat: The server decided to close the chat connection"):
                print("CLIENT INFO: CHAT UNAVAILABLE!")
                break

            elif data == (b"INFO: CLIENT EXITING CHAT MODE\n"):
                print("CLIENT INFO: EXITING CHAT MODE")
                break
            print(data.decode())  # Print received message
            message = input("message: ")
            client_message = f"Chat: {message}"
            sock.send(client_message.encode())
        except ConnectionError:
            print("Connection to server lost.")
            break

def Main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))

    print("CLIENT INFO: Connected to the server")

    MESSAGE = input("What do you want from the server?\n")

    sock.send(MESSAGE.encode("utf-8"))

    if MESSAGE.lower() == "file":
        request_file(sock=sock)
        print("CLIENT INFO: CLOSING CONNECTION")
    
    elif MESSAGE.lower() == "chat":
        handle_conversation(sock=sock)
        print("CLIENT INFO: CHAT IS NOW CLOSED")
    
    else:
        print("INVALID COMMAND!")
    sock.close()
    

    # print ("received data:", data)

Main()