import socket
import random

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum += byte
    return checksum & 0xFF

def request_file(server_address, server_port, filename, simulate_packet_loss=False, loss_probability=0.1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (server_address, server_port)
    message = f"GET /{filename}"
    sock.sendto(message.encode(), server_address)

    try:
        confirmation_data, addr = sock.recvfrom(1025)
        print("Mensagem de confirmação do servidor:", confirmation_data.decode())
        filename = filename.replace(".txt", "_client.txt")
        
        with open(filename, 'wb') as file:
            last_packet = b''
            while True:
                if last_packet and not last_packet.startswith(b"RETRANSMIT"):
                    data, addr = sock.recvfrom(1025)
                else:
                    sock.sendto(b"RETRANSMIT", server_address)
                    data, addr = sock.recvfrom(1025)
                
                if data == b"END_OF_FILE":
                    print("Fim da transmissão")
                    break
                
                # Simulate packet loss
                if simulate_packet_loss and random.random() < loss_probability:
                    print("Simulating packet loss. Packet discarded.")
                    last_packet = b''
                    continue
                
                print(data[:-1])
                received_checksum = data[-1]
                calculated_checksum = calculate_checksum(data[:-1])
                
                if received_checksum == calculated_checksum:
                    file.write(data[:-1])
                    print("Fragmento do arquivo recebido com sucesso.")
                    sock.sendto(b"SUCCESS", server_address)
                    last_packet = data
                else:
                    print("Erro: checksum inválido. Solicitando retransmissão...")
                    last_packet = b"RETRANSMIT"
                    sock.sendto(b"RETRANSMIT", server_address)  # Request retransmission
                
                print("Checksum recebido:", received_checksum)
                print("Checksum calculado:", calculated_checksum)
    except socket.timeout:
        print("Timeout: Não foi possível receber dados do servidor.")
        sock.close()
        return

    sock.close()

server_ip = "127.0.0.1"
server_port = 6000

filename = input("Digite o nome do arquivo a ser solicitado: ")

simulate_loss = input("Simulate packet loss? (y/n): ").lower() == 'y'
if simulate_loss:
    loss_probability = float(input("Enter packet loss probability (0-1): "))
else:
    loss_probability = 0

request_file(server_ip, server_port, filename, simulate_packet_loss=simulate_loss, loss_probability=loss_probability)
