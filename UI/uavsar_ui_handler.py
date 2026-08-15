# polsar_tools/uavsar_ui_handler.py
import os
# from process_runner import PROCESS_MAP 
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

def uavsar_browse_fn(self):
    """Select a UAVSAR file or folder"""
    file_filter = "ANN Files (*.ann);;All files (*.*)"
    filename, _ = QFileDialog.getOpenFileName(
        self, "Select UAVSAR Data File", "", file_filter
    )
    if filename:
        self.uavsar_inFile.setText(filename)

def uavsar_help_fn(self):
    """Show a help message box"""
    QMessageBox.information(
        self, "UAVSAR Import Help",
        "Select a valid UAVSAR .ann file and click Import to process the data into QGIS."
    )

def uavsar_import_process(self):
    file_path = self.uavsar_inFile.text()
    if not file_path or not os.path.exists(file_path):
        QMessageBox.warning(self, "Error", "Select a valid file.")
        return

    polsar_logic = getattr(self, 'logic_parent', None)
    polsar_logic.inFolder = os.path.join(os.path.dirname(file_path), os.path.basename(file_path).split('.h5')[0])
    if not polsar_logic:
        return

    # 1. Collect Radio Button Values (Product Type)
    product_type = "GRD" # Default
    if self.GRD.isChecked(): product_type = "GRD"
    elif self.MLC.isChecked(): product_type = "MLC"


    # 2. Collect Matrix and Looks
    matrix = self.pp_mat.currentText()
    # azlks = str(self.pp_azlks.value())
    # rglks = str(self.pp_rglks.value())
    
    # 3. Collect Booleans (Reciprocity and Compression)
    # Using lower() to match python boolean strings 'true'/'false'
    # reciprocity = self.pp_mat_4.currentText().lower() 
    out_format = self.pp_mat_2.currentText()
    compression = self.pp_mat_3.currentText().lower()

    # 4. Prepare Arguments for the script
    # The order here must match sys.argv indexing in your import_nisar.py
    extra_args = [
        file_path,      # sys.argv[1] 
        product_type,   # sys.argv[2]
        matrix,         # sys.argv[3]
        # azlks,          # sys.argv[4]
        # rglks,          # sys.argv[5]
        # reciprocity,    # sys.argv[6]
        out_format,     # sys.argv[7]
        compression     # sys.argv[8]
    ]

    
    polsar_logic.inFolder = os.path.dirname(file_path)
    polsar_logic.run_process(
        label=f"UAVSAR {product_type}", 
        script_name="functions/sensors/import_uavsar.py", 
        extra_args=extra_args, 
        is_import=True
    )
    
    self.close()


def uavsar_close_fn(self):
    """Close the dialog"""
    self.close()