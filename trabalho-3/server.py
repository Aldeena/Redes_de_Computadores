#!/usr/bin/env python

import socket
import os
import _thread
import hashlib
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024

client_threads = _thread.allocate_lock()

endpoints = {
    "/": "home.html",
    "/page":"htmlPage.html",
    "/landscape": "landscape.jpg",
    "/lunar": "lunar_new_year.jpg"
}


def connection_handling(connection, address) -> bool:
    while True:
        data = connection.recv(BUFFER_SIZE)
        if not data:
            break
        message = data.decode()
        request = message.split("Host")[0].strip()  # Strip any extra whitespace

        print("Request received:", message)

        for endpoint, filename in endpoints.items():
            if request.startswith(f"GET {endpoint} HTTP/1.1"):
                print("Matching endpoint found:", endpoint)
                if os.path.exists(filename):

                    if filename.endswith(".html"):
                        with open(filename, "r", encoding="utf-8") as file:
                            file_body = file.read()

                        response_status = "HTTP/1.1 200 OK\r\n"
                        response_header = f"Content-Type: text/html; charset=utf-8\r\nContent-Length: {len(file_body.encode('utf-8'))}\r\n\r\n"

                        response = (response_status + response_header + file_body).encode("utf-8")

                    elif filename.endswith(".jpg"):
                        with open(filename, "rb") as file:
                            file_body = file.read()

                        response_status = "HTTP/1.1 200 OK\r\n"
                        response_header = f"Content-Type: image/jpeg\r\nContent-Length: {len(file_body)}\r\n\r\n"

                        response = (response_status + response_header).encode("utf-8") + file_body

                    else:
                        error_message = "HTTP/1.1 400 Bad Request\r\n\r\n"
                    connection.sendall(response)
                    break  # Exit the loop if matched

        else:
            error_message = "HTTP/1.1 404 Not Found\r\n\r\n"
            connection.sendall(error_message.encode("utf-8"))

        connection.close()
        return True


def Main():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((TCP_IP, TCP_PORT))
    sock.listen()
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