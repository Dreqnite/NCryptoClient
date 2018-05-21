# -*- coding: utf-8 -*-
"""
Module which implements Chat area implemented as a QtabWidget.
"""
import datetime
from queue import Queue

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from NCryptoTools.Tools.utilities import get_formatted_date
from NCryptoTools.JIM.jim import JIMManager
from NCryptoTools.JIM.jim_base import JSONObjectType

from NCryptoClient.Utils.constants import BOLD_IMG_PATH, ITALIC_IMG_PATH, UNDERLINED_IMG_PATH

class UiChat(QTabWidget):
    """
    Widget-class which has a set of tabs, each of which is a separate chat.
    """
    def __init__(self, parent=None):
        """
        Constructor. Initializes chat, creating an empty window without tabs.
        @param parent: parent window.
        """
        super().__init__(parent)
        self.parent = parent
        self.setGeometry(328, 64, 664, 816)
        self.setObjectName('chat_tw')
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_chat_tab)
        self.show()

    def add_chat_tab(self, chat_name):
        """
        Adds tab in the chat widget.
        @param chat_name: chat name.
        @return: -
        """
        tabs_amount = self.count()

        # if there is no tabs, chat widget can possibly be in a closed state,
        # so we should open it first
        if self.count() == 0:
            self.show()
            chat_widget = UiChatTab(chat_name, self)
            self.addTab(chat_widget, chat_name)
            self.setCurrentIndex(0)
            chat_widget.show()

        # if chat widget already has some tabs, we check that the tab with
        # needed name is not there
        else:
            index = self.find_tab(chat_name)
            if index is None:
                chat_widget = UiChatTab(chat_name, self)
                self.addTab(chat_widget, chat_name)
                self.setCurrentIndex(tabs_amount)
                chat_widget.show()

            # if tab already exists, we switch the current selection to it
            else:
                self.setCurrentIndex(index)

    def close_chat_tab_by_name(self, tab_name):
        """
        Deletes tab by its name.
        @param tab_name: tab name (chat name).
        @return: -
        """
        index = self.find_tab(tab_name)
        self.close_chat_tab(index)

    def close_chat_tab(self, index):
        """
        Deletes tab by its index.
        @param index: tab index.
        @return: -
        """
        if index is not None:
            self.removeTab(index)

        # if user has closed the last tab - shows the inscription
        if self.count() == 0:
            self.hide()
            self.parent.select_chat_st.show()

    def find_tab(self, tab_name):
        """
        Tries to to find the tab with needed name.
        @param tab_name: tab name (chat name).
        @return: tab index.
        """
        # Handles one-tab case separately, because range() will give us an error
        tabs_amount = self.count()
        if tabs_amount == 1:
            if self.widget(0).tab_name == tab_name:
                return 0
            return None

        for i in range(0, tabs_amount):
            if self.widget(i).tab_name == tab_name:
                return i
        return None

    def add_tab_data(self, tab_index, time, message):
        """
        Adds new message (data) to the needed tab. This function is used
        when needs to load messages from history.
        @param tab_index: tab index.
        @param time: time/sender string.
        @param message: new message.
        @return: -
        """
        self.widget(tab_index).add_data(time, message)

    def add_tab_data_from_buffer(self, tab_index):
        """
        Adds new message (data) to the needed tab from the tab's internal
        buffer. This function is used when the current user sends messages.
        @param tab_index: tab index.
        @return: -
        """
        self.widget(tab_index).add_data_from_buffer()

    def remove_tab_data(self, tab_index, data):
        """
        Deletes row from the needed searching it by data.
        @param tab_index: tab index.
        @param data: data to be searched.
        @return: -
        """
        tab = self.widget(tab_index)
        row = tab.find_row(data)
        tab.remove_data(row)


class UiChatTab(QWidget):
    """
    Since we use a set of widgets placing them on each tab,
    we need a custom widget to group them. This class groups
    tab widgets in oneself.
    """
    def __init__(self, tab_name, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._message_queue = Queue(30)
        self.tab_name = tab_name

        # Chat window (messages display)
        self._chat_lb = QListWidget(self)
        self._chat_lb.setGeometry(QRect(8, 8, 640, 640))
        self._chat_lb.setResizeMode(QListView.Adjust)
        self._chat_lb.setObjectName(tab_name + '_contacts_lb')

        # Message input box
        self._msg_te = QTextEdit(self)
        self._msg_te.setGeometry(QRect(8, 656, 544, 120))
        # self._msg_te.setMaxLength(128)
        # self._msg_te.setAlignment(Qt.AlignLeft)
        self._msg_te.setObjectName(tab_name + '_msg_te')

        self._font = QFont()
        self._msg_te.setFont(self._font)

        self._buttons = []
        self._add_bitmap_button(BOLD_IMG_PATH,
                                QRect(560, 656, 24, 24), 'bold_pb', self.set_bold)
        self._add_bitmap_button(ITALIC_IMG_PATH,
                                QRect(592, 656, 24, 24), 'italic_pb', self.set_italic)
        self._add_bitmap_button(UNDERLINED_IMG_PATH,
                                QRect(624, 656, 24, 24), 'underlined_pb', self.set_underlined)
        self._add_bitmap_button(UNDERLINED_IMG_PATH,
                                QRect(560, 688, 24, 24), 'smile_emoji_pb', self.set_underlined)
        self._add_bitmap_button(UNDERLINED_IMG_PATH,
                                QRect(592, 688, 24, 24), 'sad_emoji_pb', self.set_underlined)
        self._add_bitmap_button(UNDERLINED_IMG_PATH,
                                QRect(624, 688, 24, 24), '3_emoji_pb', self.set_underlined)
        self._add_bitmap_button(UNDERLINED_IMG_PATH,
                                QRect(560, 720, 24, 24), '4_emoji_pb', self.set_underlined)
        self._add_bitmap_button(UNDERLINED_IMG_PATH,
                                QRect(592, 720, 24, 24), '5_emoji_pb', self.set_underlined)
        self._add_bitmap_button(UNDERLINED_IMG_PATH,
                                QRect(624, 720, 24, 24), '6_emoji_pb', self.set_underlined)

        # "Send" button
        self._send_pb = QPushButton(self)
        self._send_pb.setText('Send')
        self._send_pb.setGeometry(QRect(560, 752, 88, 24))
        self._send_pb.setObjectName(tab_name + '_send_pb')

        self._send_pb.clicked.connect(self._send_msg)

    def _add_bitmap_button(self, bitmap, geometry, object_name, action):
        button = QPushButton(self)
        button.setGeometry(geometry)
        button.setObjectName(object_name)
        button.setIcon(QIcon(bitmap))
        button.clicked.connect(action)
        self._buttons.append(button)

        # button.setIcon()

    def _send_msg(self):
        """
        Sends message to the server when "Send" button is being pressed.
        @return: -
        """
        msg_text = self._msg_te.toPlainText()

        if self._font.bold():
            msg_text = '<b>{}<b>'.format(msg_text)
        if self._font.italic():
            msg_text = '<i>{}<i>'.format(msg_text)
        if self._font.underline():
            msg_text = '<u>{}<u>'.format(msg_text)

        recipient = self.tab_name
        login = self.parent.parent.get_login()
        unix_time = datetime.datetime.now().timestamp()

        # Message to the chatroom
        if recipient.startswith('#'):
            msg = JIMManager.create_jim_object(JSONObjectType.TO_SERVER_CHAT_MSG,
                                               unix_time, recipient, login, msg_text)

        # Personal message
        else:
            msg = JIMManager.create_jim_object(JSONObjectType.TO_SERVER_PERSONAL_MSG,
                                               unix_time, recipient, login, 'utf-8', msg_text)

        self.parent.parent.msg_handler.write_to_output_buffer(msg.to_dict())

        time = '[{}] @{}> '.format(get_formatted_date(unix_time), login)

        # Adds time and message in the internal buffer (in the queue)
        self._message_queue.put((time, msg_text))

    def set_bold(self):
        self._font.setBold(not self._font.bold())
        self._msg_te.setFont(self._font)

    def set_italic(self):
        self._font.setItalic(not self._font.italic())
        self._msg_te.setFont(self._font)

    def set_underlined(self):
        self._font.setUnderline(not self._font.underline())
        self._msg_te.setFont(self._font)

    def parse_rich_text(self, rich_text):
        font = QFont()
        if rich_text.startswith('<u>'):
            font.setUnderline(True)
            rich_text = rich_text[3:-3]
        if rich_text.startswith('<i>'):
            font.setItalic(True)
            rich_text = rich_text[3:-3]
        if rich_text.startswith('<b>'):
            font.setBold(True)
            rich_text = rich_text[3:-3]
        return rich_text, font

    def add_data_from_buffer(self):
        """
        Adds new data from the internal buffer. This function is being called
        only after receiving server answer that out message has been successfully
        received by user.
        @return: -
        """
        # Clears message input text
        self._msg_te.clear()

        # Takes the first message from the queue
        (time, message) = self._message_queue.get()

        self.add_data(time, message)

    def add_data(self, time, message):
        """
        Adds new data from the external buffer.
        @param time: time and sender.
        @param message: new data (message).
        @return: -
        """
        (plain_text, font) = self.parse_rich_text(message)

        # QLabel for the time/sender
        time_st = QLabel(time)
        time_st.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        time_st.adjustSize()

        # QLabel for the message
        message_st = QLabel(plain_text)
        message_st.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        message_st.setFont(font)
        message_st.adjustSize()

        # Layout: time + message
        container = QFormLayout()
        container.setContentsMargins(0, 0, 0, 0)
        container.addRow(time_st, message_st)

        complete_line = QWidget()
        complete_line.setLayout(container)

        item = QListWidgetItem()
        item.setSizeHint(QSize(item.sizeHint().width(), 20))

        self._chat_lb.addItem(item)
        self._chat_lb.setItemWidget(item, complete_line)
