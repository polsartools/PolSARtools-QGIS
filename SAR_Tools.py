# polsar_tools/SAR_Tools.py
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
import os, multiprocessing, webbrowser

# from pip._internal import main as pip_main

import sys
import platform
import subprocess
import importlib.util

from .SAR_Tools_dialog import PST_Dialog, Nisar_Dialog, Biomass_Dialog,Uavsar_Dialog
from .qt_compat import DialogExec, MessageIcon, MessageButton

# Import helpers
# from .process_runner import PROCESS_MAP, run_process, handle_stdout, handle_stderr, handle_finished, pBarupdate
from .process_runner import (
    PROCESS_MAP, run_process, handle_stdout, handle_stderr, 
    handle_finished, pBarupdate, start_writing_animation, stop_writing_animation
)
from .UI.ui_handlers import Cob_parm, openRaster, viewData, clear_log, psi_update, chi_update, ws_update, closeui_fn, showTip


class PolSAR(object):
    """QGIS Plugin Implementation."""
    sig_abort_workers = pyqtSignal()

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dlg = PST_Dialog()
        self.actions = []
        self.menu = self.tr(u'&PolSAR-tools')
        self.first_start = None

        # State
        self.inFolder = ''
        self.ws = 5
        self.psi_val = 0
        self.chi_val = 45
    

        # Monkey-patch imported helpers so they see self
        self.run_process = run_process.__get__(self)
        self.handle_stdout = handle_stdout.__get__(self)
        self.handle_stderr = handle_stderr.__get__(self)
        self.handle_finished = handle_finished.__get__(self)
        self.pBarupdate = pBarupdate.__get__(self)

        self.Cob_parm = Cob_parm.__get__(self)
        self.openRaster = openRaster.__get__(self)
        self.viewData = viewData.__get__(self)
        self.clear_log = clear_log.__get__(self)
        self.psi_update = psi_update.__get__(self)
        self.chi_update = chi_update.__get__(self)
        self.ws_update = ws_update.__get__(self)
        self.closeui_fn = closeui_fn.__get__(self)
        self.showTip = showTip.__get__(self)

        # Connect UI signals
        self.dlg.pp_browse.clicked.connect(self.openRaster)
        self.dlg.fp_browse.clicked.connect(self.openRaster)
        self.dlg.cp_browse.clicked.connect(self.openRaster)
        self.dlg.dp_browse.clicked.connect(self.openRaster)

        self.dlg.pp_parm.currentIndexChanged.connect(self.Cob_parm)
        self.dlg.fp_parm.currentIndexChanged.connect(self.Cob_parm)
        self.dlg.cp_parm.currentIndexChanged.connect(self.Cob_parm)
        self.dlg.dp_parm.currentIndexChanged.connect(self.Cob_parm)

        self.dlg.cp_sb_psi.valueChanged.connect(self.psi_update)
        self.dlg.cp_sb_chi.valueChanged.connect(self.chi_update)

        self.dlg.pp_ws.valueChanged.connect(self.ws_update)
        self.dlg.fp_ws.valueChanged.connect(self.ws_update)
        self.dlg.cp_ws.valueChanged.connect(self.ws_update)
        self.dlg.dp_ws.valueChanged.connect(self.ws_update)

        self.dlg.pb_view.clicked.connect(self.viewData)
        self.dlg.clear_terminal.clicked.connect(self.clear_log)
        self.dlg.pb_process.clicked.connect(self.startProcess)
        self.dlg.help_btn.clicked.connect(lambda: webbrowser.open('https://sar-tools.readthedocs.io'))
        self.dlg.close_btn.clicked.connect(self.closeui_fn)

        self.dlg.tabWidget.currentChanged.connect(self.Cob_parm)

        # sensors
        self.dlg.nisar_import.clicked.connect(self.open_nisar_import)
        self.dlg.biomass_import.clicked.connect(self.open_biomass_import)
        self.dlg.uavsar_import.clicked.connect(self.open_uavsar_import)

        self.start_writing_animation = start_writing_animation.__get__(self)
        self.stop_writing_animation = stop_writing_animation.__get__(self)

        self.check_pstools()

    def is_flatpak(self):
        """Checks if the current process is running inside a Flatpak container."""
        return os.path.exists("/.flatpak-info") or "FLATPAK_ID" in os.environ

    def check_pstools(self):
        if importlib.util.find_spec("polsartools") is not None:
            return  # Already installed

        # Handle Flatpak environment early
        if self.is_flatpak():
            QMessageBox.critical(None, "Plugin Error",
                "QGIS is running inside a Flatpak sandbox container.\n\n"
                "Automatic installation is blocked due to container isolation.\n\n"
                "To install 'polsartools' for Flatpak QGIS, open your host system terminal "
                "and run this following command:\n\n"
                "flatpak run --devel --command=pip3 org.qgis.qgis install \"polsartools\" \"numpy<2\" --user\n\n"
                "After installation, please restart QGIS.")
            return

        os_type = platform.system()
        base_cmd = [sys.executable, "-m", "pip", "install", "--user", "polsartools"]

        try:
            if os_type == "Linux":
                try:
                    subprocess.check_call(base_cmd)
                except subprocess.CalledProcessError:
                    try:
                        subprocess.check_call(base_cmd + ["--break-system-packages"])
                    except subprocess.CalledProcessError as e:
                        QMessageBox.critical(None, "Plugin Error",
                            "Linux blocks system-wide pip installs.\n\n"
                            "To install manually, run in your terminal:\n"
                            "python3 -m pip install polsartools --user --break-system-packages\n\n"
                            f"Error: {e}")
                        return

            elif os_type in ["Windows", "Darwin"]:
                subprocess.check_call(base_cmd)

            else:
                QMessageBox.critical(None, "Plugin Error",
                    f"Unsupported OS: {os_type}. Please install 'polsartools' manually.")
                return

        except Exception as e:
            QMessageBox.critical(None, "Plugin Error",
                f"Failed to automatically install 'polsartools': {e}\n\n"
                "Please install it manually using pip.")
                
    def tr(self, message): return QCoreApplication.translate('PolSAR', message)
    def log(self, message): self.dlg.terminal.append(f"(polsartools) $ {message}")

    def startProcess(self):
        mode_map = {0: "import",1: "pp", 2: "fp", 3: "cp", 4: "dp"}
        mode = mode_map.get(self.dlg.tabWidget.currentIndex())
        if not mode:
            return
        
        
        if mode == "import":
            return
        
        
        indX = (self.dlg.fp_parm.currentIndex() if mode == "fp"
                else self.dlg.cp_parm.currentIndex() if mode == "cp"
                else self.dlg.dp_parm.currentIndex() if mode == "dp"
                else self.dlg.pp_parm.currentIndex())

        process_info = PROCESS_MAP.get(mode, {}).get(indX)
        if not process_info:
            return

        label, script, required_args = (process_info + ([],))[:3]
        extra = []

        if "tau" in required_args:
            extra.append(str(self.dlg.cp_cb_tau.currentIndex()))
        if "psi" in required_args:
            extra.append(str(self.psi_val))
        if "chi" in required_args:
            extra.append(str(self.chi_val))
        if "azlks" in required_args:
            extra.append(str(self.dlg.pp_azlks.value()))
        if "rglks" in required_args:
            extra.append(str(self.dlg.pp_rglks.value()))
        if "mat" in required_args:
            extra.append(str(self.dlg.pp_mat.currentIndex()))
            
        for arg in required_args:
            if arg.startswith("func="):
                extra.append(arg.split("=")[1])
            if arg.startswith("model="):
                extra.append(arg.split("=")[1])


        try:
            self.run_process(label, script, extra)
        except Exception as e:
            self.log("Error!! Invalid data folder.")
            self.log(f"Exception: {str(e)}")

          
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
        icon_path = ':/plugins/polsar_tools/icon.png'
        self.add_action(icon_path, text=self.tr(u'Process'), callback=self.run, parent=self.iface.mainWindow())

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&PolSAR-tools'), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        if self.first_start is True:
            self.first_start = False
            self.dlg = PST_Dialog()
        self.dlg.show()
        DialogExec(self.dlg)

    def Startup(self):
        logger = self.dlg.terminal
        logger.append("\n\t\tWelcome to PolSAR tools!")
        logger.append("\t================================\n")
        logger.append("\tThis plugin generates Polarimetric SAR parameters.")
        logger.append("\t   🔹 SAR Indices       🔹 Decomposition Parameters\n")
        logger.append("\t-----------------------------------------------------------------\n")
        logger.append('Tip: Start by selecting a function from the "Select function" dropdown menu.\n')


    def open_nisar_import(self):
        self.nisar_win = Nisar_Dialog(self.dlg) 
        self.nisar_win.logic_parent = self 
        self.nisar_win.show()

    def open_biomass_import(self):
        self.biomass_win = Biomass_Dialog(self.dlg) 
        self.biomass_win.logic_parent = self 
        self.biomass_win.show()
    def open_uavsar_import(self):
        self.uavsar_win = Uavsar_Dialog(self.dlg) 
        self.uavsar_win.logic_parent = self 
        self.uavsar_win.show()
#################################################################################################
# Exception
#################################################################################################
class UserAbortedNotification(Exception):
    pass
