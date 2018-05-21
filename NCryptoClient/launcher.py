# -*- coding: utf-8 -*-
"""
Entry point of the client application.
"""
import sys

from PyQt5.QtWidgets import QApplication

from NCryptoClient.main_window import MainWindow
from NCryptoClient.client_instance_holder import client_holder


def main():
    """
    Initializes main window.
    @return: application return code.
    """
    app = QApplication(sys.argv)

    main_window = MainWindow()
    client_holder.add_instance('MainWindow', main_window)

    # Opens authentication window
    main_window.open_authentication_window()
    main_window.show()

    if main_window.get_auth_state() is True:
        pass
        # Loads list of contacts
        # main_window.request_contacts_list()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
