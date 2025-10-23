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
import sys
import os
import platform
import subprocess
#################################################################################################
# Process Mapping
#################################################################################################
PROCESS_MAP = {
    "pp": {
        1: ("MLOOK", "functions/preprocess/run_mlook.py", ["azlks", "rglks"]),
        2: ("BOXCAR", "functions/preprocess/run_boxcar.py", []),
        3: ("RFLEE", "functions/preprocess/run_rflee.py", []),
        4: ("Convert S", "functions/preprocess/run_convert_s.py", ["azlks", "rglks","mat"]),
    },

    "fp": {
    1: ("GRVI FP", "functions/fp/run_fp.py", ["func=grvi"]),
    2: ("NM3CF FP", "functions/fp/run_fp.py", ["func=mf3cf"]),
    3: ("PRVI FP", "functions/fp/run_fp.py", ["func=prvi_fp"]),
    4: ("DOP FP", "functions/fp/run_fp.py", ["func=dop_fp"]),
    5: ("RVI FP", "functions/fp/run_fp.py", ["func=rvi_fp"]),
    6: ("MF4CF FP", "functions/fp/run_fp.py", ["func=mf4cf"]),
    7: ("H Alpha FP", "functions/fp/run_fp.py", ["func=halpha_fp"]),
    8: ("TSVM FP", "functions/fp/run_fp.py", ["func=tsvm"]),
    9: ("Freeman 3c FP", "functions/fp/run_fp.py", ["func=freeman_3c"]),
    10: ("Freeman 2c FP", "functions/fp/run_fp.py", ["func=freeman_2c"]),
    11: ("Neumann FP", "functions/fp/run_fp.py", ["func=neu_fp"]),
    12: ("NNED FP", "functions/fp/run_fp.py", ["func=nned_fp"]),
    13: ("Shannon FP", "functions/fp/run_fp.py", ["func=shannon_h_fp"]),
    14: ("Praks FP", "functions/fp/run_fp.py", ["func=praks_parm_fp"]),
    15: ("Yamaguchi 4c FP", "functions/fp/run_yam4c.py", ["model=y4co"]),         
    16: ("Yamaguchi 4cr FP", "functions/fp/run_yam4c.py", ["model=y4cr"]), 
    17: ("Yamaguchi 4cs FP", "functions/fp/run_yam4c.py", ["model=y4cs"]),
    },
    
    
    "cp": {

        1: ("NM3CC CP", "functions/cp/run_cp.py", ["tau", "psi", "chi","func=mf3cc"]),
        2: ("DOP CP", "functions/cp/run_cp.py", ["tau", "psi", "chi","func=dop_cp"]),
        3: ("CPRVI", "functions/cp/run_cp.py", ["tau", "psi", "chi","func=cprvi"]),
        4: ("miSOmega", "functions/cp/run_cp.py", ["tau", "psi", "chi","func=misomega"]),
        
        
    },
    "dp": {

        1: ("DpRVI", "functions/dp/run_dp.py", ["func=dprvi"]),
        2: ("PRVI dp", "functions/dp/run_dp.py", ["func=prvi_dp"]),
        3: ("DOP dp", "functions/dp/run_dp.py", ["func=dop_dp"]),
        4: ("RVI dp", "functions/dp/run_dp.py", ["func=rvi_dp"]),
        5: ("H Alpha dp", "functions/dp/run_dp.py", ["func=halpha_dp"]),
        6: ("Shannon dp", "functions/dp/run_dp.py", ["func=shannon_h_dp"]),
    }
}


#################################################################################################
# Process Runner
#################################################################################################
def run_process(self, label, script_name, extra_args=None):
    self.dlg.progressBar.setValue(0)
    self.log(f"Calculating {label}...")
    self.process = QProcess()
    # self.process.setProgram("python")
    self.process.setProgram(sys.executable)  # Cross-platform Python interpreter

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

    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        self.log(f"Could not open folder: {e}")

    print(f"Process finished with exit code: {exitCode}, status: {exitStatus}")


def pBarupdate(self, signal):
    self.dlg.progressBar.setValue(int(signal))