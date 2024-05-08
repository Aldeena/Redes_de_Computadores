import socket
import os

def split_file(filename, chunk_size):
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum += byte
    return checksum & 0xFF

UDP_PORT = 6000
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', UDP_PORT))

print("Servidor UDP esperando conexões...")

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print("Mensagem recebida:", data)
    print("Endereço do cliente:", addr)

    message = data.decode()
    print("Mensagem decodificada:", message)

    filename = message.split('/')[-1]
    print("Nome do arquivo:", filename)

    if os.path.exists(filename):
        print("Arquivo encontrado. Enviando...")
        confirmation_message = f"Recebido: {filename}"
        sock.sendto(confirmation_message.encode(), addr)
        
        for chunk in split_file(filename, BUFFER_SIZE):
            print(chunk)
            checksum = calculate_checksum(chunk)
            chunk_with_checksum = chunk + bytes([checksum])
            # print(chunk_with_checksum)
            sock.sendto(chunk_with_checksum, addr)

            # Wait for acknowledgment or retransmission request
            while True:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                if data == b"SUCCESS":
                    print("Enviado com sucesso")
                    break
                elif data == b"RETRANSMIT":
                    print("Reenviando pacote perdido")
                    sock.sendto(chunk_with_checksum, addr)
                else:
                    print("Mensagem desconhecida:", data)

            print("Checksum enviado:", checksum)
            print("Enviado:", len(chunk), "bytes")
        
        end_of_file_message = b"END_OF_FILE"
        sock.sendto(end_of_file_message, addr)
        print("Fim da transmissão")
    else:
        error_message = "Erro: Arquivo não encontrado"
        sock.sendto(error_message.encode(), addr)
        print("Erro: Arquivo não encontrado.")

sock.close()
