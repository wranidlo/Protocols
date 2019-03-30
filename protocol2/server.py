from socket import socket, AF_INET, SOCK_DGRAM
import re
import datetime
identyfikator=0
next_id = 1
komunikat = ["Operacja+!", "Status+!", "Wiadomosc+!"]
def send(to_send,size,adres,id):
    i = 0
    while i<size:

        msg = komunikat[i] + to_send[i] + "!|" + "nSekwencyjny+!" + str(size - i) + "!|" + "Identyfikator+!" + str(id) \
              + "!|" + "Time_Stamp+!" + str(datetime.datetime.now())+"!|"

        serwer.sendto(msg.encode("utf-8"), adres)
        print("Wysyłam: ", msg)

        i = i+1

def send_ack(adres,id):

    operacja = "ACK"
    status = "ACK"

    msg1 = komunikat[0] + "potwierdzenie" + "!|" + "nSekwencyjny+!" + str(2) + "!|" + "Identyfikator+!" + str(id) + "!|" + \
           "Time_Stamp+!" + str(datetime.datetime.now())+"!|"
    print("ack",msg1)
    serwer.sendto(msg1.encode("utf-8"), (adres))

    msg2 = komunikat[1] + "ACK" + "!|" + "nSekwencyjny:+!" + str(1) + "!|" + "Identyfikator+!" + str(id) + "!|" + \
           "Time_Stamp+!" + str(datetime.datetime.now())+"!|"
    print("ack",msg2)
    serwer.sendto(msg2.encode("utf-8"), (adres))
serwer = socket(AF_INET, SOCK_DGRAM)
client = socket(AF_INET, SOCK_DGRAM)
serwer.bind(('127.20.10.14', 6667))
list = []
choose=0
Op="Operacja+!"
Status="Status+!"
NSekwencyjny="NSekwencyjny+!"
Czas="Czas+!"
Identyfikator="Identyfikator+!"
Text="Text+!"
dzielnik="!|"
x=0
i=0
while True:
    received_tab=[]
    received=[]
    nr_sekwencyjny =0
    while nr_sekwencyjny !="1":
        msg, addr = serwer.recvfrom(8192)
        msg.decode('utf-8')
        print ("Odebralem : ",msg)
        data=re.split("\!\|",msg.decode('utf-8'))
        for e in data:
            extract=re.split("\+\!",e)
            received.append(extract)
            if extract[0]=="nSekwencyjny":
                nr_sekwencyjny=extract[1]
            if extract[0]=="Identyfikator":
                id=extract[1]
            if extract[0]=="Operacja":
                operation=extract[1]
                if(extract[1]=="polacz"):
                    list.append(addr)
            if extract[0]=="Wiadomosc":
                text=extract[1]

    send_ack(addr,id)
    received_tab.append(received)
    print ("OD :" ,addr)
    for e in received_tab:
        print("Tablica odebranych : ")
        print(e)
    if(operation=="polacz"):
        send(["Nadano id","waiting"],2,addr,next_id)
        next_id = next_id +1
        if(next_id>2):
            next_id=1
        msg, addr = serwer.recvfrom(8192)
        msg, addr = serwer.recvfrom(8192)
        print("polaczono")
    if(operation=="zapros"):
        if id =="1":
            id="1"
        if id =="2":
            id="0"
        if (text=="nie"):
            status_="error"
        else :
            status_="ok"
        send(["zapros",status_,text],3,list[int(id)],str(int(id)+1))
        if(text=="nie"):
            list.clear
        msg, addr = serwer.recvfrom(8192)
        msg, addr = serwer.recvfrom(8192)
        print("przesłano zaproszono")
    if(operation=="wysylam"):
        if id =="1":
            id="1"
        if id =="2":
            id="0"
        print("id : ",id)
        send(["wysylam","ok",text],3,list[int(id)],str(int(id)+1))
        msg, addr = serwer.recvfrom(8192)
        msg, addr = serwer.recvfrom(8192)
        print("przesłano wiadomosc")
        if(text=="#quit"):
            list.clear()
    print (list)

