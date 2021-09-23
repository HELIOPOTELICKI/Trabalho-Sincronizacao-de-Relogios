from dateutil import parser
import threading
import datetime
import socket
import time


def startSendingTime(slave_client):

    while True:
        slave_client.send(str(datetime.datetime.now()).encode())

        print("Hora enviada", end="\n\n")
        time.sleep(5)


def startReceivingTime(slave_client):

    while True:
        Synchronized_time = parser.parse(slave_client.recv(1024).decode())

        print(f"Hora sincronizada: {Synchronized_time}\n\n")


def initiateSlaveClient(port=8080):

    slave_client = socket.socket()

    slave_client.connect(('127.0.0.1', port))

    print("Recebendo hora do servidor\n")
    send_time_thread = threading.Thread(target=startSendingTime,
                                        args=(slave_client, ))
    send_time_thread.start()

    receive_time_thread = threading.Thread(target=startReceivingTime,
                                           args=(slave_client, ))

    receive_time_thread.start()


if __name__ == '__main__':
    initiateSlaveClient()