# -*- coding: utf-8 -*-
"""
Module of the main window (GUI + Backend).
"""
import re
import time
import datetime

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
from NCryptoTools.JIM.jim_base import JSONObjectType
from NCryptoTools.JIM.jim import JIMManager

from NCryptoClient.UI.ui_chat_tab import UiChat
from NCryptoClient.UI.ui_server_settings_window import UiServerSettingsWindow
from NCryptoClient.Transmitter.client_handler import MsgHandler
from NCryptoClient.UI.ui_main_window import UiMainWindow


class MainWindow(UiMainWindow):
    """
    Class, needed for functioning of the main window.
    """
    def __init__(self):
        """
        Constructor.
        """
        super().__init__()

        # user is not authenticated by default
        self._authenticated = False

        # User login, needed in some child classes
        self._login = 'Anonymous'

        # Gets data from the autoexec.ini
        # self._ip = self._file_manager.instance.get_item(self._file_manager.autoexec_copy_path,
        #                                                 '[Server_information]', 'ip')
        # self._port = self._file_manager.instance.get_item(self._file_manager.autoexec_copy_path,
        #                                                   '[Server_information]', 'port')
        self._ip = '127.0.0.1'
        self._port = '7777'

        self.server_settings_window = None
        self.chat_tab_widget = None
        self.msg_handler = None

    def closeEvent(self, *args, **kwargs):
        """
        Saves all needed data before closing the window.
        @param args: additional arguments (list).
        @param kwargs: additional arguments (dictionary).
        @return: -
        """
        # self._file_manager.save_changes()

        quit_msg = JIMManager.create_jim_object(JSONObjectType.TO_SERVER_QUIT)
        self.msg_handler.write_to_output_buffer(quit_msg.to_dict())
        time.sleep(1)

        # args returns object of closing event
        args[0].accept()

    # ========================================================================
    # Getters & Setters
    # ========================================================================
    def get_auth_state(self):
        """
        Getter. Returns authentication state.
        @return: authentication state.
        """
        return self._authenticated

    def set_auth_state(self, new_state):
        """
        Setter. Sets new authentication state.
        @param new_state: new authentication state.
        @return: -
        """
        self._authenticated = new_state

    def get_login(self):
        """
        Getter. Returns user login.
        @return: current login.
        """
        return self._login

    def set_login(self, new_login):
        """
        Setter. Sets new value to the user login.
        @param new_login:  new login.
        @return: -
        """
        self._login = new_login

    # ========================================================================
    # Methods, related to the chat widget (QTabWidget and its components).
    # ========================================================================
    def open_chat_widget(self):
        """
        Opens chat widget on the right click on the contact.
        @return: -
        """
        if self.chat_tab_widget is None:
            self.select_chat_st.hide()
            self.chat_tab_widget = UiChat(self)

    def open_tab(self, chat_name):
        """
        Opens new chat tab with needed name.
        @param chat_name: chat name.
        @return: -
        """
        self.open_chat_widget()
        self.chat_tab_widget.add_chat_tab(chat_name)

        # TODO: Load last messages to the tab
        # self.request_msg_history(chat_name)

    def close_tab(self, chat_name):
        """
        Closes tab, searching it by name.
        @param chat_name: chat name.
        @return: -
        """
        if self.chat_tab_widget:
            self.chat_tab_widget.close_chat_tab_by_name(chat_name)

    @pyqtSlot(str, str, name='add_log_data')
    def add_log_data(self, time_str, message):
        """
        Adds log message. if log tab is closed, it will be opened automatically.
        @param time_str: time/sender string.
        @param message: data to be added in the Log tab.
        @return: -
        """
        self.open_chat_widget()
        index = self.chat_tab_widget.find_tab('Log')
        if index is None:
            self.open_tab('Log')
            index = self.chat_tab_widget.find_tab('Log')
        self.chat_tab_widget.add_tab_data(index, time_str, message)

    @pyqtSlot(str, str, str, name='add_data_in_tab')
    def add_data_in_tab(self, tab_name, time_str, message):
        """
        Adds message in the needed tab.
        @param tab_name: tab name (chat name).
        @param time_str: time/sender string.
        @param message: message to be added in the tab.
        @return: -
        """
        if self.chat_tab_widget:
            index = self.chat_tab_widget.find_tab(tab_name)
            if index is not None:
                self.chat_tab_widget.add_tab_data(index, time_str, message)

    @pyqtSlot(str, name='self_add_data_in_tab')
    def self_add_data_in_tab(self, tab_name):
        """
        Does pretty much the same as add_data_in_tab(), but being used
        only in case of sending messages.
        @param tab_name: tab name (chat name).
        @return: -
        """
        if self.chat_tab_widget:
            index = self.chat_tab_widget.find_tab(tab_name)
            if index is not None:
                self.chat_tab_widget.add_tab_data_from_buffer(index)

    def request_msg_history(self, chat_name):
        """
        Requests a list of messages from the server for the needed chat.
        After returning the list, client_handler.py will renew GUI by adding
        new messages.
        @param chat_name: tab name (chat name).
        @return: -
        """
        jim_msg = JIMManager.create_jim_object(JSONObjectType.TO_SERVER_GET_MSGS,
                                               datetime.datetime.now().timestamp(),
                                               self._login, chat_name)
        self._client_transmitter.write_to_output_buffer(jim_msg.to_dict())

    # ========================================================================
    # Methods, related to the list of contacts.
    # ========================================================================
    @pyqtSlot(str, name='add_contact')
    def add_contact(self, contact_name):
        """
        Adds new contact in the list of contacts.
        @param contact_name: chat name (contact name) to be added in the list.
        @return: -
        """
        self.contacts_widget.add_contact(contact_name)
        self.search_le.clear()

    @pyqtSlot(str, name='remove_contact')
    def remove_contact(self, contact_name):
        """
        Deletes contact from the list of contacts.
        @param contact_name: chat name (contact name) to be removed from the list.
        @return: -
        """
        self.contacts_widget.delete_contact(contact_name)
        self.search_le.clear()

    def request_contacts_list(self):
        """
        Requests a list of contacts from the server for the needed login.
        After returning the list, client_handler.py will renew GUI by adding
        new contacts.
        @return: -
        """
        jim_msg = JIMManager.create_jim_object(JSONObjectType.TO_SERVER_GET_CONTACTS,
                                               datetime.datetime.now().timestamp())
        self.msg_handler.write_to_output_buffer(jim_msg.to_dict())

    # ========================================================================
    # Methods, related to the server settings window.
    # ========================================================================
    def open_server_settings_window(self):
        """
        Opens server settings window.
        @return: -
        """
        self.server_settings_window = UiServerSettingsWindow(self)
        self.server_settings_window.show()

    # ========================================================================
    # Methods, related to the authentication window.
    # ========================================================================
    def open_authentication_window(self):
        """
        Opens authentication window.
        @return:
        """
        self.init_auth_widgets()

        # Signals
        self.server_settings_pb.clicked.connect(self.open_server_settings_window)
        self.ok_pb.clicked.connect(self.send_auth_data)
        self.clear_pb.clicked.connect(self.clear_data)

        self.msg_handler = MsgHandler(self._ip, self._port)

        # Links QThread signals to the methods of the GUI thread. MsgHandler will
        # emit signals to control the state of GUI objects.
        self.msg_handler.open_chat_signal.connect(self.open_chat_window)
        self.msg_handler.add_contact_signal.connect(self.add_contact)
        self.msg_handler.remove_contact_signal.connect(self.remove_contact)
        self.msg_handler.add_log_signal.connect(self.add_log_data)
        self.msg_handler.add_message_signal.connect(self.add_data_in_tab)
        self.msg_handler.self_add_message_signal.connect(self.self_add_data_in_tab)
        self.msg_handler.show_message_box_signal.connect(self.show_message_box)

        self.msg_handler.start()

    def send_auth_data(self):
        """
        Sends data to the server needed to authenticate in the chat.
        @return: -
        """
        login = self.login_le.text()
        password = self.password_le.text()

        if len(login) < 3:
            self.show_message_box('Warning: invalid data',
                                  'Login length: {}. Expected length: [3;32]'.format(len(login)))
            return

        if len(password) < 4:
            self.show_message_box('Warning: invalid data',
                                  'Password length: {}. Expected length: [4;32]'.format(len(password)))
            return

        auth_msg = JIMManager.create_jim_object(JSONObjectType.TO_SERVER_AUTH,
                                                datetime.datetime.now().timestamp(),
                                                self.login_le.text(),
                                                self.password_le.text())
        self.msg_handler.write_to_output_buffer(auth_msg.to_dict())

    def clear_data(self):
        """
        Clears all QLineEdit widgets.
        @return: -
        """
        self.login_le.clear()
        self.password_le.clear()

    # ========================================================================
    # Methods, related to the chat window.
    # ========================================================================
    @pyqtSlot(name='open_chat_window')
    def open_chat_window(self):
        """
        Opens chat window.
        @return: -
        """
        self._login = self.login_le.text()

        self.logo_l.hide()
        self.login_st.hide()
        self.password_st.hide()
        self.login_le.hide()
        self.password_le.hide()
        self.clear_pb.hide()
        self.ok_pb.hide()

        self.logo_l.deleteLater()
        self.login_st.deleteLater()
        self.password_st.deleteLater()
        self.login_le.deleteLater()
        self.password_le.deleteLater()
        self.clear_pb.deleteLater()
        self.ok_pb.deleteLater()

        self.logo_l = None
        self.login_st = None
        self.password_st = None
        self.login_le = None
        self.password_le = None
        self.clear_pb = None
        self.ok_pb = None

        self.init_chat_widgets()
        self.request_contacts_list()

        # Signals
        self.add_contact_pb.clicked.connect(self.find_and_add_contact)
        self.remove_contact_pb.clicked.connect(self.find_and_remove_contact)
        self.server_item.triggered.connect(self.open_server_settings_window)
        self.exit_item.triggered.connect(self.close)

    def find_and_add_contact(self):
        """
        Searches for contacts and in case of a success adds them in the list.
        @return: -
        """
        search_contact = self.search_le.text()

        re_message = re.compile('^(#[A-Za-z_\d]{3,31}|[A-Za-z_\d]{3,32})$')
        if re.fullmatch(re_message, search_contact) is None:
            self.show_message_box('Incorrect input text!',
                                  'You have entered incorrect text! Requirements:\n' +
                                  '- Chatrooms. Length: [3,31], starts with \'#\'.\n' +
                                  '- Clients. Length: [3,32].')
            return

        # Contact should not exist in the list to be able to add it
        if self.contacts_widget.find_contact_widget(search_contact) is not None:
            self.show_message_box('Contact have not been found!',
                                  'You already have \'{}\' in your list of contacts!'.format(search_contact))
            return

        question_mb = QMessageBox()
        question_mb.setIcon(QMessageBox.Question)
        question_mb.setText('Do you really want to add \'{}\' to your list of contacts?'.format(search_contact))
        question_mb.setWindowTitle('Proceed?')
        question_mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = question_mb.exec_()

        if result == QMessageBox.No:
            return

        # Checks what kind of contact we are trying to find: a chatroom or a person
        if search_contact.startswith('#'):
            msg = JIMManager.create_jim_object(JSONObjectType.TO_SERVER_JOIN_CHAT,
                                               datetime.datetime.now().timestamp(),
                                               self._login, search_contact)
        else:
            msg = JIMManager.create_jim_object(JSONObjectType.TO_SERVER_ADD_CONTACT,
                                               datetime.datetime.now().timestamp(),
                                               search_contact)
        self.msg_handler.write_to_output_buffer(msg.to_dict())

    def find_and_remove_contact(self):
        """
        Searches for contact and and in case of a success deletes it from the list.
        :return: -
        """
        self.remove_contact_by_login(self.search_le.text())

    def remove_contact_by_login(self, contact_name):
        """
        Searches for contact and and in case of a success deletes it from the list.
        @param contact_name: contact name.
        @return:
        """
        re_message = re.compile('^(#[A-Za-z_\d]{3,31}|[A-Za-z_\d]{3,32})$')
        if re.fullmatch(re_message, contact_name) is None:
            self.show_message_box('Incorrect input text!',
                                  'You have entered incorrect text! Requirements:\n' +
                                  '- Chatrooms. Length: [3,31], starts with \'#\'.\n' +
                                  '- Clients. Length: [3,32].')
            return

        # Contact should be in our list to be deleted
        if self.contacts_widget.find_contact_widget(contact_name) is None:
            self.show_message_box('Contact have not been found!',
                                  'You do not have \'{}\' in your list of contacts!'.format(contact_name))
            return

        question_mb = QMessageBox()
        question_mb.setIcon(QMessageBox.Question)
        question_mb.setText('Do you really want to remove \'{}\' from your list of contacts?'.format(contact_name))
        question_mb.setWindowTitle('Proceed?')
        question_mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = question_mb.exec_()

        if result == QMessageBox.No:
            return

        # Checks what kind of contact we are trying to find: a chatroom or a person
        if contact_name.startswith('#'):
            msg = JIMManager.create_jim_object(JSONObjectType.TO_SERVER_LEAVE_CHAT,
                                               datetime.datetime.now().timestamp(),
                                               self._login, contact_name)
        else:
            msg = JIMManager.create_jim_object(JSONObjectType.TO_SERVER_DEL_CONTACT,
                                               datetime.datetime.now().timestamp(),
                                               contact_name)
        self.msg_handler.write_to_output_buffer(msg.to_dict())

    @pyqtSlot(str, str, name='show_message_box')
    def show_message_box(self, window_title, msg_text):
        """
        Shows message box with needed inscriptions.
        @param window_title: title inscription.
        @param msg_text: message text.
        @return: -
        """
        warning_mb = QMessageBox(self)
        warning_mb.setWindowTitle(window_title)
        warning_mb.setText(msg_text)
        warning_mb.setStandardButtons(QMessageBox.Ok)
        warning_mb.exec_()
