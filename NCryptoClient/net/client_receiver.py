# -*- coding: utf-8 -*-
"""
Module which defines Receiver-thread class.
"""
import time
from threading import Thread
from queue import Queue

from NCryptoTools.tools.utilities import get_current_time

from NCryptoClient.client_instance_holder import client_holder


class Receiver(Thread):
    """
    Thread-class for controlling the flow of incoming messages, storing them
    into the buffer for incoming messages.
    """
    def __init__(self, shared_socket, wait_time=0.1, buffer_size=30):
        """
        Constructor. _input_buffer_queue is implemented as a queue.
        @param shared_socket: client socket.
        @param wait_time: wait time in seconds to avoid overheating.
        @param buffer_size: buffer size in number of elements.
        """
        super().__init__()
        self.daemon = True
        self._socket = shared_socket
        self._wait_time = wait_time
        self._input_buffer_queue = Queue(buffer_size)
        self._main_window = client_holder.get_instance('MainWindow')

    def pop_msg_from_queue(self):
        """
        Takes first element from the queue.
        @return: JSON-object. (message).
        """
        return self._input_buffer_queue.get() if self._input_buffer_queue.qsize() > 0 else None

    def run(self):
        """
        Runs thread routine.
        @return: -
        """
        while True:
            try:
                msg_bytes = self._socket.recv(1024)
            except OSError as e:
                self._main_window.add_data_in_tab('Log', '[{}] @NCryptoChat> {}'.format(get_current_time(), str(e)))
                return
            else:
                self._input_buffer_queue.put(msg_bytes)
            time.sleep(self._wait_time)
