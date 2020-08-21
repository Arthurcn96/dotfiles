#   
#   Programa que cria um servidor http na pasta atual e gera um QR Code para o link na rede.
#   Autor: Arthur Novais
#

# server.py
import qrcode_terminal as qr
import netifaces as ni 
import sys
import os

PORT = 9000

ip = ni.ifaddresses('eno1')[ni.AF_INET][0]['addr']
server = "http://"+ip+":"+str(PORT)

print("The server is running on", server)

srv = "python3 -m http.server " + str(PORT)

try:
    dir = sys.argv[1]
    command = srv + " -d " + str(dir)
    
    print("Vai abrir um servidor em ", srv,dir)

    #print(command)
    qr.draw(server)
    os.system(command)

except:
   print("Error")
