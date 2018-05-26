# -*- coding: utf-8 -*-
"""
Module for the main window.
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from NCryptoClient.ui.ui_contacts_list import UiContactsList
from NCryptoClient.utils.client_file_manager import ClientFileManager
from NCryptoClient.utils.constants import NCRYPTOLOGO_IMG_PATH, ADD_CONTACT_IMG_PATH, REMOVE_CONTACT_IMG_PATH


class UiMainWindow(QMainWindow):
    """
    GUI-class of the main window.
    """
    def __init__(self, parent=None):
        """
        Constructor. Initializes all GUI-elements.
        @param parent: reference to the parent window.
        """
        super(UiMainWindow, self).__init__(parent)

        # self._file_manager = ClientFileManager()

        self.setObjectName('NCryptoClient')

        self.size_policy = QSizePolicy(QSizePolicy.Preferred,
                                       QSizePolicy.Preferred)
        self.size_policy.setHorizontalStretch(0)
        self.size_policy.setVerticalStretch(0)
        self.size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        # Main panel of client window
        self.background_panel = QWidget(self)
        self.background_panel.setObjectName('background_panel')
        self.setCentralWidget(self.background_panel)

        # Main font
        self.inscription_font = QFont()
        self.inscription_font.setFamily('Adobe Caslon Pro Bold')
        self.inscription_font.setBold(True)
        self.inscription_font.setWeight(75)
        self.inscription_font.setPointSize(14)

        # Font for big inscriptions
        self.big_inscription_font = QFont()
        self.big_inscription_font.setFamily('Adobe Caslon Pro Bold')
        self.big_inscription_font.setBold(True)
        self.big_inscription_font.setWeight(75)
        self.big_inscription_font.setPointSize(18)

        # GUI of the activation window
        self.logo_l = None
        self.login_st = None
        self.password_st = None
        self.login_le = None
        self.password_le = None
        self.server_settings_pb = None
        self.clear_pb = None
        self.ok_pb = None

        # GUI the chat window
        self.search_le = None
        self.add_contact_pb = None
        self.remove_contact_pb = None
        self.contacts_widget = None
        self.select_chat_st = None
        self.contacts_st = None
        self.menu_bar = None
        self.menu_superchat = None
        self.options_menu = None
        self.status_bar = None
        self.server_item = None
        self.about_item = None
        self.help_item = None
        self.exit_item = None

        self._center_window()

    def init_auth_widgets(self):
        """
        Initializes authentication window GUI elements.
        @return: -
        """
        self.setFixedSize(QSize(782, 382))

        self.logo_l = QLabel(self.background_panel)
        self.logo_l.setPixmap(QPixmap(NCRYPTOLOGO_IMG_PATH))
        self.logo_l.setGeometry(16, 16, 750, 206)

        # Static text "Login"
        self.login_st = QLabel(self.background_panel)
        self.login_st.setGeometry(QRect(16, 238, 103, 32))
        self.login_st.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.login_st.setObjectName('login_st')
        self.login_st.setFont(self.inscription_font)

        # Static text "Password"
        self.password_st = QLabel(self.background_panel)
        self.password_st.setGeometry(QRect(16, 286, 103, 32))
        self.password_st.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.password_st.setObjectName('password_st')
        self.password_st.setFont(self.inscription_font)

        # Login EditBox
        self.login_le = QLineEdit(self.background_panel)
        self.login_le.setGeometry(QRect(135, 238, 512, 32))
        self.login_le.setMaxLength(32)
        self.login_le.setAlignment(Qt.AlignCenter)
        self.login_le.setObjectName('login_le')
        login_font = self.login_le.font()
        login_font.setPointSize(12)
        self.login_le.setFont(login_font)

        # Login should be in between 3 and 32 characters
        re_login = QRegExp('^(.{3,32})$')
        login_validator = QRegExpValidator(re_login)
        self.login_le.setValidator(login_validator)

        # Password EditBox
        self.password_le = QLineEdit(self.background_panel)
        self.password_le.setGeometry(QRect(135, 286, 512, 32))
        self.password_le.setMaxLength(32)
        self.password_le.setAlignment(Qt.AlignCenter)
        self.password_le.setObjectName('password_le')
        self.password_le.setEchoMode(QLineEdit.Password)
        password_font = self.password_le.font()
        password_font.setPointSize(12)
        self.password_le.setFont(password_font)

        # Login should be in between 8 and 32 characters
        re_password = QRegExp('^(.{8,32})$')
        password_validator = QRegExpValidator(re_password)
        self.password_le.setValidator(password_validator)

        # "Server Settings" button
        self.server_settings_pb = QPushButton(self.background_panel)
        self.server_settings_pb.setGeometry(QRect(135, 334, 160, 32))
        self.server_settings_pb.setObjectName('server_settings_pb')
        # TODO:
        self.server_settings_pb.setDisabled(True)

        # "Clear" button
        self.clear_pb = QPushButton(self.background_panel)
        self.clear_pb.setGeometry(QRect(311, 334, 160, 32))
        self.clear_pb.setObjectName('clear_pb')

        # "OK" button
        self.ok_pb = QPushButton(self.background_panel)
        self.ok_pb.setGeometry(QRect(487, 334, 160, 32))
        self.ok_pb.setObjectName('ok_pb')

        self._center_window()

        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate('NCryptoClient', 'NCryptoChat'))
        self.login_st.setText(_translate('NCryptoClient', 'Login:'))
        self.password_st.setText(_translate('NCryptoClient', 'Password:'))
        self.server_settings_pb.setText(_translate('NCryptoClient', 'Server Settings'))
        self.ok_pb.setText(_translate('NCryptoClient', 'OK'))
        self.clear_pb.setText(_translate('NCryptoClient', 'Clear'))

    def init_chat_widgets(self):
        """
        Initializes chat window GUI elements.
        @return: -
        """
        self.setFixedSize(QSize(1000, 904))

        # Static text above the list of contacts
        self.contacts_st = QLabel(self.background_panel)
        self.contacts_st.setEnabled(True)
        self.contacts_st.setGeometry(QRect(8, 8, 312, 24))
        self.contacts_st.setSizePolicy(self.size_policy)
        self.contacts_st.setFont(self.inscription_font)
        self.contacts_st.setAlignment(Qt.AlignCenter)
        self.contacts_st.setObjectName('contacts_st')
        self.contacts_st.show()

        # Search EditBox
        self.search_le = QLineEdit(self.background_panel)
        self.search_le.setGeometry(QRect(8, 40, 248, 24))
        self.search_le.setMaxLength(32)
        self.search_le.setAlignment(Qt.AlignCenter)
        self.search_le.setObjectName('search_le')
        self.search_le.show()

        # "Add" button
        self.add_contact_pb = QPushButton(self.background_panel)
        self.add_contact_pb.setGeometry(QRect(264, 40, 24, 24))
        self.add_contact_pb.setObjectName('add_contact_pb')
        self.add_contact_pb.setIcon(QIcon(ADD_CONTACT_IMG_PATH))
        self.add_contact_pb.show()

        # "Delete" button
        self.remove_contact_pb = QPushButton(self.background_panel)
        self.remove_contact_pb.setGeometry(QRect(296, 40, 24, 24))
        self.remove_contact_pb.setObjectName('remove_contact_pb')
        self.remove_contact_pb.setIcon(QIcon(REMOVE_CONTACT_IMG_PATH))
        self.remove_contact_pb.show()

        # Contacts list widget
        self.contacts_widget = UiContactsList(self, self.background_panel)
        self.contacts_widget.setGeometry(QRect(8, 72, 312, 784))
        self.contacts_widget.show()

        # Inscription when all chats are closed:
        # "Select chat to start messaging..."
        self.select_chat_st = QLabel(self.background_panel)
        self.select_chat_st.setGeometry(QRect(328, 416, 656, 32))

        # Font for the above inscription
        self.select_chat_st.setFont(self.big_inscription_font)
        self.select_chat_st.setAlignment(Qt.AlignCenter)
        self.select_chat_st.setObjectName('select_chat_st')
        self.select_chat_st.show()

        # Menu panel
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setGeometry(QRect(0, 0, 1000, 21))
        self.menu_bar.setObjectName('menu_bar')

        # "File" menu
        self.menu_superchat = QMenu(self.menu_bar)
        self.menu_superchat.setObjectName('menu_superchat')

        # Menu item: "File" -> "Options"
        self.options_menu = QMenu(self.menu_superchat)
        self.options_menu.setObjectName('options_menu')

        self.setMenuBar(self.menu_bar)

        # Status bar
        self.status_bar = QStatusBar(self)
        self.status_bar.setObjectName('status_bar')
        self.setStatusBar(self.status_bar)

        # Menu item: "SuperChat" -> "Options" -> "Server"
        self.server_item = QAction('Server', self)
        self.server_item.setObjectName('server_item')

        # Menu item: "SuperChat" -> "About"
        self.about_item = QAction('About', self)
        self.about_item.setObjectName('about_item')

        # Menu item: "SuperChat" -> "Help"
        self.help_item = QAction('Help', self)
        self.help_item.setObjectName('help_item')

        # Menu item: "SuperChat" -> "Exit"
        self.exit_item = QAction('Exit', self)
        self.exit_item.setObjectName('exit_item')

        # Adds items to the menu
        self.menu_bar.addMenu(self.menu_superchat)
        self.menu_superchat.addAction(self.options_menu.menuAction())
        self.menu_superchat.addAction(self.about_item)
        self.menu_superchat.addAction(self.help_item)
        self.menu_superchat.addSeparator()
        self.menu_superchat.addAction(self.exit_item)
        self.options_menu.addAction(self.server_item)

        self._center_window()

        _translate = QCoreApplication.translate
        self.select_chat_st.setText(_translate('NCryptoClient',
                                               'Please select a chat to start messaging'))
        self.contacts_st.setText(_translate('NCryptoClient', 'Your list of contacts'))
        self.menu_superchat.setTitle(_translate('NCryptoClient', 'NCryptoChat'))
        self.options_menu.setTitle(_translate('NCryptoClient', 'Options'))
        self.server_item.setText(_translate('NCryptoClient', 'Server'))
        self.help_item.setText(_translate('NCryptoClient', 'Help'))
        self.about_item.setText(_translate('NCryptoClient', 'About'))
        self.exit_item.setText(_translate('NCryptoClient', 'Exit'))
        self.server_item.setText(_translate('NCryptoClient', 'Server'))

    def _center_window(self):
        """
        Centers window on the monitor.
        @return: -
        """
        resolution = QDesktopWidget().screenGeometry()
        x = (resolution.width() / 2) - (self.frameSize().width() / 2)
        y = (resolution.height() / 2) - (self.frameSize().height() / 2)
        self.move(x, y)
