# SAR_Tools.py
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
import os, multiprocessing, webbrowser

from pip._internal import main as pip_main

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
        self.menu = self.tr(u'&PolSAR tools')
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
        self.dlg.fp_browse.clicked.connect(self.openRaster)
        self.dlg.cp_browse.clicked.connect(self.openRaster)
        self.dlg.dp_browse.clicked.connect(self.openRaster)

        self.dlg.fp_parm.currentIndexChanged.connect(self.Cob_parm)
        self.dlg.cp_parm.currentIndexChanged.connect(self.Cob_parm)
        self.dlg.dp_parm.currentIndexChanged.connect(self.Cob_parm)

        self.dlg.cp_sb_psi.valueChanged.connect(self.psi_update)
        self.dlg.cp_sb_chi.valueChanged.connect(self.chi_update)

        self.dlg.fp_ws.valueChanged.connect(self.ws_update)
        self.dlg.cp_ws.valueChanged.connect(self.ws_update)
        self.dlg.dp_ws.valueChanged.connect(self.ws_update)

        self.dlg.pb_view.clicked.connect(self.viewData)
        self.dlg.clear_terminal.clicked.connect(self.clear_log)
        self.dlg.pb_process.clicked.connect(self.startProcess)
        self.dlg.help_btn.clicked.connect(lambda: webbrowser.open('https://sar-tools.readthedocs.io/en/latest/'))
        self.dlg.close_btn.clicked.connect(self.closeui_fn)

        self.dlg.tabWidget.currentChanged.connect(self.Cob_parm)

        self.check_pstools()

    def check_pstools(self):
        try:
            import polsartools
        except ImportError:
            pip_main(['install', 'polsartools'])
            
    def tr(self, message): return QCoreApplication.translate('PolSAR', message)
    def log(self, message): self.dlg.terminal.append(f"(polsartools) $ {message}")

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
