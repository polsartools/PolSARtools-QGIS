# -*- coding: utf-8 -*-
"""
/***************************************************************************
                                PolSAR Tools
                                A QGIS plugin
                             -------------------
        begin                : 2020-02-03
        git sha              : $Format:%H$
        copyright            : (C) 2025 by PolSAR tools team
        email                : bnarayanarao@nitw.ac.in
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'mainWindow.ui'))


class PST_Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(PST_Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


from . import nisar_ui_handler
# Add a second UI load for the nisar file
NISAR_FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'NISAR.ui'))

class Nisar_Dialog(QtWidgets.QDialog, NISAR_FORM_CLASS):
    def __init__(self, parent=None):
        super(Nisar_Dialog, self).__init__(parent)
        self.setupUi(self)

        # Mapping buttons to handler functions
        self.nisar_browse.clicked.connect(lambda: nisar_ui_handler.nisar_browse_fn(self))
        self.nisar_help.clicked.connect(lambda: nisar_ui_handler.nisar_help_fn(self))
        self.nisar_close.clicked.connect(lambda: nisar_ui_handler.nisar_close_fn(self))
        self.nisar_import.clicked.connect(lambda: nisar_ui_handler.nisar_import_process(self))