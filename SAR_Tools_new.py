# -*- coding: utf-8 -*-
"""
A QGIS plugin to generate derived SAR parameters from input polarimetric matrix (C3, T3, C2, T2).
Refactored to remove redundancy in process launching, parameter handling, and error handling.
"""

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import QProcess

from qgis.PyQt import *
from qgis.core import *
import numpy as np
import multiprocessing
import webbrowser
import os
import re
from osgeo import gdal
import time

from .resources import *
from .SAR_Tools_dialog import PST_Dialog
from .qt_compat import (
    QtCore, QtGui, QtWidgets, Qt,
    DialogExec, MessageIcon, MessageButton,
    AlignmentFlag, Key, PYQT_VERSION
)

# Create a lock for multiprocess
p_lock = multiprocessing.Lock()

#################################################################################################
# Process Mapping
#################################################################################################
PROCESS_MAP = {
    "fp": {
        1: ("GRVI FP pst", "functions/fp/run_grvi.py"),
        2: ("NM3CF FP pst", "functions/fp/run_nm3cf.py"),
        3: ("PRVI FP pst", "functions/fp/run_prvifp.py"),
        4: ("DOP FP pst", "functions/fp/run_dopfp.py"),
        5: ("RVI FP pst", "functions/fp/run_rvifp.py"),
        6: ("MF4CF FP pst", "functions/fp/run_mf4cf.py"),
    },
    "cp": {
        1: ("NM3CC CP pst", "functions/cp/run_nm3cc.py", True),
        2: ("DOP CP pst", "functions/cp/run_dop_cp.py", True),
        3: ("CPRVI pst", "functions/cp/run_cprvi.py", True),
        4: ("miSOmega pst", "functions/cp/run_misomega.py", True),
    },
    "dp": {
        1: ("DpRVI pst", "functions/dp/run_dprvi.py"),
        2: ("PRVI dp pst", "functions/dp/run_prvidp.py"),
        3: ("DOP dp pst", "functions/dp/run_dop_dp.py"),
        4: ("RVI dp pst", "functions/dp/run_rvidp.py"),
    }
}

#################################################################################################
# Parameter-to-UI mapping (for Cob_parm)
#################################################################################################
COB_UI_MAP = {
    "fp": {
        1: ["inFolder_fp", "fp_browse"],
        2: ["inFolder_fp", "fp_browse"],
        3: ["inFolder_fp", "fp_browse"],
        4: ["inFolder_fp", "fp_browse"],
        5: ["inFolder_fp", "fp_browse"],
        6: ["inFolder_fp", "fp_browse"],
    },
    "cp": {
        1: ["inFolder_cp", "cp_browse"],
        2: ["inFolder_cp", "cp_browse"],
        3: ["inFolder_cp", "cp_browse"],
        4: ["inFolder_cp", "cp_browse", "cp_sb_psi", "cp_sb_chi"],
    },
    "dp": {
        1: ["inFolder_dp", "dp_browse"],
        2: ["inFolder_dp", "dp_browse"],
        3: ["inFolder_dp", "dp_browse"],
        4: ["inFolder_dp", "dp_browse"],
    }
}

#################################################################################################
# Main Plugin Class
#################################################################################################
class PolSAR(object):
    """QGIS Plugin Implementation."""
    sig_abort_workers = pyqtSignal()

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # Initialize dialog
        self.dlg = PST_Dialog()
        self.actions = []
        self.menu = self.tr(u'&PolSAR tools')
        self.first_start = None

        self.inFolder = ''
        self.ws = 5
        self.psi_val = 0
        self.chi_val = 45

        self.toolbar = self.iface.addToolBar(u'PolSAR Tools')
        self.toolbar.setObjectName(u'PolSAR Tools')

        # Setup UI defaults
        self.dlg.inFolder_fp.setEnabled(False)
        self.dlg.fp_browse.setEnabled(False)
        self.dlg.inFolder_cp.setEnabled(False)
        self.dlg.cp_browse.setEnabled(False)
        self.dlg.inFolder_dp.setEnabled(False)
        self.dlg.dp_browse.setEnabled(False)
        self.dlg.pb_process.setEnabled(False)


        # --- File browse buttons ---
        self.dlg.fp_browse.clicked.connect(self.openRaster)
        self.dlg.cp_browse.clicked.connect(self.openRaster)
        self.dlg.dp_browse.clicked.connect(self.openRaster)

        # --- Parameter dropdowns already connected ---
        self.dlg.fp_parm.currentIndexChanged.connect(self.Cob_parm)
        self.dlg.cp_parm.currentIndexChanged.connect(self.Cob_parm)
        self.dlg.dp_parm.currentIndexChanged.connect(self.Cob_parm)

        # --- Spinboxes for psi/chi ---
        self.dlg.cp_sb_psi.valueChanged.connect(self.psi_update)
        self.dlg.cp_sb_chi.valueChanged.connect(self.chi_update)

        # --- Spinboxes for window size ---
        self.dlg.fp_ws.valueChanged.connect(self.ws_update)
        self.dlg.cp_ws.valueChanged.connect(self.ws_update)
        self.dlg.dp_ws.valueChanged.connect(self.ws_update)

        # --- Other buttons ---
        self.dlg.pb_view.clicked.connect(self.viewData)
        self.dlg.clear_terminal.clicked.connect(self.clear_log)
        self.dlg.pb_process.clicked.connect(self.startProcess)
        self.dlg.help_btn.clicked.connect(lambda: webbrowser.open('https://sar-tools.readthedocs.io/en/latest/'))
        self.dlg.close_btn.clicked.connect(self.closeui_fn)

        # --- Tab change ---
        self.dlg.tabWidget.currentChanged.connect(self.Cob_parm)


        self.dlg.tabWidget.setStyleSheet("""
            QTabBar::tab:selected {
                background: rgb(0, 175, 255)
            }
        """)

    #################################################################################################
    # Utilities
    #################################################################################################
    def tr(self, message):
        return QCoreApplication.translate('PolSAR', message)

    def log(self, message):
        self.dlg.terminal.append(f"(polsartools) $ {message}")

    def show_error(self, text, title="Error!"):
        msgBox = QMessageBox()
        msgBox.setIcon(MessageIcon.Information)
        msgBox.setText(text)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(MessageButton.Ok)
        msgBox.exec()
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

        if self.dlg.tabWidget.currentIndex() == 2:
            self.inFolder = str(QFileDialog.getExistingDirectory(
                            self.dlg, "Select C2 Folder"))
            self.dlg.inFolder_dp.setText(self.inFolder)

            
    def pBarupdate(self, signal):
        pB = self.dlg.progressBar
        pB.setValue(int(signal))
        # log.append(str(signal)) 
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
    #################################################################################################
    # Process Runner
    #################################################################################################
    def run_process(self, label, script_name, extra_args=None):
        self.log(f"Calculating {label}...")
        self.process = QProcess()
        self.process.setProgram("python")

        script_path = os.path.join(os.path.dirname(__file__), script_name)
        args = [script_path, self.inFolder, str(self.ws)]
        if extra_args:
            args.extend(extra_args)

        self.process.setArguments(args)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start()

    #################################################################################################
    # Core Workflow
    #################################################################################################
    def startProcess(self):
        mode_map = {0: "fp", 1: "cp", 2: "dp"}
        mode = mode_map.get(self.dlg.tabWidget.currentIndex())
        if not mode:
            return

        indX = (self.dlg.fp_parm.currentIndex() if mode == "fp"
                else self.dlg.cp_parm.currentIndex() if mode == "cp"
                else self.dlg.dp_parm.currentIndex())

        process_info = PROCESS_MAP.get(mode, {}).get(indX)
        if not process_info:
            return

        label, script, needs_tau = (process_info + (False,))[:3]
        extra = [str(self.dlg.cp_cb_tau.currentIndex())] if needs_tau else None

        try:
            self.run_process(label, script, extra)
        except Exception:
            self.log("Error!! Invalid data folder.")

    def Cob_parm(self):
        mode_map = {0: ("fp", self.dlg.fp_parm), 1: ("cp", self.dlg.cp_parm), 2: ("dp", self.dlg.dp_parm)}
        mode, widget = mode_map.get(self.dlg.tabWidget.currentIndex(), (None, None))
        if not mode:
            return

        parm = widget.currentIndex()
        enabled_widgets = COB_UI_MAP.get(mode, {}).get(parm, [])

        # Disable all first
        for w in ["inFolder_fp", "fp_browse", "inFolder_cp", "cp_browse", "cp_sb_psi", "cp_sb_chi", "inFolder_dp", "dp_browse"]:
            getattr(self.dlg, w).setEnabled(False)
        self.dlg.pb_process.setEnabled(False)

        # Enable required widgets
        for w in enabled_widgets:
            getattr(self.dlg, w).setEnabled(True)
        if enabled_widgets:
            self.dlg.pb_process.setEnabled(True)

    #################################################################################################
    # Handlers (stdout/stderr/progress)
    #################################################################################################
    def handle_stdout(self):
        output = self.process.readAllStandardOutput().data().decode()
        for line in output.splitlines():
            self.log(line.strip())
            match = re.search(r'progress: (\d+)', line)
            if match:
                self.pBarupdate(int(match.group(1)))

    def handle_stderr(self):
        error_output = self.process.readAllStandardError().data().decode().strip()
        print("QProcess Error:", error_output)

    def handle_finished(self, exitCode, exitStatus):
        self.log("Ready to process.")
        path = os.path.realpath(self.inFolder)
        os.startfile(path)
        print(f"Process finished with exit code: {exitCode}, status: {exitStatus}")

    def pBarupdate(self, signal):
        self.dlg.progressBar.setValue(int(signal))

    #################################################################################################
    # GUI/Plugin lifecycle
    #################################################################################################
    def add_action(self, icon_path, text, callback, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        self.Startup()
        return action

    def initGui(self):
        icon_path = ':/plugins/SAR_Tools/icon.png'
        self.add_action(icon_path, text=self.tr(u'Process'), callback=self.run, parent=self.iface.mainWindow())

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&PolSAR tools'), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        if self.first_start is True:
            self.first_start = False
            self.dlg = PST_Dialog()
        self.dlg.show()
        DialogExec(self.dlg)

    def Startup(self):
        logger = self.dlg.terminal
        logger.append("\n\tWelcome to PolSAR tools!")
        logger.append("\t================================\n")
        logger.append("\tThis plugin generates Polarimetric SAR parameters.")
        logger.append("\t   🔹 SAR Indices       🔹 Decomposition Parameters\n")
        logger.append("\t-----------------------------------------------------------------\n")
        logger.append('Tip: Start by selecting a parameter from the "Select Parameter" dropdown menu.\n')

#################################################################################################
# Exception
#################################################################################################
class UserAbortedNotification(Exception):
    pass
