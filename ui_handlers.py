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
#################################################################################################
# Parameter-to-UI mapping (for Cob_parm)
#################################################################################################
COB_UI_MAP = {
    "pp": {
        1: ["inFolder_pp", "pp_browse","pp_azlks","pp_rglks"],
        2: ["inFolder_pp", "pp_browse"],
        3: ["inFolder_pp", "pp_browse"],
        4: ["inFolder_pp", "pp_browse","pp_azlks","pp_rglks","pp_mat"],
    },
    "fp": {
        1: ["inFolder_fp", "fp_browse"],
        2: ["inFolder_fp", "fp_browse"],
        3: ["inFolder_fp", "fp_browse"],
        4: ["inFolder_fp", "fp_browse"],
        5: ["inFolder_fp", "fp_browse"],
        6: ["inFolder_fp", "fp_browse"],
        7: ["inFolder_fp", "fp_browse"],
        8: ["inFolder_fp", "fp_browse"],
        9: ["inFolder_fp", "fp_browse"],
        10: ["inFolder_fp", "fp_browse"],
        11: ["inFolder_fp", "fp_browse"],
        12: ["inFolder_fp", "fp_browse"],
        13: ["inFolder_fp", "fp_browse"],
        14: ["inFolder_fp", "fp_browse"],
        15: ["inFolder_fp", "fp_browse"],
        16: ["inFolder_fp", "fp_browse"],
        17: ["inFolder_fp", "fp_browse"],
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
        5: ["inFolder_dp", "dp_browse"],
        6: ["inFolder_dp", "dp_browse"],
    }
}

def Cob_parm(self):
    mode_map = {1: ("pp", self.dlg.pp_parm), 
                2: ("fp", self.dlg.fp_parm), 
                3: ("cp", self.dlg.cp_parm), 
                4: ("dp", self.dlg.dp_parm)}
    mode, widget = mode_map.get(self.dlg.tabWidget.currentIndex(), (None, None))
    if not mode:
        return

    parm = widget.currentIndex()
    enabled_widgets = COB_UI_MAP.get(mode, {}).get(parm, [])

    # Disable all first
    for w in [
              "inFolder_pp", "pp_browse", "pp_azlks","pp_rglks","pp_mat",
              "inFolder_fp", "fp_browse", 
              "inFolder_cp", "cp_browse", "cp_sb_psi", "cp_sb_chi", 
              "inFolder_dp", "dp_browse"]:
        getattr(self.dlg, w).setEnabled(False)
    self.dlg.pb_process.setEnabled(False)

    # Enable required widgets
    for w in enabled_widgets:
        getattr(self.dlg, w).setEnabled(True)
    if enabled_widgets:
        self.dlg.pb_process.setEnabled(True)


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
    # self.showTip() # pop-up tip
    
    if self.dlg.tabWidget.currentIndex() == 1:
        self.inFolder = str(QFileDialog.getExistingDirectory(
                        self.dlg, "Select a PolSAR matrix Folder"))                   
        self.dlg.inFolder_pp.setText(self.inFolder)
        
    if self.dlg.tabWidget.currentIndex() == 2:
        self.inFolder = str(QFileDialog.getExistingDirectory(
                        self.dlg, "Select T3/C3 Folder"))                   
        self.dlg.inFolder_fp.setText(self.inFolder)
        
            
    if self.dlg.tabWidget.currentIndex() == 3:
        self.inFolder = str(QFileDialog.getExistingDirectory(
                        self.dlg, "Select C2 Folder"))
        self.dlg.inFolder_cp.setText(self.inFolder)

    if self.dlg.tabWidget.currentIndex() == 4:
        self.inFolder = str(QFileDialog.getExistingDirectory(
                        self.dlg, "Select C2 Folder"))
        self.dlg.inFolder_dp.setText(self.inFolder)

def closeui_fn(self):
    self.dlg.close()
    
def psi_update(self):
    self.psi_val = float(self.dlg.cp_sb_psi.value())

def chi_update(self):
    self.chi_val = float(self.dlg.cp_sb_chi.value())
        
def ws_update(self):
    if self.dlg.tabWidget.currentIndex()==1:
        self.ws = int(self.dlg.pp_ws.value())    
    if self.dlg.tabWidget.currentIndex()==2:
        self.ws = int(self.dlg.fp_ws.value())
    if self.dlg.tabWidget.currentIndex()==3:
        self.ws = int(self.dlg.cp_ws.value())
    if self.dlg.tabWidget.currentIndex()==4:
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
    self.dlg.inFolder_pp.clear()
    self.dlg.inFolder_fp.clear()
    self.dlg.inFolder_cp.clear()
    self.dlg.inFolder_dp.clear()
    # self.dlg.inFolder_fp.setEnabled(False)
    # self.dlg.fp_browse.setEnabled(False)
    self.dlg.progressBar.setValue(0)
    self.dlg.pp_ws.setValue(5)
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