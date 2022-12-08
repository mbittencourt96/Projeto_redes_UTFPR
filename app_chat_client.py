import socket
from PySide6 import QtCore,QtWidgets,QtGui

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
        self.clientMultiSocket.send(str.encode(message))

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.portInput = QtWidgets.QLineEdit()
        self.portInput.setMaxLength(5)
        self.portInput.setAlignment(QtCore.Qt.AlignRight)
        self.portInput.setFont(QtGui.QFont("Arial",20))

        self.host = "192.168.15.81"    #Mariana's PC

        self.labelHost = QtWidgets.QLabel(self.host)

        self.button = QtWidgets.QPushButton("Conectar!")

   
        self.flo = QtWidgets.QFormLayout()
        self.flo.addRow("IP Host:", self.labelHost)
        self.flo.addRow("Digite a porta:",self.portInput)
        self.flo.addRow("Aperte para iniciar a conexão:",self.button)

        self.setLayout(self.flo)

        self.button.clicked.connect(self.initConnection)

        self.setWindowTitle("Chat App")

        self.textStatus = QtWidgets.QLabel()
        self.flo.addWidget(self.textStatus)

    @QtCore.Slot()
    def initConnection(self):
        self.textStatus.setText("Iniciando conexão...")
        port = self.portInput.text()
        if port != "":
            myClientInst = myClient(port,self.host)
            status = myClientInst.init_client()

            if status == 0:
                self.textStatus.setText("Conectado! Envie uma mensagem abaixo...")
                self.flo.removeRow(self.portInput)
                self.flo.removeRow(self.button)
            else:
                self.textStatus.setText("Não foi possível iniciar a conexão! Tente novamente!")
        else: 
            self.textStatus.setText("Por favor, digite a porta!")