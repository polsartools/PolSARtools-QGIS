# SAR_Tools.py
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
import os, multiprocessing, webbrowser

from pip._internal import main as pip_main

import sys
import platform
import subprocess
import importlib.util

from .SAR_Tools_dialog import PST_Dialog
from .qt_compat import DialogExec, MessageIcon, MessageButton

# Import helpers
from .process_runner import PROCESS_MAP, run_process, handle_stdout, handle_stderr, handle_finished, pBarupdate
from .ui_handlers import Cob_parm, openRaster, viewData, clear_log, psi_update, chi_update, ws_update, closeui_fn, showTip


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

        self.check_pstools()

    # def check_pstools(self):
    #     try:
    #         import polsartools
    #     except ImportError:
    #         pip_main(['install', 'polsartools'])

    # def check_pstools(self):
    #     try:
    #         import polsartools
    #     except ImportError:
    #         try:
    #             import sys
    #             import io
    #             if sys.stderr is None:
    #                 sys.stderr = io.StringIO()

    #             from pip._internal import main as pip_main
    #             pip_main(['install', 'polsartools'])

    #             # Try importing again after installation
    #             import polsartools
    #         except Exception as e:
    #             from qgis.PyQt.QtWidgets import QMessageBox
    #             QMessageBox.critical(None, "Plugin Error", f"Failed to install 'polsartools': {e}")
    #             # pass


    # def check_pstools(self):
    #     try:
    #         import polsartools
    #     except ImportError:
    #         try:
    #             os_type = platform.system()

    #             if os_type == "Windows":
    #                 subprocess.check_call([sys.executable, "-m", "pip", "install", "polsartools"])

    #             elif os_type == "Linux":
    #                 # Linux may block pip installs in system Python (PEP 668)
    #                 try:
    #                     subprocess.check_call([sys.executable, "-m", "pip", "install", "polsartools"])
    #                 except subprocess.CalledProcessError as e:
    #                     QMessageBox.critical(None, "Plugin Error",
    #                         "Linux system Python may be externally managed.\n"
    #                         "Try installing 'polsartools' manually in a virtual environment or using pipx.\n\n"
    #                         f"Error: {e}")
    #                     return

    #             elif os_type == "Darwin":  # macOS
    #                 subprocess.check_call([sys.executable, "-m", "pip", "install", "polsartools"])

    #             else:
    #                 QMessageBox.critical(None, "Plugin Error",
    #                     f"Unsupported OS: {os_type}. Please install 'polsartools' manually.")
    #                 return

    #             # Try importing again after installation
    #             import polsartools

    #         except Exception as e:
    #             QMessageBox.critical(None, "Plugin Error", f"Failed to install 'polsartools': {e}")

    def check_pstools(self):
        if importlib.util.find_spec("polsartools") is not None:
            return  # Already installed

        os_type = platform.system()
        base_cmd = [sys.executable, "-m", "pip", "install", "polsartools"]

        try:
            if os_type == "Linux":
                try:
                    # Try normal install first
                    subprocess.check_call(base_cmd)
                except subprocess.CalledProcessError:
                    # Retry with --break-system-packages
                    try:
                        subprocess.check_call(base_cmd + ["--break-system-packages"])
                    except subprocess.CalledProcessError as e:
                        QMessageBox.critical(None, "Plugin Error",
                            "Linux system Python blocks pip installs due to PEP 668.\n\n"
                            "To install 'polsartools' system-wide, you can run:\n"
                            "  python3 -m pip install polsartools --break-system-packages\n\n"
                            "Or use a virtual environment:\n"
                            "  python3 -m venv myenv && source myenv/bin/activate\n"
                            "  pip install polsartools\n\n"
                            f"Error: {e}")
                        return

            elif os_type in [ "Darwin"]:  # macOS
                subprocess.check_call(base_cmd)
            elif os_type in ["Windows"]:
                pip_main(['install', 'polsartools'])

            else:
                QMessageBox.critical(None, "Plugin Error",
                    f"Unsupported OS: {os_type}. Please install 'polsartools' manually.")
                return

        except Exception as e:
            QMessageBox.critical(None, "Plugin Error",
                f"Failed to install 'polsartools': {e}")

            
    def tr(self, message): return QCoreApplication.translate('PolSAR', message)
    def log(self, message): self.dlg.terminal.append(f"(polsartools) $ {message}")

    def startProcess(self):
        mode_map = {1: "pp", 2: "fp", 3: "cp", 4: "dp"}
        mode = mode_map.get(self.dlg.tabWidget.currentIndex())
        if not mode:
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

#################################################################################################
# Exception
#################################################################################################
class UserAbortedNotification(Exception):
    pass
