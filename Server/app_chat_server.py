import sys
from _thread import *
from PySide6 import QtCore,QtWidgets,QtGui
import socket
import json
import threading
    

class myServer(QtWidgets.QWidget):
    def __init__(self):

        super(myServer, self).__init__()

        #server parameters
        self.socket = None
        self.connected_clients = {}
        self.list = []
        self.map = {}
        self.running = False

        #create and configure input widget
        self.portInput = QtWidgets.QLineEdit()
        self.portInput.setMaxLength(5)
        self.portInput.setAlignment(QtCore.Qt.AlignRight)
        self.portInput.setFont(QtGui.QFont("Arial",20))

        self.labelSendBroadcast = QtWidgets.QLabel("Envie mensagem para todos os clientes:")
        self.btnSendBroadcast = QtWidgets.QPushButton("Enviar!")
        self.broadcastInput = QtWidgets.QLineEdit()
        self.broadcastInput.setMaxLength(20)
        self.broadcastInput.setAlignment(QtCore.Qt.AlignRight)
        self.broadcastInput.setFont(QtGui.QFont("Arial",14))

        #create list widgets
        self.clients_list_wdgt = QtWidgets.QListWidget()
        self.boxLayout = QtWidgets.QHBoxLayout()

        #set host
        hostname = socket.gethostname() 
        self.host = socket.gethostbyname(hostname)
        self.labelHost = QtWidgets.QLabel("IP Host:" + self.host)
        self.labelPort = QtWidgets.QLabel("Digite a porta:")
        self.labelInit = QtWidgets.QLabel("Aperte para iniciar:")
        self.textStatus = QtWidgets.QLabel()

        #create and configure widgets
        self.button = QtWidgets.QPushButton("Iniciar servidor!")

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.addWidget(self.labelHost, 0, 0)
        self.gridLayout.addWidget(self.labelPort, 1, 0)
        self.gridLayout.addWidget(self.portInput, 1, 1)
        self.gridLayout.addWidget(self.labelInit, 2, 0)
        self.gridLayout.addWidget(self.button, 2, 1)
        self.gridLayout.addWidget(self.textStatus, 3, 0)
        self.gridLayout.setVerticalSpacing(10)

        self.labelClients = QtWidgets.QLabel("Clientes conectados:")

        self.gridLayoutClients = QtWidgets.QGridLayout()

        self.gridLayoutClients.addWidget(self.labelClients, 0, 0)
        self.gridLayoutClients.addWidget(self.clients_list_wdgt, 1, 0)

        self.boxLayout.addLayout(self.gridLayout)
        self.boxLayout.addLayout(self.gridLayoutClients)
        self.setLayout(self.boxLayout)

        self.button.clicked.connect(self.initServer)
        self.btnSendBroadcast.clicked.connect(self.broadcast)

        self.setWindowTitle("Chat App")

    def acceptConnection(self):
        while True:
            try:
                Client, address = self.socket.accept()
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                self.connected_clients[address] = Client
                threading.Thread(target=self.listen,args=(Client, address,)).start()
            except:
                self.running = False
                self.textStatus.setText("O servidor foi desligado!")
                break

    def listen(self, client, address):
        while self.running:
            print("escutando")
            try:
                message = json.loads(client.recv(1024))
                print(message)
                if message["type"] == "CONNECT":
                    self.send(client, "CONNECTED", None, None, self.list)
                    self.map[client] = (message["name"], message["ip"])
                    self.list.append((message["name"], message["ip"]))
                    self.update([])
                elif message["type"] == "MESSAGE":
                    for user in message["clients"]:
                        for key, value in self.map.items():
                            if value[1] == user:
                                self.send(key, "MESSAGE", message["name"], message["content"], message["clients"])
                elif message["type"] == "DISCONNECT":
                    self.list.remove(self.map.pop(client))
                    self.connected_clients.pop(address)
                    self.send(client, "DISCONNECTED", None, None, None)
                    self.update([client])
                    client.close()
                    break
            except Exception as e:
                print(str(e))
                self.list.remove(self.map.pop(client))
                self.update([client])
                self.connected_clients.pop(address)
                client.close()
                break
        
    def initServer(self):
        self.textStatus.setText("Iniciando servidor...")
        self.port = self.portInput.text()
        if self.port != "":
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.bind((self.host, int(self.port)))
                self.socket.listen()
                self.running = True
                self.textStatus.setText("Servidor OK! Aguardando clientes...")
                self.labelPort.hide()
                self.portInput.hide()
                self.labelInit.hide()
                self.button.hide()
                self.gridLayout.addWidget(self.labelSendBroadcast,4,0)
                self.gridLayout.addWidget(self.broadcastInput,5,0)
                self.gridLayout.addWidget(self.btnSendBroadcast,6,0)
                threading.Thread(target=self.acceptConnection).start()
            except socket.error:
                self.textStatus.setText("Não foi possível iniciar o servidor! Tente novamente!")          
        else: 
            self.textStatus.setText("Por favor, digite a porta!")

    def update(self,excludes: list):
        clients = self.connected_clients.copy()
        self.clients_list_wdgt.clear()
        for key in clients.keys():
            if key[0] not in excludes:
                client_list = self.list.copy()
                self.send(clients[key], "UPDATE", None, None, client_list)
                item = QtWidgets.QListWidgetItem()
                item.setText(self.map[clients[key]][0])
                self.clients_list_wdgt.addItem(item)
        for client in excludes:
            if client in clients.keys():
                self.clients_list_wdgt.takeItem(self.clients_list_wdgt.row(self.items[client]))

    def stop(self):
        clients = self.connected_clients.copy()
        for client in clients.values():
            self.send(client, "DISCONNECTED", None, None, None)
        self.list.clear()
        self.map.clear()
        self.connected_clients.clear()
        self.socket.close()

    def send(self, client, type, name, content, aList):
        if self.running and client:
            message = {
                "type": type,
                "name": name,
                "content": content,
                "clients": aList
            }
            try:
                client.send(json.dumps(message).encode())
            except:
                item = QtWidgets.QListWidgetItem()
                item.setText('Não foi possível enviar a mensagem para o cliente {}'.format(name))
                self.chat_list_wdgt.addItem(item)

    def broadcast(self):
        message = self.broadcastInput.text()
        if message:
            clients = self.map.copy()
            for client in clients.keys():
                try:
                    self.send(client, "MESSAGE", 'Servidor', message, None)
                except:
                    item = QtWidgets.QListWidgetItem()
                    item.setText('Não foi possível enviar a mensagem para o cliente {}'.format(clients[client][0]))
                    self.chat_list_wdgt.addItem(item)

    def closeEvent(self, event):
        if self.running:
            self.stop()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = myServer()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())