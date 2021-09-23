from dateutil import parser
import threading
import datetime
import socket
import time

# Armazena o endereco do client e dados do relogio
client_data = {}


def startReceivingClockTime(connector, address):

    while True:
        clock_time_string = connector.recv(1024).decode()
        clock_time = parser.parse(clock_time_string)
        clock_time_diff = datetime.datetime.now() - \
                                                 clock_time

        client_data[address] = {
            "clock_time": clock_time,
            "time_difference": clock_time_diff,
            "connector": connector
        }

        print(f"Client atualizado: {address}\n\n")
        time.sleep(5)


def startConnecting(master_server):

    while True:
        master_slave_connector, addr = master_server.accept()
        slave_address = str(f'{addr[0]}:{addr[1]}')

        print(f"{slave_address} connectado com sucesso!")

        current_thread = threading.Thread(target=startReceivingClockTime,
                                          args=(
                                              master_slave_connector,
                                              slave_address,
                                          ))
        current_thread.start()


def getAverageClockDiff():

    current_client_data = client_data.copy()

    time_difference_list = list(client['time_difference']
                                for client_addr, client in client_data.items())


    sum_of_clock_difference = sum(time_difference_list, \
                                   datetime.timedelta(0, 0))

    average_clock_difference = sum_of_clock_difference \
                                         / len(client_data)

    return average_clock_difference


def synchronizeAllClocks():

    while True:

        print("Sincronização iniciada...")
        print(f"Clients disponiveis para sincronizar: {len(client_data)}")

        if len(client_data) > 0:

            average_clock_difference = getAverageClockDiff()

            for client_addr, client in client_data.items():
                try:
                    synchronized_time = \
                         datetime.datetime.now() + \
                                    average_clock_difference

                    client['connector'].send(str(synchronized_time).encode())

                except Exception as e:
                    print(
                        f'Erro! \n   enviando hora sincronizada para: {client_addr}'
                    )

        else:
            print("Nenhum client online\n\n")
        time.sleep(5)


def initiateClockServer(port=8080):

    master_server = socket.socket()
    master_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print("Socket criado\n")

    master_server.bind(('', port))

    master_server.listen(10)
    print("Relógio do servidor iniciado...\n")

    print("Iniciando conexões...\n")
    master_thread = threading.Thread(target=startConnecting,
                                     args=(master_server, ))
    master_thread.start()

    print("Iniciando sincronização...\n")
    sync_thread = threading.Thread(target=synchronizeAllClocks, args=())
    sync_thread.start()


if __name__ == '__main__':
    initiateClockServer(port=8080)