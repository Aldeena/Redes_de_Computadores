#!/usr/bin/env python

import socket
import os
import _thread
import hashlib
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 6000
BUFFER_SIZE = 1024

client_threads = _thread.allocate_lock()

def split_file(filename, chunk_size):
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk


def send_file(connection, address):
    data = connection.recv(BUFFER_SIZE)
    print("SERVER INFO: MESSAGE RECEIVED", data)

    message = data.decode()
    print("SERVER INFO: MESSAGE DECODED", message)

    filename = message.split('/')[-1]
    print("SERVER INFO: FILENAME ", filename)

    if os.path.exists(filename):
        file = open(filename, "r")
        text = file.read()
        hash_verification = hashlib.sha256(text.encode("utf-8")).hexdigest()
        print("SERVER INFO: FOUND FILE. SENDING TO THE CLIENT")
        confirmation_message = f"INFO:{filename}_{str(len(text))}_{hash_verification}"
        connection.send(confirmation_message.encode("UTF-8"))
        
        for chunk in split_file(filename, BUFFER_SIZE):
            # print(chunk)
            chunk_with_sha = chunk + ("_" + (hashlib.sha256(chunk).hexdigest())).encode("utf-8")
            # print(len(chunk_with_sha))
            # print(chunk_with_checksum)
            connection.send(chunk_with_sha)

            # Wait for acknowledgment or retransmission request
            while True:
                data = connection.recv(BUFFER_SIZE)
                if data == b"SUCCESS":
                    print("SERVER INFO: CHUNK SENT SUCCESSFULY!")
                    break
                elif data == b"RETRANSMIT":
                    print("SERVER ERROR: RE-SENDING CHUNK")
                    connection.send(chunk_with_sha)
                else:
                    print("SERVER ERROR: UNKNOWN MESSAGE", data)
        
        end_of_file_message = b"END_OF_FILE"
        connection.send(end_of_file_message)
        print("SERVER INFO: FILE SENT! CHECK CLIENT")

        return

    else:
        error_message = "ERROR: FILE NOT FOUND!"
        connection.send(error_message.encode())
        print("SERVER ERROR: FILE NOT FOUND!")

        return
    

def handle_chat(connection, address):
    connection.send(b"You are now in chat mode. Type 'exit' to exit chat mode.\n")
    while True:
        # Start a timer with time.sleep() for 5 seconds
        timeout = 5.0
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            data = connection.recv(BUFFER_SIZE)
            if data:
                message = data.decode().strip()
                print(f"Client {address}: {message}")
                
                if message.lower() == "chat: exit":
                    connection.send(b"INFO: CLIENT EXITING CHAT MODE\n")
                    return
                
                respond_message = input("Respond client's message? (y/n): ").lower() == 'y'
                if respond_message:
                    response = input("response: ")
                    server_response = f"Chat: {response}"
                    connection.send(server_response.encode())
                else:
                    server_response = "Chat: The server decided to close the chat connection"
                    connection.send(server_response.encode())
                    return

                # Reset start_time for next timeout check
                start_time = time.time()
            else:
                time.sleep(0.1)  # Small sleep to avoid busy waiting

        # If no response received within timeout
        if (time.time() - start_time) >= timeout:
            connection.send(b"SERVER INFO: CONNECTION TIMED OUT, TOOK TOO LONG TO ANSWER, CLOSING CONNECTION.\n")
            return

def connection_handling(connection, address) -> bool:
    while True:
        data = connection.recv(BUFFER_SIZE)
        if not data: break
        message = data.decode()
        if message.lower() == "exit":
            print ( f"SERVER INFO: CLIENT {address} REQUESTING TO CLOSE THE CONNECTION")
            connection.send(b"SERVER INFO: CLIENT REQUESTING TO CLOSE THE CONNECTION")
            break
        elif message.lower() == "file":
            send_file(connection=connection, address=address)
            break
        elif message.lower() == "chat":
            handle_chat(connection=connection, address=address)
            break
        else:
            print(data.decode())
            print ("SERVER ERROR: CLIENT COMMAND IS INVALID, CLOSING THE CONNECTION IMMEDIATLY!")
            connection.send(b"SERVER ERROR: CLIENT COMMAND IS INVALID, CLOSING THE CONNECTION IMMEDIATLY!")
            break

    connection.close()

    return True

def Main():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((TCP_IP, TCP_PORT))
    sock.listen(1)
    print("SERVER INFO: SERVER IS NOW LISTENING. AGORA ESTÁ DEMONSTRANDO A VERDADEIRA ESSÊNCIA")

    
    while True:
        connection, address = sock.accept()
        print("SERVER INFO: NEW CONNECTION ON THE FOLLOWING ADDRESS: ", address)
        client_threads.acquire()

        _thread.start_new_thread(connection_handling, (connection, address))
        
        client_threads.release()
        
    # sock.close()
        # print ("received data:", data.decode())
        # conn.send(data)  # echo
    # conn.close()

Main()