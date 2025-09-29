
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *

from qgis.PyQt import *
from qgis.core import *
import requests
import numpy as np
import multiprocessing

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .SAR_Tools_dialog import PST_Dialog
import os.path
from osgeo import gdal
import time
import os.path


##############################################################################################

class your_class(QtCore.QObject):

    def __init__(self,iFolder,data_stack,var_list):
        QtCore.QObject.__init__(self)

        self.iFolder = iFolder
        self.C2 = data_stack
        self.v1=var_list[0]
        self.v2=var_list[1]
        self.killed = False
        # self.mainObj = MRSLab()
        

    
    def run(self):
        finish_cond = 0
        try:
            def your_fun(C2_stack,v1,v2):

                """
                
                Your Code here
                
                
                """

                
                your_desc = C2_stack*v1 # add your code
                
                
                self.progress.emit('->> Write files to disk...')
                
                """Write files to disk"""
                if (self.iFolder+'/C11.bin'):
                    infile = self.iFolder+'/C11.bin'
                else:
                    infile = self.iFolder+'/T11.bin'
                
                your_desc = self.iFolder+'/your_dec.bin'
                write_bin(your_desc,your_desc,infile)
                
                self.pBar.emit(100)
                self.progress.emit('->> Finished calculation!!')


            

            def write_bin(file,wdata,refData):
                
                ds = gdal.Open(refData)
                [cols, rows] = wdata.shape
            
                driver = gdal.GetDriverByName("ENVI")
                outdata = driver.Create(file, rows, cols, 1, gdal.GDT_Float32)
                outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
                outdata.SetProjection(ds.GetProjection())##sets same projection as input
                
                outdata.SetDescription(file)
                outdata.GetRasterBand(1).WriteArray(wdata)
                # outdata.GetRasterBand(1).SetNoDataValue(np.NaN)##if you want these values transparent
                outdata.FlushCache() ##saves to disk!!    
        
            # self.dop_fp(self.T3)
            your_fun(self.C2,self.v1,self.v2)
            
            finish_cond = 1
            
        
        except Exception as e:
            # forward the exception upstream
            self.error.emit(e, traceback.format_exc())
            
        self.finished.emit(finish_cond)
        
    # def kill(self):
    #     self.killed = True
        

        
    """***************************************"""
    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(Exception, str)
    progress = QtCore.pyqtSignal(str)     
    pBar =  QtCore.pyqtSignal(int)             
