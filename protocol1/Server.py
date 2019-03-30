import socket
from bitarray import bitarray
from threading import Thread
import struct

#Dane konfiguracyjne
host = '127.0.0.1'
port = 8080

#Inicjalizacja socketu
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))

#Obsługa pierwszego komunikatu, wywoływan, gdy klient wysłał prośbę o połączenie
def accept_client_connections():
    recentid = 0
    while True:
        client_con, client_address = s.accept()
        # konfiguracja
        print(client_address)
        print(client_con)
        #Odbieranie komunikatu od klienta
        msg = client_con.recv(14)
        msg2 = bitarray(endian='big')
        msg2.frombytes(msg)
        #czytanie statusu
        status = msg2[98:102]
        print (status)
        #Wybór akcji ze względu na odebrany komunikat
        if status == bitarray('0000'):
            #Nadanie id
            clientid = recentid + 1
            recentid=recentid +1
            print(client_address, "Has connected")
            liczba1 = '{:032b}'.format(0)
            liczba2 = '{:032b}'.format(0)
            liczba3 = '{:032b}'.format(0)
            w = '{:02b}'.format(0)
            blank = liczba1 + liczba2 + liczba3 + w
            setid = '{:06b}'.format(clientid)

            setstatus_ack = '{:04b}'.format(1)  # status: 1 dopisano clienta, oczekiwanie na dane
            sender='{:01b}'.format(1)
            msg = blank + setid + setstatus_ack+sender
            msg2=bitarray(msg)
            print("wiadomosc do nowego klienta: " + msg)
            ba=bitarray(msg2)
            client_con.send(ba.tobytes())
            Thread(target=handle_client, args=(client_con, client_address)).start()
        else:
            #Obsługa ewentualnego błędu połączenia
            print("Błąd połączenia")
            liczba1 = '{:032b}'.format(0)
            liczba2 = '{:032b}'.format(0)
            liczba3 = '{:032b}'.format(0)
            w = '{:02b}'.format(0)
            blank = liczba1 + liczba2 + liczba3 + w
            setid = '{:06}'.format(0)
            setstatus = '{:04b}'.format(15)  # status: 1 dopisano clienta, oczekiwanie na dane
            sender='{:01b}'.format(1)
            msg = blank + setid + setstatus+sender
            msg2=bitarray(msg)
            print("wiadomosc do nowego klienta: ", msg2)
            ba=bitarray(msg2)
            client_con.send(ba.tobytes())

#Obsługa już połączonego klienta
def handle_client(connection, address):
    while True:
        #Odebranie komunikatu
        msg = connection.recv(14)
        msg2 = bitarray(endian='big')
        msg2.frombytes(msg)
        msg2=msg2.to01()
        print(msg2)
        #Wyodrębnienie potrzebnych części komunikatu
        liczba1 = msg2[2:34]
        liczba2 = msg2[34:66]
        liczba3 = msg2[66:98]
        dzialanie = msg2[0:2]
        print(dzialanie)
        id = msg2[102:108]
        status = msg2[98:102]
        sender='{:01b}'.format(1)
        dzial2 = '{:02b}'.format(int(dzialanie, 2))
        print(status)
        print(dzial2)
        id2 = '{:06b}'.format(int(id, 2))
        #Wybór akcji ze względu na status
        if status == '0011':
            #Status OK, obliczanie wyniku
            print("Odebrano : ", msg2)
            status='1100'
            stat2 = '{:04b}'.format(int(status, 2))
            #Wybor dzialania i obliczenie wyniku
            if dzialanie == '10':
                x = (int(liczba1, 2) + int(liczba2, 2) + int(liczba3, 2))
                x2 = '{:096b}'.format(x)
            if dzialanie == '00':
                x = (int(liczba1, 2) - int(liczba2, 2) - int(liczba3, 2))
                x2 = '{:096b}'.format(x)
            if dzialanie == '01':
                if (int(liczba1, 2))==0 or (int(liczba3, 2))==0:
                    x=0
                    x2 = '{:096b}'.format(x)
                    status='1000'
                    stat2 = '{:04b}'.format(int(status, 2))
                else :
                    x = int(int(liczba1, 2) / int(liczba2, 2) / int(liczba3, 2))
                    x2 = '{:096b}'.format(x)
            if dzialanie == '11':
                x = (int(liczba1, 2) * int(liczba2, 2) * int(liczba3, 2))
                x2 = '{:096b}'.format(x)
            #Sprawdzanie czy wynik nie jest wiekszy od maksymalnej wartości
            if abs(x)>(2**96-1):
                status='1000'
                stat2 = '{:04b}'.format(int(status, 2))
            #Konstruowanie komunikatu
            msg = dzial2 +x2 + stat2+id2 + sender
            print("Wysyłam : ",msg)
            msg3=''
            print (msg)
            if msg[2]=='-':
                msg3=msg[0:2]+'1'+msg[3:109]
                ba=bitarray(msg3)
            else:
                ba=bitarray(msg)
            #Wysyłanie komunikatu
            connection.send(ba.tobytes())
            print("Wysyłam : ",ba)
        if status == '1010':
            connection.close()
            break;

#Główna funkcja main
if __name__ == "__main__":
    n = int(input("Podaj max liczbe klientow : "))
    s.listen(n)
    print("The serwer is now listening to clients requests")
    t1 = Thread(target=accept_client_connections)
    t1.start()
    t1.join()
