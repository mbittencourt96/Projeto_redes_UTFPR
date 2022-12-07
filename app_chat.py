import sys
import random
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
            print('Socket is listening..')
            self.serverSideSocket.listen()
        except socket.error as e:
            print(str(e))

    def multi_threaded_client(self,connection):
        connection.send(str.encode('Server is working:'))
        while True:
            data = connection.recv(2048)
            response = 'Server message: ' + data.decode('utf-8')
            if not data:
                break
            connection.sendall(str.encode(response))
        connection.close()

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
            myServerInst.init_server()
        else: 
            self.textStatus.setText("Por favor, digite a porta!")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())