import sys
from _thread import *
from PySide6 import QtCore,QtWidgets,QtGui
import socket

class myServer:
    def __init__(self,port,host):
        self.port = int(port)
        self.host = host

    def init_server(self):
        self.serverSideSocket = socket.socket()
        self.ThreadCount = 0
        try:
            self.serverSideSocket.bind((self.host, self.port))
            self.serverSideSocket.listen()
            return 0
        except socket.error as e:
            return -1

    def multi_threaded_client(self,connection):
        while True:
            data = connection.recv(2048)
            response = 'Server message: ' + data.decode('utf-8')
            if not data:
                break
            connection.sendall(str.encode(response))
        connection.close()

    def acceptConnection(self):
        while True:
            Client, address = self.serverSideSocket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(self.multi_threaded_client, (Client, ))
            ThreadCount += 1
            print('Thread Number: ' + str(ThreadCount))

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.portInput = QtWidgets.QLineEdit()
        self.portInput.setMaxLength(5)
        self.portInput.setAlignment(QtCore.Qt.AlignRight)
        self.portInput.setFont(QtGui.QFont("Arial",20))

        hostname = socket.gethostname() 
        self.host = socket.gethostbyname(hostname) 

        self.labelHost = QtWidgets.QLabel(self.host)

        self.button = QtWidgets.QPushButton("Iniciar servidor!")

   
        self.flo = QtWidgets.QFormLayout()
        self.flo.addRow("IP Host:", self.labelHost)
        self.flo.addRow("Digite a porta:",self.portInput)
        self.flo.addRow("Aperte para iniciar:",self.button)

        self.setLayout(self.flo)

        self.button.clicked.connect(self.initServer)

        self.setWindowTitle("Chat App")

        self.textStatus = QtWidgets.QLabel()
        self.flo.addWidget(self.textStatus)

    @QtCore.Slot()
    def initServer(self):
        self.textStatus.setText("Iniciando servidor...")
        port = self.portInput.text()
        if port != "":
            myServerInst = myServer(port,self.host)
            status = myServerInst.init_server()

            if status == 0:
                self.textStatus.setText("Servidor OK! Aguardando clientes...")
                self.flo.removeRow(self.portInput)
                self.flo.removeRow(self.button)
                myServerInst.acceptConnection()
            else:
                self.textStatus.setText("Não foi possível iniciar o servidor! Tente novamente!")
        else: 
            self.textStatus.setText("Por favor, digite a porta!")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())