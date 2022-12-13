import socket
from PySide6 import QtCore,QtWidgets,QtGui
from PySide6.QtCore import Qt
import threading
import json
import sys    

class myClient(QtWidgets.QWidget):
    def __init__(self):
        super(myClient, self).__init__()

        self.socket = None
        self.dict_clients = {}
        self.list = []
        self.connected = False
        self.ip = socket.gethostbyname(socket.gethostname())

        self.portInput = QtWidgets.QLineEdit()
        self.portInput.setMaxLength(5)
        self.portInput.setAlignment(QtCore.Qt.AlignRight)
        self.portInput.setFont(QtGui.QFont("Arial",20))

        self.clients_list_wdgt = QtWidgets.QListWidget()
        self.clients_list_wdgt.itemClicked.connect(self.onItemClicked)
        self.chat_list_wdgt = QtWidgets.QListWidget()
        self.labelClients = QtWidgets.QLabel("Clientes disponíveis:")
        self.labelChat = QtWidgets.QLabel("Chat:")

        self.inputHost = QtWidgets.QLineEdit()
        self.inputHost.setMaxLength(20)
        self.inputHost.setAlignment(QtCore.Qt.AlignRight)
        self.inputHost.setFont(QtGui.QFont("Arial",20))

        self.button = QtWidgets.QPushButton("Conectar!")

        self.msgInput = QtWidgets.QLineEdit()
        self.msgInput.setMaxLength(35)
        self.msgInput.setAlignment(QtCore.Qt.AlignRight)
        self.msgInput.setFont(QtGui.QFont("Arial",12))

        self.nameInput = QtWidgets.QLineEdit()
        self.nameInput.setMaxLength(15)
        self.nameInput.setAlignment(QtCore.Qt.AlignRight)
        self.nameInput.setFont(QtGui.QFont("Arial",14))

        self.btnSend = QtWidgets.QPushButton("Enviar!")

        self.flo = QtWidgets.QFormLayout()
        self.flo.addRow("IP Host:", self.inputHost)
        self.flo.addRow("Digite a porta:",self.portInput)
        self.flo.addRow("Digite seu nome:",self.nameInput)
        self.flo.addRow("Aperte para iniciar a conexão:",self.button)
       
        self.boxLayout = QtWidgets.QVBoxLayout()
        self.boxLayoutH = QtWidgets.QHBoxLayout()

        self.gridLayoutClients = QtWidgets.QGridLayout()
        self.gridLayoutChat = QtWidgets.QGridLayout()

        self.gridLayoutClients.addWidget(self.labelClients, 0, 0)
        self.gridLayoutClients.addWidget(self.clients_list_wdgt, 1, 0)

        self.gridLayoutChat.addWidget(self.labelChat, 0, 0)
        self.gridLayoutChat.addWidget(self.chat_list_wdgt, 1, 0)

        self.boxLayoutH.addLayout(self.gridLayoutClients)
        self.boxLayoutH.addLayout(self.gridLayoutChat)

        self.boxLayout.addLayout(self.flo)
        self.boxLayout.addLayout(self.boxLayoutH)

        self.setLayout(self.boxLayout)

        self.button.clicked.connect(self.initConnection)

        self.btnSend.clicked.connect(self.sendTextMessage)

        self.setWindowTitle("Chat App")

        self.textStatus = QtWidgets.QLabel()
        self.flo.addWidget(self.textStatus)

    def connect(self):
        self.connected = True

    def initConnection(self):
        self.textStatus.setText("Iniciando conexão...")
        port = self.portInput.text()
        host = self.inputHost.text()
        name = self.nameInput.text()

        if port != "" and host != "" and name != "":
            self.port = port
            self.host = host
            self.name = name
            status = self.init_client()

            if status == 0:
                self.textStatus.setText("Conectado! Envie uma mensagem abaixo...")
                self.flo.removeRow(self.portInput)
                self.flo.removeRow(self.button)
                self.flo.addRow(self.msgInput)
                self.flo.addRow(self.btnSend)
            else:
                self.textStatus.setText("Não foi possível iniciar a conexão! Tente novamente!")
        else: 
            self.textStatus.setText("Por favor, digite o host, a porta e o nome!")
    
    def disconnect(self):
        self.socket.close()
        self.connected = False
        self.dict_clients.clear()

    def init_client(self):
        if not self.connected:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect((self.host, int(self.port)))
                threading.Thread(target=self.receive).start()
                return 0
            except socket.error as e:
                print("Houve um problema ao se conectar ao servidor.")
                return -1
        else:
            self.sendGenericMessage("DISCONNECT",None)
            self.list.clear()

    def sendTextMessage(self):
        if self.msgInput.text() == "":
            self.textStatus.setText("Digite uma mensagem!")
        else:
            message = {
                "ip": self.ip,
                "type": "MESSAGE",
                "name": self.name,
                "content": self.msgInput.text(),
                "clients": self.list
            }

            try:
                self.socket.send(json.dumps(message).encode())
            except Exception as e:
                print(str(e) + " Não foi possível enviar a mensagem para o servidor!")

    def sendGenericMessage(self,flag,content):
            message = {
                "ip": self.ip,
                "type": flag,
                "name": self.name,
                "content": content,
                "clients": self.list
            }

            try:
                self.socket.send(json.dumps(message).encode())
            except Exception as e:
                print(str(e) + "Não foi possível enviar a mensagem para o servidor!")

    def update(self, aList: list):
        if type(aList) == list:
            remove = []
            for i in range(len(self.list)):
                if self.list[i] not in aList:
                    remove.append(self.list[i])

            for item in remove:
                items = self.clients_list_wdgt.findItems(self.dict_clients[item],Qt.MatchExactly)
                if len(items) > 0:
                    self.clients_list_wdgt.takeItem(self.clients_list_wdgt.row(items[0]))

            for client in aList:
                if client[1] is not self.ip:
                    client = tuple(client)
                    if client not in self.dict_clients.keys():
                        item = QtWidgets.QListWidgetItem()
                        item.setText(client[0])
                        item.setToolTip(client[1])
                        item.setCheckState(Qt.Unchecked)
                        self.clients_list_wdgt.addItem(item)
                        self.dict_clients[client[1]] = client[0]

    def receive(self):
        self.sendGenericMessage("CONNECT",None)

        while True:
            try:
                message = json.loads(self.socket.recv(1024))
                if message["type"] == "CONNECTED":
                    self.connect()
                    self.update(message["clients"])
                    item = QtWidgets.QListWidgetItem()
                    item.setText("Conectado ao servidor!")
                    self.chat_list_wdgt.addItem(item)
                elif message["type"] == "MESSAGE":
                    item = QtWidgets.QListWidgetItem()
                    item.setText(message["name"] + ":" + message["content"])
                    self.chat_list_wdgt.addItem(item)
                elif message["type"] == "UPDATE":
                    self.update(message["clients"])
                elif message["type"] == "DISCONNECTED":
                    self.disconnect()
                    item = QtWidgets.QListWidgetItem()
                    item.setText("Desconectado do Servidor!")
                    self.chat_list_wdgt.addItem(item)
                    break
            except Exception as e:
                print(str(e))
                self.disconnect()
                break
    def closeEvent(self, event):
        if self.connected:
            self.sendGenericMessage("DISCONNECT",None)
            self.disconnect()

    def onItemClicked(self, item):
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
            self.list.remove(item.toolTip())
        else:
            item.setCheckState(Qt.Checked)
            if item.toolTip() not in self.list:
                self.list.append(item.toolTip())

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = myClient()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())