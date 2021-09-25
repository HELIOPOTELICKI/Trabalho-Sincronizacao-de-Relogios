'''
   TRABALHO PARCIAL 02 – SINCRONIZAÇÃO DE RELÓGIO
   Hélio Potelicki, Luis Felipe Zaguini e Pedro Henrique Roweder
 '''
from datetime import datetime, timedelta
from dateutil.parser import parse
from time import sleep
import threading
import socket


def startSendingTime(slave_client):
    # Envia ao servidor a hora do client a cada 10 segundos
    while True:
        # Adição de tempo somente para testes
        timeNow = (datetime.now() + timedelta(hours=4))
        slave_client.send(str(timeNow).encode())
        print(f"Client --> Port:{slave_client.getsockname()[1]}")
        print(f"Hora do client enviada -> {timeNow.strftime('%H:%M:%S')}")
        sleep(10)


def startReceivingTime(slave_client):

    while True:
        Synchronized_time = parse(slave_client.recv(1024).decode())

        print(f"Hora atualizada: {Synchronized_time.strftime('%H:%M:%S')}\n\n")


def initiateSlaveClient(port=8080):
    slave_client = socket.socket()
    slave_client.connect(('192.168.1.2', port))

    print("Recebendo hora do servidor\n")
    send_time_thread = threading.Thread(target=startSendingTime,
                                        args=(slave_client, ))
    send_time_thread.start()

    receive_time_thread = threading.Thread(target=startReceivingTime,
                                           args=(slave_client, ))

    receive_time_thread.start()


if __name__ == '__main__':
    initiateSlaveClient()