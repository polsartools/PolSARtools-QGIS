import os,re
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import QProcess

from qgis.PyQt import *
from qgis.core import *

from .qt_compat import (
    QtCore, QtGui, QtWidgets, Qt,
    DialogExec, MessageIcon, MessageButton,
    AlignmentFlag, Key, PYQT_VERSION
)

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