'''
   TRABALHO PARCIAL 02 – SINCRONIZAÇÃO DE RELÓGIO
   Hélio Potelicki, Luis Felipe Zaguini e Pedro Henrique Roweder
 '''
from datetime import datetime, timedelta
from threading import Thread
from dateutil import parser
from time import sleep
import socket

# Armazena o endereco do client e dados do relogio
client_data = {}


def startReceivingClockTime(connector, address):
    try:
        while True:
            clock_time_string = connector.recv(1024).decode()
            clock_time = parser.parse(clock_time_string)
            clock_time_diff = datetime.now() - clock_time

            client_data[address] = {
                "clock_time": clock_time,
                "time_difference": clock_time_diff,
                "connector": connector
            }

            print(f"\nHora atualizada do client:{address}")
            sleep(10)

    except ConnectionResetError:
        pass


def startConnecting(master_server):

    while True:
        master_slave_connector, addr = master_server.accept()
        slave_address = str(f'{addr[0]}:{addr[1]}')

        print(f"{slave_address} connectado com sucesso!")

        current_thread = Thread(target=startReceivingClockTime,
                                args=(
                                    master_slave_connector,
                                    slave_address,
                                ))
        current_thread.start()


def getAverageClockDiff():

    time_difference_list = list(client['time_difference']
                                for client_addr, client in client_data.items())

    sum_of_clock_difference = sum(time_difference_list, timedelta(0, 0))

    average_clock_difference = sum_of_clock_difference / len(client_data)

    return average_clock_difference


def synchronizeAllClocks():

    while True:

        timeNow = datetime.now()
        print("\nSincronização iniciada...")
        print(f"Clients disponiveis para sincronizar: {len(client_data)}")
        print(f"Hora do servidor {timeNow.strftime('%H:%M:%S')}")

        if len(client_data) > 0:

            average_clock_difference = getAverageClockDiff()

            try:
                for client_addr, client in client_data.items():
                    try:
                        synchronized_time = timeNow + average_clock_difference

                        client['connector'].send(
                            str(synchronized_time).encode())

                    except Exception as e:
                        print(
                            f'\nErro!\n   Perda de conexão com client:{client_addr}'
                        )
                        del client_data[client_addr]

            except RuntimeError:
                synchronizeAllClocks()

        else:
            print("Nenhum client online\n")
        sleep(10)


def initiateClockServer(port=8080):
    # Cria socket
    master_server = socket.socket()
    master_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    master_server.bind(('', port))

    # Inicia relógio do servidor
    master_server.listen(10)

    # Inicia conexões
    master_thread = Thread(target=startConnecting, args=(master_server, ))
    master_thread.start()

    # Inicia sincronização
    sync_thread = Thread(target=synchronizeAllClocks, args=())
    sync_thread.start()


if __name__ == '__main__':
    initiateClockServer()