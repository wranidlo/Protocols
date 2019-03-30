from socket import socket, AF_INET, SOCK_DGRAM
import datetime
import re
from threading import Thread

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('127.0.0.1', 6667))

operacja = ""
status = ""
wiadomosc = ""
my_id = "-1"

komunikat = ["Operacja+!", "Status+!", "Wiadomosc+!"]

isConnected = 0
isInvited = 2


def receive():
    global isInvited
    global isConnected
    while isInvited == 1 or isInvited == 2:
        try:
            nsekw_received = 0
            msg_received, addr = s.recvfrom(8196)
            if msg_received:
                while nsekw_received != "1":

                    msg_received = msg_received.decode("utf-8")
                    print("Odebrano: <<", msg_received)

                    data = re.split("!\|", msg_received)
                    for e in data:
                        extract = re.split("\+!", e)

                        if extract[0] == "nSekwencyjny":
                            nsekw_received = extract[1]

                        if extract[0] == "Wiadomosc" and extract[1] == "wysylam":
                            print("Odebrano wiadomosc")

                        if extract[0] == "Wiadomosc" and extract[1] == "przyjmuje":
                            print("Przyjeto moje zaproszenie")
                            print("Laczenie")
                            isInvited = 2
                            isConnected = 1

                        if extract[0] == "Wiadomosc" and extract[1] == "nie":
                            print("Odrzucono")
                            isConnected = 0
                            isInvited = 0

                        if extract[0] == "Wiadomosc" and extract[1] == "#quit":
                            isInvited = 0
                            isConnected = 0
                            s.close()

                        if extract[0] == "Wiadomosc":
                            print("Odebrano wiadomosc: ", extract[1])
                            nsekw_received = 0

                if isInvited == 2:
                    break
                if isInvited == 0:
                    s.close()
        except:
            continue


def send_internal_message(to_send, size):
    i = 0
    while i < size:
        msg = komunikat[i] + to_send[i] + "!|" + "nSekwencyjny+!" + str(size - i) + "!|" + "Identyfikator+!" + my_id \
              + "!|" + "Time_Stamp+!" + str(datetime.datetime.now()) + "!|"

        s.sendto(msg.encode("utf-8"), ('127.0.0.1', 6668))
        print("Wysyłam: >>", msg)

        i = i + 1


def send_ack():
    operacja = "Potwierdzenie"
    status = "ACK"

    msg1 = komunikat[0] + operacja + "!|" + "nSekwencyjny+!" + str(2) + "!|" + "Identyfikator+!" + my_id + "!|" + \
           "Time_Stamp+!" + str(datetime.datetime.now()) + "!|"

    s.sendto(msg1.encode("utf-8"), ('127.0.0.1', 6668))

    msg2 = komunikat[1] + status + "!|" + "nSekwencyjny:+!" + str(1) + "!|" + "Identyfikator+!" + my_id + "!|" + \
           "Time_Stamp+!" + str(datetime.datetime.now()) + "!|"

    s.sendto(msg2.encode("utf-8"), ('127.0.0.1', 6668))


def connect():
    global isConnected
    global isInvited
    if isConnected == 0:
        operacja = "polacz"
        status = "waiting"
        comm_list = [operacja, status]
        send_internal_message(comm_list, 2)

    else:
        print("Already connected")


def invite():
    global isConnected
    global isInvited
    if isInvited == 0 or isInvited == 2:
        operacja = "zapros"
        status = "waiting"
        wiadomosc = "invite"
        comm_list = [operacja, status, wiadomosc]
        send_internal_message(comm_list, 3)
        receive()

    else:
        print("Already in chat")


def send(msg):
    global isConnected
    global isInvited

    if isConnected and isInvited:
        operacja = "wysylam"
        status = "sending"
        wiadomosc = msg
        comm_list = [operacja, status, wiadomosc]
        send_internal_message(comm_list, 3)

    else:
        print("Nie dołączyłeś do czatu, polącz się z serwerem i zaproś uczestnika przed wysłaniem wiadomosci.")

    if msg == "#quit":
        print("Disconnected")
        isConnected = 0
        isInvited = 0
        s.close()


def listening():
    global isInvited
    global isConnected
    global my_id
    nsekw_received = 0

    while nsekw_received != "1":
        msg_received, addr = s.recvfrom(8196)
        msg_received = msg_received.decode("utf-8")
        print("Odebrano: <<", msg_received)

        data = re.split("!\|", msg_received)
        for e in data:
            extract = re.split("\+!", e)

            if extract[0] == "nSekwencyjny":
                nsekw_received = extract[1]

            if extract[0] == "Operacja" and extract[1] == "potwierdzenie":
                print("Odebrano potwierdzenie 1")
            if extract[0] == "Status" and extract[1] == "ACK":
                print("Odebrano potwierdzenie 2")

            if extract[0] == "Operacja" and extract[1] == "Nadano id":
                print(data)
                print("Otrzymano ID", data[2][15])

                my_id = data[2][15]

    send_ack()
    if my_id == "2":
        print("Zapraszam")
        invite()
        isInvited = 1
        isConnected = 1
    else:
        print("Oczekiwanie na zaproszenie")
        nsekw_received = "-1"
        while nsekw_received != "1" and (isInvited == 1 or isInvited == 2):
            msg_received, addr = s.recvfrom(8196)
            msg_received = msg_received.decode("utf-8")
            print("Odebrano: <<", msg_received)

            data = re.split("!\|", msg_received)
            for e in data:
                extract = re.split("\+!", e)

                if extract[0] == "nSekwencyjny":
                    nsekw_received = extract[1]

                if extract[0] == "Operacja" and extract[1] == "zapros":
                    print("Odebrano zaproszenie")
                    odp = input("przyjmujesz zaproszenie? przyjmuje/nie: ")
                    if odp == "nie":
                        send(odp)
                        isInvited = 0
                        isConnected = 0
                        s.close()
                        break
                    else:
                        odp = "przyjmuje"
                        send(odp)
                    isInvited = 1
        if isInvited:
            send_ack()

    receive_thread.start()
    while True:
        if input != False:
            if isInvited:
                try:
                    send(input(""))
                except:
                    print("Nie jestes polaczony")
                    break
            else:
                print("Nie dołączyłeś do czatu, polącz się z serwerem i zaproś uczestnika przed wysłaniem wiadomosci.")
                break


def action():
    global isConnected
    global isInvited
    print("Menu")
    print("Connect to server - type 0")

    choose = input("Choose your action: \n")

    if choose == "0":
        print("Coonnecting to server")
        connect()
        isConnected = 1
    else:
        print("Coonnecting to server")
        connect()
        isConnected = 1


if __name__ == "__main__":
    receive_thread = Thread(target=receive)

    action()
    listening()