try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QMessageBox

    PYQT_VERSION = 6
    DialogExec = lambda dlg: dlg.exec()
    MessageIcon = QMessageBox.Icon
    MessageButton = QMessageBox.StandardButton

except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QMessageBox

    PYQT_VERSION = 5
    DialogExec = lambda dlg: dlg.exec_()
    MessageIcon = QMessageBox
    MessageButton = QMessageBox

