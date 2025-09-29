# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 A QGIS plugin
This plugin generates derived SAR parameters from input polarimetric matrix (C3, T3, C2, T2).
                              -------------------
        begin                : 2020-02-03
        git sha              : $Format:%H$
        copyright            : (C) 2020 by PolSAR tools team
        email                : bnarayanarao@iitb.ac.in
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
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import QProcess

from qgis.PyQt import *
from qgis.core import *
import requests
import numpy as np
import multiprocessing
import webbrowser


from .resources import *
# Import the code for the dialog
from .SAR_Tools_dialog import PST_Dialog
import os.path
import sys
import polsartools as pst
import re
from osgeo import gdal
import time

from .qt_compat import (
    QtCore, QtGui, QtWidgets, Qt,
    DialogExec, MessageIcon, MessageButton,
    AlignmentFlag, Key, PYQT_VERSION
)



# Create a lock for multiprocess
p_lock = multiprocessing.Lock()

############################################################################################################################################
############################################################################################################################################

class PolSAR(object):
    """QGIS Plugin Implementation."""
    sig_abort_workers = pyqtSignal()
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface


        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PolSAR_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.dlg = PST_Dialog()

        # Declare instance attributes
        self.actions = []
        icon_path = ':/plugins/SAR_Tools/icon.png'
        self.menu = self.tr(u'&PolSAR tools')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        ##################################################################
        # USER VARIABLES
        
        self.inFolder=''
        # self.ws = 5
        
        self.toolbar = self.iface.addToolBar(u'PolSAR Tools')
        self.toolbar.setObjectName(u'PolSAR Tools')
        
        
        # self.dlg.fp_browse.setEnabled(True)
        # self.dlg.inFolder_fp.setEnabled(False)
        self.dlg.inFolder_fp.setEnabled(False)
        self.dlg.fp_browse.setEnabled(False)
        # self.dlg.fp_cb_C3.setEnabled(False)
        # self.dlg.fp_cb_T3.setEnabled(False)
       
        self.dlg.inFolder_cp.setEnabled(False)
        self.dlg.cp_browse.setEnabled(False)
        # self.dlg.cp_cb_C2.setEnabled(False)
        # self.dlg.cp_cb_T2.setEnabled(False)
        
        self.dlg.inFolder_dp.setEnabled(False)
        self.dlg.dp_browse.setEnabled(False)
        # self.dlg.dp_cb_C2.setEnabled(False)
        # self.dlg.dp_cb_T2.setEnabled(False)
                     
        
        self.dlg.fp_ws.setEnabled(True)
        self.dlg.cp_ws.setEnabled(True)
        self.dlg.dp_ws.setEnabled(True)
        self.dlg.fp_parm.setEnabled(True)
        self.dlg.cp_parm.setEnabled(True)
        self.dlg.dp_parm.setEnabled(True)
        # self.dlg.lineEdit.clear()
        
        self.dlg.pb_process.setEnabled(False)
        # self.dlg.cp_cb_tau.setCurrentText('Tau')
        # Set active tab background colour  
        self.dlg.tabWidget.setStyleSheet(
                """
            QTabBar::tab:selected {
                background: rgb(0, 175, 255)
            }
            """
            )
        
        
        
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PolSAR', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)
        self.Startup()
        

        """ Global variables"""
        global  logger
        logger = self.dlg.terminal
        global pol_mode
        pol_mode = self.dlg.tabWidget.currentIndex()




        # self.dlg.cb_mat_type.currentIndexChanged.connect(self.Cob_mode)

        # logger.append(str(self.dlg.tabWidget.currentIndex()))
        # self.dlg.fp_parm.currentIndexChanged.connect(self.Cob_mode)
        """CP"""
        # self.dlg.fp_cb_C3.setChecked(False)
        # self.dlg.fp_cb_T3.setChecked(True)
        # self.dlg.fp_cb_T3.stateChanged.connect(self.fpt3_state_changed)
        # self.dlg.fp_cb_C3.stateChanged.connect(self.fpc3_state_changed)

        self.dlg.fp_browse.clicked.connect(self.openRaster)

        self.dlg.fp_parm.currentIndexChanged.connect(self.Cob_parm)   
        self.ws = int(self.dlg.fp_ws.value())

        self.dlg.fp_ws.valueChanged.connect(self.ws_update)
        
        """CP"""
        # self.dlg.cp_cb_C2.setChecked(False)
        # self.dlg.cp_cb_T2.setChecked(True)
        # self.dlg.cp_cb_T2.stateChanged.connect(self.cpt2_state_changed)
        # self.dlg.cp_cb_C2.stateChanged.connect(self.cpc2_state_changed)
        self.dlg.cp_browse.clicked.connect(self.openRaster)
        self.dlg.cp_ws.valueChanged.connect(self.ws_update)
        self.dlg.cp_parm.currentIndexChanged.connect(self.Cob_parm)
        
        self.psi_val=0
        self.chi_val=45
        self.dlg.cp_sb_psi.valueChanged.connect(self.psi_update)
        self.dlg.cp_sb_chi.valueChanged.connect(self.chi_update)
        
        """DP"""
        # self.dlg.dp_cb_C2.setChecked(False)
        # self.dlg.dp_cb_T2.setChecked(True)
        # self.dlg.dp_cb_T2.stateChanged.connect(self.dpt2_state_changed)
        # self.dlg.dp_cb_C2.stateChanged.connect(self.dpc2_state_changed)
        self.dlg.dp_browse.clicked.connect(self.openRaster)
        self.dlg.dp_ws.valueChanged.connect(self.ws_update)
        self.dlg.dp_parm.currentIndexChanged.connect(self.Cob_parm) 


        """ TAB; CLEAR; PROCESS; VIEW """
        self.dlg.tabWidget.currentChanged.connect(self.ontabChange)               
        self.dlg.pb_view.clicked.connect(self.viewData)
        self.dlg.clear_terminal.clicked.connect(self.clear_log)
        self.dlg.pb_process.clicked.connect(self.startProcess)
        self.dlg.help_btn.clicked.connect(lambda: webbrowser.open('https://sar-tools.readthedocs.io/en/latest/'))
        self.dlg.close_btn.clicked.connect(self.closeui_fn)
        # self.dlg.close_btn.clicked.connect(self.cancel_fn)
        # self.dlg.pb_cancel.clicked.connect(self.cancel_fn)
        # self.dlg.pb_cancel.clicked.connect(lambda: self.worker.stop())
        return action
    
    #@pyqtSlot()  
    # Print the tab/polarimetric mode update to the logger 
    def ontabChange(self,i): #changed!
        if i==0:
            # logger.append("(polsartools) $ Full-pol")
            pol_mode = i            
            # logger.append(str(pol_mode))
        if i==1:
            # logger.append("(polsartools) $ Compact-pol")
            pol_mode = i
            # logger.append(str(pol_mode))
        if i==2:
            # logger.append("(polsartools) $ Dual-pol")
            pol_mode = i
            # logger.append(str(pol_mode))
            
   

    def closeui_fn(self):

        self.dlg.close()
            
        
    def psi_update(self):
        self.psi_val = float(self.dlg.cp_sb_psi.value())

    def chi_update(self):
        self.chi_val = float(self.dlg.cp_sb_chi.value())
            
    def ws_update(self):
        
        if self.dlg.tabWidget.currentIndex()==0:
            self.ws = int(self.dlg.fp_ws.value())
        if self.dlg.tabWidget.currentIndex()==1:
            self.ws = int(self.dlg.cp_ws.value())
        if self.dlg.tabWidget.currentIndex()==2:
            self.ws = int(self.dlg.dp_ws.value())
        if self.ws%2==0:
            self.ws+=1
        # logger = self.dlg.terminal
        # logger.append('(polsartools) $ Window size: '+str(self.ws))
        
 
    def dtype_error(self):
        logger.append('(polsartools) $ Error!! Invalid data folder.')
                 
    def startProcess(self):
        
        
        if self.dlg.tabWidget.currentIndex() == 0:
            # self.inFolder = str(QFileDialog.getExistingDirectory(self.dlg, 
                                                            # "Select T3/C3/T2/C2 Folder"))

            # if(self.fp_cb_C3.isChecked()):
            indX =self.dlg.fp_parm.currentIndex()          
            
            if indX==1:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startGRVI()
                except:
                    self.dtype_error()
                    
            if indX==2:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startNM3CF()
                except:
                    self.dtype_error()
                    
            if indX==3:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startPRVI()
                except:
                    self.dtype_error()
                    
            if indX==4:
                # try:
                    logger.append('(polsartools) $ --------------------')
                    self.startDOPfp()
                # except:
                #     self.dtype_error()
            if indX==5:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startRVIFP()
                except:
                    self.dtype_error()
            if indX==6:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startMF4CF()
                except:
                    self.dtype_error()
            else:
                pass
            
            
        if self.dlg.tabWidget.currentIndex() == 1:
            # if(self.fp_cb_C3.isChecked()):
            indX =self.dlg.cp_parm.currentIndex()  
            if indX==1:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startNM3CC()
                except:
                    self.dtype_error()
            
            if indX==2:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startDOPCP()
                except:
                    self.dtype_error()
                    
            if indX==3:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startCPRVI()
                except:
                    self.dtype_error()

            if indX==4:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startmiSOmega()
                except:
                    self.dtype_error()

            else:
                pass
        
        if self.dlg.tabWidget.currentIndex() == 2:
            # if(self.fp_cb_C3.isChecked()):
            indX =self.dlg.dp_parm.currentIndex()   
            if indX==1:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startDpRVI()
                except:
                    self.dtype_error()

            if indX==2:
                try:
                    logger.append('(polsartools) $ --------------------')
                    self.startPRVIdp()
                except:
                    self.dtype_error()

            if indX==3:
                try:                    
                    logger.append('(polsartools) $ --------------------')
                    self.startDOPdp()
                except:
                    self.dtype_error()
            if indX==4:
                try:                    
                    logger.append('(polsartools) $ --------------------')
                    self.startRVIdp()
                except:
                    self.dtype_error()


            else:
                pass
            
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SAR_Tools/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Process'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def Cob_parm(self):
        # For terminal and UI update
        
        if self.dlg.tabWidget.currentIndex() == 0:
            parm =self.dlg.fp_parm.currentIndex()
            if parm == 1:
                # logger.append('(polsartools) $      GRVI')
                self.dlg.inFolder_fp.setEnabled(True)
                self.dlg.fp_browse.setEnabled(True)
                # self.dlg.fp_cb_T3.setChecked(True)
                # self.dlg.fp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            elif parm == 2:
                # logger.append('(polsartools) $      MF3CF')
                self.dlg.inFolder_fp.setEnabled(True)
                self.dlg.fp_browse.setEnabled(True)
                # self.dlg.fp_cb_T3.setChecked(True)
                # self.dlg.fp_browse.setEnabled(True)
                # self.dlg.fp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            elif parm == 3:
                # logger.append('(polsartools) $      PRVI')
                self.dlg.inFolder_fp.setEnabled(True)
                self.dlg.fp_browse.setEnabled(True)
                # self.dlg.fp_cb_T3.setChecked(True)
                # self.dlg.fp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            elif parm == 4:
                # logger.append('(polsartools) $      DOP')
                self.dlg.inFolder_fp.setEnabled(True)
                self.dlg.fp_browse.setEnabled(True)
                # self.dlg.fp_cb_T3.setChecked(True)
                # self.dlg.fp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            elif parm == 5:
                # logger.append('(polsartools) $      RVI')
                self.dlg.inFolder_fp.setEnabled(True)
                self.dlg.fp_browse.setEnabled(True)
                # self.dlg.fp_cb_T3.setChecked(True)
                # self.dlg.fp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            elif parm == 6:
                # logger.append('(polsartools) $      MF4CF')
                self.dlg.inFolder_fp.setEnabled(True)
                self.dlg.fp_browse.setEnabled(True)
                # self.dlg.fp_cb_T3.setChecked(True)
                # self.dlg.fp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            

            elif parm==0:
                self.dlg.inFolder_fp.setEnabled(False)
                self.dlg.pb_process.setEnabled(False)
                self.dlg.fp_browse.setEnabled(False)
                # self.dlg.fp_ws.setEnabled(False)

        if self.dlg.tabWidget.currentIndex() == 1:
            parm =self.dlg.cp_parm.currentIndex()
            # tau = self.dlg.cp_cb_tau.currentIndex()
            if parm == 1:
                # logger.append('(polsartools) $     MF3CC')
                self.dlg.inFolder_cp.setEnabled(True)
                self.dlg.cp_browse.setEnabled(True)
                # self.dlg.cp_cb_C2.setChecked(True)
                # self.dlg.cp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            
            if parm == 2:
                # logger.append('(polsartools) $     DOP')
                self.dlg.inFolder_cp.setEnabled(True)
                self.dlg.cp_browse.setEnabled(True)
                # self.dlg.cp_cb_C2.setChecked(True)
                # self.dlg.cp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            
            if parm == 3:
                # logger.append('(polsartools) $    CpRVI')
                self.dlg.inFolder_cp.setEnabled(True)
                self.dlg.cp_browse.setEnabled(True)
                # self.dlg.cp_cb_C2.setChecked(True)
                # self.dlg.cp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            
            if parm == 4:
                # logger.append('(polsartools) $    CpRVI')
                self.dlg.inFolder_cp.setEnabled(True)
                self.dlg.cp_browse.setEnabled(True)
                # self.dlg.cp_cb_C2.setChecked(True)
                # self.dlg.cp_ws.setEnabled(True)
                self.dlg.cp_sb_psi.setEnabled(True)
                self.dlg.cp_sb_chi.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            
            elif parm==0:
                self.dlg.inFolder_cp.setEnabled(False)
                self.dlg.pb_process.setEnabled(False)
                self.dlg.cp_browse.setEnabled(False)
                self.dlg.cp_sb_psi.setEnabled(False)
                self.dlg.cp_sb_chi.setEnabled(False)
                # self.dlg.fp_ws.setEnabled(False)
  
        if self.dlg.tabWidget.currentIndex() == 2:
            parm =self.dlg.dp_parm.currentIndex()
            
            if parm == 1:
                # logger.append('(polsartools) $      DpRVI')
                # self.dlg.dp_cb_C2.setChecked(True)
                self.dlg.inFolder_dp.setEnabled(True)
                self.dlg.dp_browse.setEnabled(True)
                # self.dlg.dp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            if parm == 2:
                # logger.append('(polsartools) $      PRVI')
                # self.dlg.dp_cb_C2.setChecked(True)
                self.dlg.inFolder_dp.setEnabled(True)
                self.dlg.dp_browse.setEnabled(True)
                # self.dlg.dp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            if parm == 3:
                # logger.append('(polsartools) $      DOP')
                # self.dlg.dp_cb_C2.setChecked(True)
                self.dlg.inFolder_dp.setEnabled(True)
                self.dlg.dp_browse.setEnabled(True)
                # self.dlg.dp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            if parm == 4:
                # logger.append('(polsartools) $      RVI')
                # self.dlg.dp_cb_C2.setChecked(True)
                self.dlg.inFolder_dp.setEnabled(True)
                self.dlg.dp_browse.setEnabled(True)
                # self.dlg.dp_ws.setEnabled(True)
                self.dlg.pb_process.setEnabled(True)
            elif parm==0:
                self.dlg.inFolder_dp.setEnabled(False)
                self.dlg.dp_browse.setEnabled(False)
                self.dlg.pb_process.setEnabled(False)
                # self.dlg.dp_ws.setEnabled(False)
           
            
            
            
    def viewData(self):
        # log_text = self.dlg.terminal
        # log_text.append('(polsartools) $ Data loaded in to QGIS\n')
        
        file_filter = "All (*.*);;GeoTiFF (*.tif);;bin (*.bin)"
                                          
        if self.inFolder:
            f_path = self.inFolder
        else:
            f_path = os.path.dirname(__file__)
        names = QFileDialog.getOpenFileNames(self.dlg, 
                                            "Select files to view/import into QGIS",
                                            f_path,
                                            file_filter       
                                                      )
        
        if names is not None:
            for i in np.arange(0,np.size(list(names[0][0:])),1):
                try:

                    self.iface.addRasterLayer(str(names[0][i]))   
                    logger.append(str(names[0][i]))

                except:
                    logger.append("(polsartools) $ invalid file type!!")

        # logger.append(str(np.size(list(names[0][0:]))))
        # logger.append(str(f_path))    
        
        
  
            
    def clear_log(self):
        self.dlg.terminal.clear()
        self.Startup()
        # self.dlg.cb_mat_type.setCurrentIndex(0)
        self.dlg.inFolder_fp.clear()
        self.dlg.inFolder_cp.clear()
        self.dlg.inFolder_dp.clear()
        # self.dlg.inFolder_fp.setEnabled(False)
        # self.dlg.fp_browse.setEnabled(False)
        self.dlg.progressBar.setValue(0)
        self.dlg.fp_ws.setValue(5)
        self.dlg.cp_sb_psi.setValue(0)
        self.dlg.cp_sb_chi.setValue(45)
        # self.dlg.fp_ws.setEnabled(False)
        self.dlg.fp_parm.setCurrentIndex(0)
        self.dlg.cp_ws.setValue(5)
        # self.dlg.cp_ws.setEnabled(False)
        self.dlg.cp_parm.setCurrentIndex(0)
        self.dlg.dp_ws.setValue(5)
        # self.dlg.dp_ws.setEnabled(False)
        self.dlg.dp_parm.setCurrentIndex(0)
        
        self.dlg.pb_process.setEnabled(False)

        
    def showmsg(self, signal):
        log = self.dlg.terminal
        log.append(str(signal))  
        
    def showTip(self):
        msgBox = QMessageBox()
        msgBox.setIcon(MessageIcon.Information)
        msgBox.setText(
            "Please select a valid matrix folder\n"
            "generated from PolSARpro\n"
            "file format: *.bin, *.hdr"
        )
        msgBox.setWindowTitle("Tip!")
        msgBox.setStandardButtons(MessageButton.Ok)

        returnValue = msgBox.exec()

        # if returnValue == MessageButton.Ok:
        #     print('OK clicked')    #       # print('OK clicked')

    def showError3(self):
       msgBox = QMessageBox()
       msgBox.setIcon(QMessageBox.Information)
       msgBox.setText("Please select a valid C3/T3 matrix folder \
                      \n generated from PolSARpro \
                      \n file format: *.bin, *.hdr")
       msgBox.setWindowTitle("Error!")
       msgBox.setStandardButtons(QMessageBox.Ok)
       # msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
       # msgBox.buttonClicked.connect(msgButtonClick)
    
       returnValue = msgBox.exec()
       # if returnValue == QMessageBox.Ok:
          # print('OK clicked')

    def showError2(self):
       msgBox = QMessageBox()
       msgBox.setIcon(QMessageBox.Information)
       msgBox.setText("Please select a valid C2 matrix folder \
                      \n generated from PolSARpro \
                      \n file format: *.bin, *.hdr")
       msgBox.setWindowTitle("Error!")
       msgBox.setStandardButtons(QMessageBox.Ok)
       # msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
       # msgBox.buttonClicked.connect(msgButtonClick)
    
       returnValue = msgBox.exec()
       # if returnValue == QMessageBox.Ok:
          # print('OK clicked')


    def openRaster(self):
        """Open raster from file dialog"""
        # logger.append(str(self.dlg.tabWidget.currentIndex()))
        self.showTip() # pop-up tip
        
        if self.dlg.tabWidget.currentIndex() == 0:
            self.inFolder = str(QFileDialog.getExistingDirectory(
                            self.dlg, "Select T3/C3 Folder"))                   
            self.dlg.inFolder_fp.setText(self.inFolder)
            
                
        if self.dlg.tabWidget.currentIndex() == 1:
            self.inFolder = str(QFileDialog.getExistingDirectory(
                            self.dlg, "Select C2 Folder"))
            self.dlg.inFolder_cp.setText(self.inFolder)
            
            if self.inFolder:
                try:
                    # logger.append('(polsartools) $ C2 selected')
                    self.C2_stack = self.load_C2(self.inFolder)
                    logger.append('(polsartools) $ Ready to process.')
                    self.dlg.cp_ws.setEnabled(True)
                    self.dlg.cp_parm.setEnabled(True)
                except:
                    logger.append('(polsartools) $ Error! \n(polsartools) $ Please select a valid C2 folder')
                    self.showError2()
            
            # if self.inFolder:


                
        if self.dlg.tabWidget.currentIndex() == 2:
            self.inFolder = str(QFileDialog.getExistingDirectory(
                            self.dlg, "Select C2 Folder"))                   
            self.dlg.inFolder_dp.setText(self.inFolder)
            
            if self.inFolder:
                try:
                    logger.append('(polsartools) $ C2 selected')
                    self.C2_stack = self.load_C2(self.inFolder)
                    logger.append('(polsartools) $ Ready to process.')
                    self.dlg.dp_ws.setEnabled(True)
                    self.dlg.dp_parm.setEnabled(True)
                except:
                    logger.append('(polsartools) $ Error! \n(polsartools) $ Please select a valid C2 folder')
                    self.showError2()


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&PolSAR tools'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = PST_Dialog()
        
        self.dlg.show()
        result = DialogExec(self.dlg)
        
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            pass
        
    def Startup(self):
        # For terminal outputs
        logger = self.dlg.terminal
        logger.append("\n\t                  Welcome to PolSAR tools!")
        logger.append("\t================================\n")
        logger.append("\t This plugin generates Polarimetric SAR parameters.")
        logger.append("\t   🔹 SAR Indices       🔹 Decomposition Parameters\n")
        logger.append("\t-----------------------------------------------------------------\n")
        logger.append('Tip: Start by selecting a parameter from the "Select Parameter" dropdown menu.\n')

    def handle_stdout(self):
        output = self.process.readAllStandardOutput().data().decode()
        lines = output.splitlines()
        for line in lines:
            self.dlg.terminal.append(line.strip())                
            match = re.search(r'progress: (\d+)', line)    
            if match:
                percent = int(match.group(1))
                self.pBarupdate(percent)
                
    def handle_stderr(self):
        error_output = self.process.readAllStandardError().data().decode().strip()
        print("QProcess Error:", error_output)
        # Optionally log to terminal or show warning
    def handle_finished(self, exitCode, exitStatus):
        self.dlg.terminal.append('\n(polsartools) $ Ready to process.')
        path = os.path.realpath(self.inFolder)
        os.startfile(path)
        print(f"Process finished with exit code: {exitCode}, status: {exitStatus}")
    def cancel_fn(self):
        # self.sig_abort_workers.emit()
        self.dlg.terminal.append('(polsartools) $ cancelling...')
        for thread, worker in self.__threads:  # note nice unpacking by Python, avoids indexing
            thread.quit()  # this will quit **as soon as thread event loop unblocks**
            thread.wait()  # <- so you need to wait for it to *actually* quit
            # worker.kill()


    def pBarupdate(self, signal):
        pB = self.dlg.progressBar
        pB.setValue(int(signal))
        # log.append(str(signal))  

    def workerFinished(self,finish_cond):

        # if finish_cond:
        logger = self.dlg.terminal
        logger.append('(polsartools) $ Process completed with ' +str(self.ws)+' x ' +str(self.ws)+' window ')
        # clean up the worker and thread
    
        # self.viewData() # Load data into QGIS
        #Open output folder after finishing the process
        path = os.path.realpath(self.inFolder)
        os.startfile(path)

        #set progress bar to Zero
        pB = self.dlg.progressBar
        pB.setValue(100)

        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()

        if finish_cond == 0:
            # self.worke
            logger.append('(polsartools) $ Process stopped in between ! You are good to go again.')
            pB.setValue(0)

    def workerError(self, e, exception_string):
        logger = self.dlg.terminal
        logger.append('(polsartools) $ :-( Error:\n\n %s' %str(exception_string))
    
###################### Dual-pol ############################
    def startPRVIdp(self):
        self.dlg.terminal.append('(polsartools) $ Calculating PRVIdp pst...')
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/dp/run_prvidp.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()

    def startDOPdp(self):
        self.dlg.terminal.append('(polsartools) $ Calculating DOP pst...')
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/dp/run_dop_dp.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()
    def startDpRVI(self):
        self.dlg.terminal.append('(polsartools) $ Calculating DpRVI pst...')
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/dp/run_dprvi.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()

    def startRVIdp(self):
        self.dlg.terminal.append('(polsartools) $ Calculating RVI DP pst...')
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/dp/run_rvidp.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()

###################### Compact-pol ############################

    def startmiSOmega(self):
        self.dlg.terminal.append('(polsartools) $ Calculating startmiSOmega pst...')
        tau = self.dlg.cp_cb_tau.currentIndex()
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/cp/run_misomega.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws), str(tau)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()


    def startCPRVI(self):
        self.dlg.terminal.append('(polsartools) $ Calculating startCPRVI pst...')
        tau = self.dlg.cp_cb_tau.currentIndex()
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/cp/run_cprvi.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws), str(tau)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()


    def startDOPCP(self):
        self.dlg.terminal.append('(polsartools) $ Calculating DOPCP pst...')
        tau = self.dlg.cp_cb_tau.currentIndex()
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/cp/run_dop_cp.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws), str(tau)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()



    def startNM3CC(self):
        self.dlg.terminal.append('(polsartools) $ Calculating startNM3CC pst...')
        tau = self.dlg.cp_cb_tau.currentIndex()
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/cp/run_nm3cc.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws), str(tau)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()

###################### Full-pol ############################

    def startDOPfp(self):  
        self.dlg.terminal.append('(polsartools) $ Calculating DOP FP pst...')
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/fp/run_dopfp.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()
        

    def startPRVI(self):  
        self.dlg.terminal.append('(polsartools) $ Calculating PRVI FP pst...')
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/fp/run_prvifp.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()

    def startMF4CF(self):
        
        self.dlg.terminal.append('(polsartools) $ Calculating NM4CF FP pst...')
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/fp/run_mf4cf.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()

    def startNM3CF(self):
        
        self.dlg.terminal.append('(polsartools) $ Calculating NM3CF FP pst...')
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/fp/run_nm3cf.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()

    def startRVIFP(self):
        self.dlg.terminal.append('(polsartools) $ Calculating RVI FP pst...')
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/fp/run_rvifp.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()

        
    def startGRVI(self):
        self.dlg.terminal.append('(polsartools) $ Calculating GRVI FP pst...')
        self.process = QProcess()
        self.process.setProgram("python")  
        
        script_path = os.path.join(os.path.dirname(__file__), "functions/fp/run_grvi.py")
        self.process.setArguments([script_path, self.inFolder, str(self.ws)])
        # self.dlg.terminal.append(script_path)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()

class UserAbortedNotification(Exception):
    pass 
        
        
        
        
        
        
        
        
