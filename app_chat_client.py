import socket
from PySide6 import QtCore,QtWidgets,QtGui
import threading
import sys

class threadClient(threading.Thread):
    def __init__(self, thread_name, thread_ID,connection):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.connection = connection

    def run(self):
        data = self.connection.recv(2048)
        response = 'Server message: ' + data.decode('utf-8')
        self.connection.sendall(str.encode(response))

class myClient:
    def __init__(self,port,host):
        self.port = int(port)
        self.host = host

    def init_client(self):
        self.clientMultiSocket = socket.socket()
        try:
            self.clientMultiSocket.connect((self.host, self.port))
            return 0
        except socket.error as e:
            return 1

    def sendMessage(self,message):
        try:
            self.clientMultiSocket.send(str.encode(message))
        except Exception as e:
            print(e)

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.portInput = QtWidgets.QLineEdit()
        self.portInput.setMaxLength(5)
        self.portInput.setAlignment(QtCore.Qt.AlignRight)
        self.portInput.setFont(QtGui.QFont("Arial",20))

        self.inputHost = QtWidgets.QLineEdit()
        self.inputHost.setMaxLength(20)
        self.inputHost.setAlignment(QtCore.Qt.AlignRight)
        self.inputHost.setFont(QtGui.QFont("Arial",20))

        self.button = QtWidgets.QPushButton("Conectar!")

        self.msgInput = QtWidgets.QLineEdit()
        self.msgInput.setMaxLength(35)
        self.msgInput.setAlignment(QtCore.Qt.AlignRight)
        self.msgInput.setFont(QtGui.QFont("Arial",12))

        self.btnSend = QtWidgets.QPushButton("Enviar!")

        self.flo = QtWidgets.QFormLayout()
        self.flo.addRow("IP Host:", self.inputHost)
        self.flo.addRow("Digite a porta:",self.portInput)
        self.flo.addRow("Aperte para iniciar a conexão:",self.button)

        self.setLayout(self.flo)

        self.button.clicked.connect(self.initConnection)

        self.btnSend.clicked.connect(self.sendMessage)

        self.setWindowTitle("Chat App")

        self.textStatus = QtWidgets.QLabel()
        self.flo.addWidget(self.textStatus)

    @QtCore.Slot()
    def initConnection(self):
        self.textStatus.setText("Iniciando conexão...")
        port = self.portInput.text()
        host = self.inputHost.text()
        if port != "" and host != "":
            self.myClientInst = myClient(port,host)
            status = self.myClientInst.init_client()

            if status == 0:
                self.textStatus.setText("Conectado! Envie uma mensagem abaixo...")
                self.flo.removeRow(self.portInput)
                self.flo.removeRow(self.button)
                self.flo.addRow(self.msgInput)
                self.flo.addRow(self.btnSend)
            else:
                self.textStatus.setText("Não foi possível iniciar a conexão! Tente novamente!")
        else: 
            self.textStatus.setText("Por favor, digite o host e a porta!")
    
    def sendMessage(self):
        if self.msgInput.text() == "":
            self.textStatus.setText("Digite uma mensagem!")
        else:
            self.myClientInst.sendMessage(self.msgInput.text())

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())