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


def nisar_import_process(self):
    file_path = self.nisar_inFile.text()
    self.inFolder = file_path 
    if not file_path:
        return

    # Using the logic_parent we attached in the open_nisar_import function
    main_window_ui = getattr(self, 'logic_parent', None)
    main_window_ui.inFolder = os.path.join(os.path.dirname(file_path), os.path.basename(file_path).split('.h5')[0])
    
    
    if main_window_ui:
        # script_name should be the relative path to your nisar script
        script_rel_path = "functions/sensors/import_nisar.py" 
        
        main_window_ui.run_process(
            label="NISAR GCOV", 
            script_name=script_rel_path, 
            extra_args=[file_path], # This becomes sys.argv[1]
            is_import=True
        )
        
        self.close() # Close the small import window

def nisar_close_fn(self):
    """Close the dialog"""
    self.close()