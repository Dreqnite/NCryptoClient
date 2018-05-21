# -*- coding: utf-8 -*-
"""
Module for the window which appears when user chooses:
"NCryptoChat" -> "Options" -> "Server"
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from Solution.NCryptoClient.Utils.client_file_manager import ClientFileManager


class UiServerSettingsWindow(QDialog):
    """
    UI-class, which is needed for the server connection customization.
    """
    def __init__(self, parent):
        """
        Constructor.
        @param parent: reference to the parent window.
        """
        super(UiServerSettingsWindow, self).__init__(parent)

        # self._file_manager = ClientFileManager()

        self.setObjectName('server_settings_window')
        self.resize(256, 136)

        # Static text "IPv4"
        self.ip_st = QLabel(self)
        self.ip_st.setGeometry(QRect(16, 16, 64, 24))
        self.ip_st.setAlignment(Qt.AlignCenter)
        self.ip_st.setAlignment(Qt.AlignVCenter)
        self.ip_st.setObjectName('ip_st')

        # Static text "Port"
        self.port_st = QLabel(self)
        self.port_st.setGeometry(QRect(16, 56, 64, 24))
        self.port_st.setAlignment(Qt.AlignCenter)
        self.ip_st.setAlignment(Qt.AlignVCenter)
        self.port_st.setObjectName('port_st')

        # IPv4 EditBox
        self.ip_le = QLineEdit(self)
        self.ip_le.setGeometry(QRect(80, 16, 96, 24))
        self.ip_le.setMaxLength(15)
        self.ip_le.setAlignment(Qt.AlignCenter)
        self.ip_le.setObjectName('ip_le')

        # Ipv4 EditBox input limitations
        re_ip = QRegExp('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}' +
                        '([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
        ip_validator = QRegExpValidator(re_ip)
        self.ip_le.setValidator(ip_validator)

        # Port number EditBox
        self.port_le = QLineEdit(self)
        self.port_le.setGeometry(QRect(80, 56, 96, 24))
        self.port_le.setMaxLength(5)
        self.port_le.setAlignment(Qt.AlignCenter)
        self.port_le.setObjectName('port_le')

        # Port number EditBox input limitations
        re_port = QRegExp('^(102[3-9]|1[3-9][0-9]{2}|[2-9][0-9]{3}|[1-5][0-9]{4}' +
                          '|6[0-4][0-9]{3}|655[0-2][0-9]|6553[0-5])$')
        port_validator = QRegExpValidator(re_port)
        self.port_le.setValidator(port_validator)

        # "OK" button
        self.ok_pb = QPushButton(self)
        self.ok_pb.setGeometry(QRect(176, 96, 64, 24))
        self.ok_pb.setObjectName('ok_pb')
        # TODO:
        self.ok_pb.setDisabled(True)

        # "Cancel" button
        self.cancel_pb = QPushButton(self)
        self.cancel_pb.setGeometry(QRect(96, 96, 64, 24))
        self.cancel_pb.setObjectName('cancel_pb')

        # "Default" button
        self.default_pb = QPushButton(self)
        self.default_pb.setGeometry(QRect(16, 96, 64, 24))
        self.default_pb.setObjectName('default_pb')

        self._retranslate_ui()
        self._create_signals()

    def _create_signals(self):
        """
        Creates signals.
        @return: -
        """
        self.ok_pb.clicked.connect(self._ok_clicked)
        self.cancel_pb.clicked.connect(self._cancel_clicked)
        self.default_pb.clicked.connect(self._default_clicked)

    def _ok_clicked(self):
        """
        Accepts all changes which have been done by user, saving them
        in the file controlling by the file manager.
        @return: -
        """
        ip = self.ip_le.text()
        port = self.port_le.text()
        self._file_manager.instance.set_item(self._file_manager.autoexec_copy_path,
                                             '[Server_information]', 'ip', ip)
        self._file_manager.instance.set_item(self._file_manager.autoexec_copy_path,
                                             '[Server_information]', 'port', port)
        self.close()

    def _cancel_clicked(self):
        """
        Cancels all changes, done by user.
        @return: -
        """
        self.close()

    def _default_clicked(self):
        """
        Sets IPv4 and port default values.
        @return: -
        """
        self.ip_le.setText("127.0.0.1")
        self.port_le.setText("7777")

    def _retranslate_ui(self):
        """
        Sets inscriptions on the all GUI elements.
        @return: -
        """
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate('server_settings_window', 'Server Settings'))
        self.ip_st.setText(_translate('server_settings_window', 'IPv4:'))
        self.port_st.setText(_translate('server_settings_window', 'Port:'))
        self.ok_pb.setText(_translate('server_settings_window', 'OK'))
        self.cancel_pb.setText(_translate('server_settings_window', 'Cancel'))
        self.default_pb.setText(_translate('server_settings_window', 'Default'))
        self.ip_le.setText('127.0.0.1')
        self.port_le.setText('7777')
        # TODO:
        # self.ip_le.setText(self._file_manager.instance.get_item(self._file_manager.autoexec_copy_path,
        #                                                         '[Server_information]', 'ip'))
        # self.port_le.setText(self._file_manager.instance.get_item(self._file_manager.autoexec_copy_path,
        #                                                           '[Server_information]', 'port'))



