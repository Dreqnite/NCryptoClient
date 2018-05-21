# -*- coding: utf-8 -*-
"""
Модуль для обработчика входящих сообщений.
"""
import re
import time
import socket

from PyQt5.QtCore import *
from NCryptoTools.Tools.utilities import get_formatted_date, get_current_time
from NCryptoTools.JIM.jim import JIMManager
from NCryptoTools.JIM.jim_base import JSONObjectType, UnknownJSONObjectType

from NCryptoClient.client_instance_holder import client_holder
from NCryptoClient.Transmitter.client_receiver import Receiver
from NCryptoClient.Transmitter.client_sender import Sender


class MsgHandler(QThread):
    """
    Thread-class for handling of the input, coming from the server.
    It reads the data from the buffer, defines its type and performs needed
    actions depending on the message type. This class was intentionally
    created to reduce time needed for Receiver thread to handle messages -
    now it just stores incoming messages in the buffer. All handling work is
    done by this thread.
    """
    add_contact_signal = pyqtSignal(str)
    remove_contact_signal = pyqtSignal(str)
    add_message_signal = pyqtSignal(str, str, str)
    add_log_signal = pyqtSignal(str, str)
    self_add_message_signal = pyqtSignal(str)
    show_message_box_signal = pyqtSignal(str, str)
    open_chat_signal = pyqtSignal()

    def __init__(self,
                 ipv4_address,
                 port_number,
                 socket_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 wait_time=0.05):
        """
        Конструктор.
        @param ipv4_address: IPv4 address of server.
        @param port_number: port number.
        @param socket_family: socket family.
        @param socket_type: socket type.
        @param wait_time: wait time in seconds to avoid overheating.
        """
        super().__init__()
        self.daemon = True
        self._socket = socket.socket(socket_family, socket_type)
        self._socket.connect((ipv4_address, int(port_number)))
        self._wait_time = wait_time
        self._main_window = None
        self._sender = Sender(self._socket)
        self._receiver = Receiver(self._socket)

    def __del__(self):
        """
        Destructor. Closes the connection with the server.
        @return: -
        """
        self._socket.close()

    def run(self):
        """
        Runs thread routine.
        @return: -
        """
        self._main_window = client_holder.get_instance('MainWindow')

        self._sender.start()
        self._receiver.start()

        while True:
            msg_dict = self._receiver.pop_msg_from_queue()
            if msg_dict is not None:
                self._handle_message(msg_dict)
            time.sleep(self._wait_time)

    def write_to_output_buffer(self, msg_dict):
        """
        Writes JSON-object to the output buffer of the Sender thread.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        self._sender.add_msg_to_queue(msg_dict)

    def _handle_message(self, msg_dict):
        """
        Handles input messages and performs actions depending on the
        message type.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        try:
            json_object_type = JIMManager.determine_jim_msg_type(msg_dict)
        except UnknownJSONObjectType:
            return

        # User wrote personal message to the current client
        if json_object_type == JSONObjectType.TO_SERVER_PERSONAL_MSG:
            self._server_to_client_personal_msg(msg_dict)

        # Server sent information, that another user has written a message to the chatroom
        elif json_object_type == JSONObjectType.TO_SERVER_CHAT_MSG:
            self._server_to_client_chat_msg(msg_dict)

        # Server sent information, that another user joined the chatroom
        elif json_object_type == JSONObjectType.TO_SERVER_JOIN_CHAT:
            self._server_to_client_join_chat(msg_dict)

        # Server sent information, that another user left the chatroom
        elif json_object_type == JSONObjectType.TO_SERVER_LEAVE_CHAT:
            self._server_to_client_leave_chat(msg_dict)

        # Server sent information about the amount of contacts in the client's list
        elif json_object_type == JSONObjectType.TO_CLIENT_QUANTITY:
            self._server_to_client_quantity(msg_dict)

        # Server sent information about the next client in the client's list
        elif json_object_type == JSONObjectType.TO_CLIENT_CONTACT_LIST:
            self._server_to_client_contact_list(msg_dict)

        # Server sent an ordinary answer to the client regarding his previous action
        elif json_object_type == JSONObjectType.TO_CLIENT_INFO:
            self._server_to_client_alert(msg_dict)

        # Server sent a error/critical message
        elif json_object_type == JSONObjectType.TO_CLIENT_ERROR:
            self._server_to_client_error(msg_dict)

    # ========================================================================
    # A group of protected methods, each of which is charge of message handling
    # of a specific type.
    # ========================================================================
    def _server_to_client_personal_msg(self, msg_dict):
        """
        Handles personal message from a client.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        time_str = '[{}] @{}>'.format(get_formatted_date(msg_dict['time']),
                                      msg_dict['from'])
        self.add_message_signal.emit(msg_dict['from'], time_str, msg_dict['message'])

    def _server_to_client_chat_msg(self, msg_dict):
        """
        Handles message to the chat from a client.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        time_str = '[{}] @{}>'.format(get_formatted_date(msg_dict['time']),
                                      msg_dict['from'])
        self.add_message_signal.emit(msg_dict['to'], time_str, msg_dict['message'])

    def _server_to_client_join_chat(self, msg_dict):
        """
        Handles message from the server that another client has joined a chatroom.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        time_str = '[{}] @Server>'.format(get_formatted_date(msg_dict['time']))
        msg_string = '{} joined {} chatroom.'.format(msg_dict['login'],
                                                     msg_dict['room'])
        self.add_message_signal.emit(msg_dict['room'], time_str, msg_string)

    def _server_to_client_leave_chat(self, msg_dict):
        """
        Handles message from the server that another client has left a chatroom.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        time_str = '[{}] @Server>'.format(get_formatted_date(msg_dict['time']))
        msg_string = '{} left {} chatroom.'.format(msg_dict['login'],
                                                   msg_dict['room'])
        self.add_message_signal.emit(msg_dict['room'], time_str, msg_string)

    def _server_to_client_quantity(self, msg_dict):
        """
        Handles message with amount of contacts of the current client.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        time_str = '[{}] @Server>'.format(get_current_time())
        alert_msg = 'Amount of contacts: {}'.format(msg_dict['quantity'])
        self.add_log_signal.emit(time_str, alert_msg)

    def _server_to_client_contact_list(self, msg_dict):
        """
        Handles message with the next login of client's contact.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        self.add_contact_signal.emit(msg_dict['login'])

    def _server_to_client_alert(self, msg_dict):
        """
        Handles an ordinary answer from the server (response).
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        if str(msg_dict['response'])[0] in ['1', '2']:

            # Defines where to send the data
            if self._main_window.get_auth_state():
                time_str = '[{}] @Server>'.format(get_current_time())
                alert_msg = 'Alert {}: {}'.format(msg_dict['response'],
                                                  msg_dict['alert'])

                self.add_log_signal.emit(time_str, alert_msg)

                self._handle_alert_message(msg_dict['alert'])

            # if user is not logged in, checks the code
            else:
                if msg_dict['response'] == 200:
                    self._main_window.set_auth_state(True)
                    self.open_chat_signal.emit()

    def _server_to_client_error(self, msg_dict):
        """
        Handles error message from the server (response).
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        if str(msg_dict['response'])[0] in ['4', '5']:

            # Defines where to send the data
            if self._main_window.get_auth_state():
                time_str = '[{}] @Server>'.format(get_current_time())
                error_msg = 'Error {}: {}'.format(msg_dict['response'],
                                                  msg_dict['error'])
                self.add_log_signal.emit(time_str, error_msg)

            # if user is not logged in, checks the code
            else:
                if msg_dict['response'] == 401:
                    self.show_message_box_signal.emit('Invalid authentication data!',
                                                      'Authentication has failed! Try again!')
                else:
                    self.show_message_box_signal.emit('Unknown error!',
                                                      'An unknown error has occured! Try again!')

    def _handle_alert_message(self, message_text):
        """
        Parses message text to define what kind of operation should be performed.
        @param message_text: message text.
        @return: -
        """
        re_message = re.compile('^(Message to \'(#[A-Za-z_\d]{3,31}|[A-Za-z_\d]{3,32})\' has been delivered!)$')
        if re.fullmatch(re_message, message_text) is not None:
            recipient = message_text.split('\'')[1]
            self.self_add_message_signal.emit(recipient)
            return

        re_joined = re.compile('^(You have joined \'#[A-Za-z_\d]{3,31}\' chatroom!)$')
        if re.fullmatch(re_joined, message_text) is not None:
            contact_name = message_text.split('\'')[1]
            self.add_contact_signal.emit(contact_name)
            return

        re_left = re.compile('^(You have left \'#[A-Za-z_\d]{3,31}\' chatroom!)$')
        if re.fullmatch(re_left, message_text) is not None:
            contact_name = message_text.split('\'')[1]
            self.remove_contact_signal.emit(contact_name)
            return

        re_added = re.compile(
            '^(Contact \'((#[A-Za-z_\d]{3,31})|([A-Za-z_\d]{3,32}))\' has been successfully added!)$')
        if re.fullmatch(re_added, message_text) is not None:
            contact_name = message_text.split('\'')[1]
            self.add_contact_signal.emit(contact_name)
            return

        re_removed = re.compile(
            '^(Contact \'((#[A-Za-z_\d]{3,31})|([A-Za-z_\d]{3,32}))\' has been successfully removed!)$')
        if re.fullmatch(re_removed, message_text) is not None:
            contact_name = message_text.split('\'')[1]
            self.remove_contact_signal.emit(contact_name)
            return

        self.show_message_box_signal.emit('Incorrect message format!',
                                          'Could not parse message from the server!')
