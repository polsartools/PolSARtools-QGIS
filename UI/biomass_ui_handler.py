# polsar_tools/biomass_ui_handler.py
import os
# from process_runner import PROCESS_MAP 
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

# def biomass_browse_fn(self):
#     """Select a BIOMASS file or folder"""
#     file_filter = "All files (*.*)"
#     filename, _ = QFileDialog.getOpenFileName(
#         self, "Select BIOMASS Data Folder", "", file_filter
#     )
#     if filename:
#         self.biomass_inFile.setText(filename)


def biomass_browse_fn(self):
    """Select a BIOMASS folder"""
    folder_path = QFileDialog.getExistingDirectory(
        self, "Select BIOMASS Data Folder", ""
    )
    if folder_path:
        self.biomass_inFile.setText(folder_path)

def biomass_help_fn(self):
    """Show a help message box"""
    QMessageBox.information(
        self, "BIOMASS Import Help",
        "Select a valid BIOMASS data folder and click Import to process the data into QGIS."
    )

def biomass_import_process(self):
    file_path = self.biomass_inFile.text()
    if not file_path or not os.path.exists(file_path):
        QMessageBox.warning(self, "Error", "Select a valid folder.")
        return

    polsar_logic = getattr(self, 'logic_parent', None)
    polsar_logic.inFolder = os.path.join(os.path.dirname(file_path), os.path.basename(file_path).split('.h5')[0])
    if not polsar_logic:
        return

    # 1. Collect Radio Button Values (Product Type)
    product_type = "L1A" # Default
    if self.L1A.isChecked(): product_type = "L1A"
    elif self.L1B.isChecked(): product_type = "L1B"


    # 2. Collect Matrix and Looks
    matrix = self.pp_mat.currentText()
    azlks = str(self.pp_azlks.value())
    rglks = str(self.pp_rglks.value())
    
    # 3. Collect Booleans (Reciprocity and Compression)
    # Using lower() to match python boolean strings 'true'/'false'
    reciprocity = self.pp_mat_4.currentText().lower() 
    out_format = self.pp_mat_2.currentText()
    compression = self.pp_mat_3.currentText().lower()

    # 4. Prepare Arguments for the script
    # The order here must match sys.argv indexing in your import_nisar.py
    extra_args = [
        file_path,      # sys.argv[1] 
        product_type,   # sys.argv[2]
        matrix,         # sys.argv[3]
        azlks,          # sys.argv[4]
        rglks,          # sys.argv[5]
        reciprocity,    # sys.argv[6]
        out_format,     # sys.argv[7]
        compression     # sys.argv[8]
    ]

    
    polsar_logic.inFolder = os.path.dirname(file_path)
    polsar_logic.run_process(
        label=f"BIOMASS {product_type}", 
        script_name="functions/sensors/import_biomass.py", 
        extra_args=extra_args, 
        is_import=True
    )
    
    self.close()


def biomass_close_fn(self):
    """Close the dialog"""
    self.close()