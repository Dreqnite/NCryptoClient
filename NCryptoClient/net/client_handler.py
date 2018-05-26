# -*- coding: utf-8 -*-
"""
Module which handles messages.
"""
import re
import time
import socket

from PyQt5.QtCore import *
from NCryptoTools.tools.utilities import get_formatted_date, get_current_time
from NCryptoTools.jim.jim_constants import JIMMsgType, HTTPCode
from NCryptoTools.jim.jim_core import to_dict, type_of, is_valid_msg

from NCryptoClient.client_instance_holder import client_holder
from NCryptoClient.net.client_receiver import Receiver
from NCryptoClient.net.client_sender import Sender


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

    def __init__(self, ipv4_address, port_number,
                 socket_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 wait_time=0.05):
        """
        Constructor.
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
        @return: None.
        """
        self._socket.close()

    def run(self):
        """
        Runs thread routine.
        @return: None.
        """
        self._main_window = client_holder.get_instance('MainWindow')

        self._sender.start()
        self._receiver.start()

        while True:
            msg_bytes = self._receiver.pop_msg_from_queue()
            if msg_bytes is not None:
                self._handle_message(to_dict(msg_bytes))
            time.sleep(self._wait_time)

    def write_output_bytes(self, msg_bytes):
        """
        Writes bytes to the output buffer of the Sender thread.
        @param msg_bytes: serialized JSON-object. (bytes).
        @return: None.
        """
        self._sender.add_msg_to_queue(msg_bytes)

    def _handle_message(self, msg_dict):
        """
        Handles input messages and performs actions depending on the
        message type.
        @param msg_dict: JSON-object. (message).
        @return: None.
        """
        jim_msg_type = type_of(msg_dict)
        if jim_msg_type == JIMMsgType.UNDEFINED_TYPE or is_valid_msg(jim_msg_type, msg_dict) is False:
            return

        if jim_msg_type == JIMMsgType.CTS_PERSONAL_MSG:
            self._handle_personal_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.CTS_CHAT_MSG:
            self._handle_chat_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.CTS_JOIN_CHAT:
            self._handle_join_chat_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.CTS_LEAVE_CHAT:
            self._handle_leave_chat_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.STC_QUANTITY:
            self._handle_quantity_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.STC_CONTACTS_LIST:
            self._handle_contacts_list_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.STC_ALERT:
            self._handle_alert_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.STC_ERROR:
            self._handle_error_msg(msg_dict)

    # ========================================================================
    # A group of protected methods, each of which is charge of message handling
    # of a specific type.
    # ========================================================================
    def _handle_personal_msg(self, msg_dict):
        """
        Handles personal message from a client.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        time_str = '[{}] @{}>'.format(get_formatted_date(msg_dict['time']),
                                      msg_dict['from'])
        self.add_message_signal.emit(msg_dict['from'], time_str, msg_dict['message'])

    def _handle_chat_msg(self, msg_dict):
        """
        Handles message to the chat from a client.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        time_str = '[{}] @{}>'.format(get_formatted_date(msg_dict['time']),
                                      msg_dict['from'])
        self.add_message_signal.emit(msg_dict['to'], time_str, msg_dict['message'])

    def _handle_join_chat_msg(self, msg_dict):
        """
        Handles message from the server that another client has joined a chatroom.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        time_str = '[{}] @Server>'.format(get_formatted_date(msg_dict['time']))
        msg_string = '{} joined {} chatroom.'.format(msg_dict['login'],
                                                     msg_dict['room'])
        self.add_message_signal.emit(msg_dict['room'], time_str, msg_string)

    def _handle_leave_chat_msg(self, msg_dict):
        """
        Handles message from the server that another client has left a chatroom.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        time_str = '[{}] @Server>'.format(get_formatted_date(msg_dict['time']))
        msg_string = '{} left {} chatroom.'.format(msg_dict['login'],
                                                   msg_dict['room'])
        self.add_message_signal.emit(msg_dict['room'], time_str, msg_string)

    def _handle_quantity_msg(self, msg_dict):
        """
        Handles message with amount of contacts of the current client.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        time_str = '[{}] @Server>'.format(get_current_time())
        alert_msg = 'Amount of contacts: {}'.format(msg_dict['quantity'])
        self.add_log_signal.emit(time_str, alert_msg)

    def _handle_contacts_list_msg(self, msg_dict):
        """
        Handles message with the next login of client's contact.
        @param msg_dict: JSON-object. (message).
        @return: -
        """
        self.add_contact_signal.emit(msg_dict['login'])

    def _handle_alert_msg(self, msg_dict):
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
                if msg_dict['response'] == HTTPCode.OK:
                    self._main_window.set_auth_state(True)
                    self.open_chat_signal.emit()

    def _handle_error_msg(self, msg_dict):
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
                if msg_dict['response'] == HTTPCode.UNAUTHORIZED:
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
