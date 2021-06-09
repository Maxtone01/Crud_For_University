from PyQt5.QtWidgets import *
global _connection


class PreDialog(QDialog):
    """
    Class, that was built to create Pre Dialog window, that will start every time while person will open program.
    """
    def __init__(self, *args, **kwargs):
        """
        Defined some basic window settings.

        :param args:
        :param kwargs:
        """
        super(PreDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle('Host Parameters')
        self.setModal(True)
        self.line_host = QLineEdit()
        _connect = QPushButton("connect")
        self.spinBox_port = QSpinBox()
        self.spinBox_port.setProperty("value", 3311)
        self.hbox = QHBoxLayout()
        self.spinBox_port.setMaximum(10000)

        self.form = QFormLayout()
        self.form.setSpacing(20)

        self.form.addRow("&Host:",self.line_host)
        self.form.addRow("&Port:",self.spinBox_port)
        self.form.addRow(_connect)
        _connect.clicked.connect(self.close)

        self.setLayout(self.form)

    def get_host(self):
        """
        Getting host information that user was written.

        :return: host information
        """
        _host = self.line_host.text()
        _file = open('connection.txt', 'w', encoding='utf-8')
        _file.write(_host + '\n')
        _file.close()
        return _host

    def get_port(self):
        """
        Getting port information that user was written.

        :return: port information
        """
        _port = self.spinBox_port.text()
        _file = open('connection.txt', 'a', encoding='utf-8')
        _file.write(_port + '\n')
        _file.close()
        return _port

    def closeEvent(self, event):
        """
        Closing window after user finished entering data.

        :param event: PreDialog window event
        :return:
        """
        self.close()