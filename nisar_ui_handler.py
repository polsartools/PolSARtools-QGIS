import os
# from process_runner import PROCESS_MAP 
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

def nisar_browse_fn(self):
    """Select a NISAR file or folder"""
    file_filter = "HDF5 Files (*.h5);;All files (*.*)"
    filename, _ = QFileDialog.getOpenFileName(
        self, "Select NISAR Data File", "", file_filter
    )
    if filename:
        self.nisar_inFile.setText(filename)

def nisar_help_fn(self):
    """Show a help message box"""
    QMessageBox.information(
        self, "NISAR Import Help",
        "Select a valid NISAR .h5 file and click Import to process the data into QGIS."
    )


# def nisar_import_process(self):
#     file_path = self.nisar_inFile.text()
#     self.inFolder = file_path 
#     if not file_path:
#         return

#     # Using the logic_parent we attached in the open_nisar_import function
#     main_window_ui = getattr(self, 'logic_parent', None)
#     main_window_ui.inFolder = os.path.join(os.path.dirname(file_path), os.path.basename(file_path).split('.h5')[0])
    

#     if main_window_ui:
#         # script_name should be the relative path to your nisar script
#         script_rel_path = "functions/sensors/import_nisar.py" 
        
#         main_window_ui.run_process(
#             label="NISAR GCOV", 
#             script_name=script_rel_path, 
#             extra_args=[file_path], # This becomes sys.argv[1]
#             is_import=True
#         )
        
#         self.close() # Close the small import window

def nisar_import_process(self):
    file_path = self.nisar_inFile.text()
    if not file_path or not os.path.exists(file_path):
        QMessageBox.warning(self, "Error", "Select a valid file.")
        return

    polsar_logic = getattr(self, 'logic_parent', None)
    polsar_logic.inFolder = os.path.join(os.path.dirname(file_path), os.path.basename(file_path).split('.h5')[0])
    if not polsar_logic:
        return

    # 1. Collect Radio Button Values (Product Type)
    product_type = "GCOV" # Default
    if self.RSLC.isChecked(): product_type = "RSLC"
    elif self.GSLC.isChecked(): product_type = "GSLC"
    elif self.GCOV.isChecked(): product_type = "GCOV"

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
        file_path,      # sys.argv[1] (already handled by run_process is_import=True)
        product_type,   # sys.argv[2]
        matrix,         # sys.argv[3]
        azlks,          # sys.argv[4]
        rglks,          # sys.argv[5]
        reciprocity,    # sys.argv[6]
        out_format,     # sys.argv[7]
        compression     # sys.argv[8]
    ]

    # Update logic parent and run
    polsar_logic.inFolder = os.path.dirname(file_path)
    polsar_logic.run_process(
        label=f"NISAR {product_type}", 
        script_name="functions/sensors/import_nisar.py", 
        extra_args=extra_args, # Pass the new list here
        is_import=True
    )
    
    self.close()


def nisar_close_fn(self):
    """Close the dialog"""
    self.close()