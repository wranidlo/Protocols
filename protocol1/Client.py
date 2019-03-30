import socket
from bitarray import bitarray

#Inicjalizacja socketu
host = '127.0.0.1'
port = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

#Deklaracja zmiennych pomocniczych
command = ""
check = 0
x = 0
isClient = 0

#Formatowanie komunikatu proszącego o połączenie
isClientSend = '{0:01b}'.format(isClient)
liczba1 = '{0:032b}'.format(x)
liczba2 = '{0:032b}'.format(x)
liczba3 = '{0:032b}'.format(x)
w = '{0:02b}'.format(x)
blank = w + liczba1 + liczba2 + liczba3
setid = '{0:06}'.format(x)
setstatus = '{0:04b}'.format(0)

#Złożenie komunikatu operatorem konkatenacji
msg = blank + setstatus + setid + isClientSend

#Zamiana komunikatu string na bitarray
ba = bitarray(msg)

#Wysłanie komunikatu
s.send(ba.tobytes())

#Debugowanie, sprawdzenie poprawnosci przez wypisanie komunikatu w konsoli
print("Client:> Sent first msg: ", ba.tobytes())
print("Client:> Sent first msg: ", ba.to01())

myid = 0

#Główna pętla
while True:
    if check == 0:
        try:
            #Odbieranie komunikatu od serwera
            msg = s.recv(14)
            msg2 = bitarray(endian="big")
            msg2.frombytes(msg)
            print("Serwer:> ", msg2.to01())

            #Podzial komunikatu odebranego na potrzebne segmenty
            recv_status = msg2[98:102]
            myid = (msg2[102:108]).to01()

            #Podział komunikatu ze względu na odebrany status
            if recv_status == bitarray('1100'):

                #Odebranie i przedstawienie wyniku
                result = msg2[2:98]
                resultInt = result.to01()
                if resultInt[0] == "1":
                    resultInt2 = "0" + resultInt[3:98]
                    print("Serwer:> Wynik otrzymany od serwera: -", int(resultInt2, 2))
                else:
                    resultInt2 = resultInt
                    print("Serwer:> Wynik otrzymany od serwera: ", int(resultInt2, 2))
            #Odebranie potwierdzenia nadania identyfikatora
            if recv_status == bitarray('0001'):
                print("Client:> Moje ID: ", myid)
                print("Serwer:> Odebrano: ", msg)
            #Obsługa błędów
            if recv_status == bitarray('1000'):
                print("Serwer:> Bledne dane. Sprobuj ponownie")
        except:
            print(":> There is an error in while receiving")
            break
        #Zamykanie połączenia z inicjatywy klienta
        command = str(input(":> Wpisz exit jesli chcesz zakonczyc: "))
    try:
        if command == "exit":
            print("Client:> Closing")
            stat = 10
            number1 = int(0)
            number2 = int(0)
            number3 = int(0)
            dzialanie = int(0)
        else:
            #Wczytywanie danych od użytkownika
            stat = 3
            number1 = int(input(":> Podaj 1. liczbe: "))
            while number1 > (2**32 - 1) or number1 < 0:
                print(":> Przekroczono limit. Sproboj ponownie: ")
                number1 = int(input(":> Podaj 1. liczbe: "))
                if number1 == -1:
                    print("Client:> Closing")
                    stat = 10
                    number1 = int(0)
                    number2 = int(0)
                    number3 = int(0)
                    dzialanie = int(0)

            number2 = int(input(":> Podaj 2. liczbe: "))
            while number2 > (2**32 - 1) or number2 < 0:
                print(":> Przekroczono limit. Sproboj ponownie: ")
                number2 = int(input(":> Podaj 2. liczbe: "))
                if number2 == -1:
                    print("Client:> Closing")
                    stat = 10
                    number1 = int(0)
                    number2 = int(0)
                    number3 = int(0)
                    dzialanie = int(0)

            number3 = int(input(":> Podaj 3. liczbe: "))
            while number3 > (2**32 - 1) or number3 < 0:
                print(":> Przekroczono limit. Sproboj ponownie: ")
                number3 = int(input(":> Podaj 3. liczbe: "))
                if number3 == -1:
                    print(":> Closing")
                    stat = 10
                    number1 = int(0)
                    number2 = int(0)
                    number3 = int(0)
                    dzialanie = int(0)

            dzialanie = int(input(":> Wybierz dzialanie : 0-odejmowanie, 1-dzielenie, 2-dodawanie, 3-mnozenie: "))
    except:
        print("Blad")
        check = 1
        continue
    check = 0
    #Składanie danych otrzymanych od użytkownika
    liczba1 = '{0:032b}'.format(number1)
    liczba2 = '{0:032b}'.format(number2)
    liczba3 = '{0:032b}'.format(number3)
    w = '{0:02b}'.format(dzialanie)
    status = '{0:04b}'.format(stat)

    msg = w + liczba1 + liczba2 + liczba3 + status + myid + isClientSend

    ba = bitarray(msg, endian="big")
    #Wysyłanie komunikatu
    s.send(ba.tobytes())
    print("Client:> ", ba)

    #Zajmowanie się zamknięciem komunikacji
    if command == "exit":
        s.close()
        break
