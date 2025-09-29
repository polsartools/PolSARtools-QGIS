
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *

from qgis.PyQt import *
from qgis.core import *
import requests
import numpy as np
import multiprocessing

# Initialize Qt resources from file resources.py
from ...resources import *
# Import the code for the dialog
from ...SAR_Tools_dialog import MRSLabDialog
import os.path
from osgeo import gdal
import time
import os.path


##############################################################################################

class NM3CC(QtCore.QObject):
    '''NM3CC '''
    def __init__(self,iFolder,C2,ws,tau):
        QtCore.QObject.__init__(self)

        self.iFolder = iFolder
        self.C2 = C2
        self.ws=ws
        self.tau=tau
        self.killed = False
        # self.mainObj = MRSLab()
        
    def conv2d(self,a, f):
        filt = np.zeros(a.shape)
        wspad = int(f.shape[0]/2)
        s = f.shape + tuple(np.subtract(a.shape, f.shape) + 1)
        strd = np.lib.stride_tricks.as_strided
        subM = strd(a, shape = s, strides = a.strides * 2)
        filt_data = np.einsum('ij,ijkl->kl', f, subM)
        filt[wspad:wspad+filt_data.shape[0],wspad:wspad+filt_data.shape[1]] = filt_data
        return filt
    
    def run(self):
        finish_cond = 0
        try:
            def NM3CC_fn(C2_stack,ws):

                if self.tau==0:                    
                    chi_in = -45.0
                else:
                    chi_in = 45.0

                kernel = np.ones((ws,ws),np.float32)/(ws*ws)
                c11_T1 = C2_stack[:,:,0]
                c12_T1 = C2_stack[:,:,1]
                c21_T1 = C2_stack[:,:,2]
                c22_T1 = C2_stack[:,:,3]
            
                c11_T1r = self.conv2d(np.real(c11_T1),kernel)
                c11_T1i = self.conv2d(np.imag(c11_T1),kernel)
                c11s = c11_T1r+1j*c11_T1i

                c12_T1r = self.conv2d(np.real(c12_T1),kernel)
                c12_T1i = self.conv2d(np.imag(c12_T1),kernel)
                c12s = c12_T1r+1j*c12_T1i
                self.pBar.emit(25)

                c21_T1r = self.conv2d(np.real(c21_T1),kernel)
                c21_T1i = self.conv2d(np.imag(c21_T1),kernel)
                c21s = c21_T1r+1j*c21_T1i


                c22_T1r = self.conv2d(np.real(c22_T1),kernel)
                c22_T1i = self.conv2d(np.imag(c22_T1),kernel)
                c22s = c22_T1r+1j*c22_T1i

                self.pBar.emit(50)

                c2_det = (c11s*c22s-c12s*c21s)
                c2_trace = c11s+c22s
                # t2_span = t11s*t22s
                m1 = np.real(np.sqrt(1.0-(4.0*c2_det/np.power(c2_trace,2))))

                # Stokes Parameter
                s0 = c11s + c22s;
                s1 = c11s - c22s;
                s2 = (c12s + c21s);

                if (chi_in >= 0):
                    s3 = (1j*(c12s - c21s)); # The sign is according to RC or LC sign !!
                if (chi_in < 0):
                    s3 = -(1j*(c12s - c21s)); # The sign is according to RC or LC sign !!
                
                SC = ((s0)-(s3))/2;
                OC = ((s0)+(s3))/2;

                h = (OC-SC)
                span = c11s + c22s

                val = ((m1*s0*h))/((SC*OC + (m1**2)*(s0**2)))
                thet = np.real(np.arctan(val))
                theta_CP = np.rad2deg(thet)

                Ps_CP= (((m1*(span)*(1.0+np.sin(2*thet))/2)))
                Pd_CP= (((m1*(span)*(1.0-np.sin(2*thet))/2)))
                Pv_CP= (span*(1.0-m1))
                
                self.pBar.emit(90)                        
                
                self.progress.emit('->> Write files to disk...')
                """Write files to disk"""
                # ofilervi = self.iFolder+'/RVI.bin'
                infile = self.iFolder+'/C11.bin'
                # write_bin(ofilervi,rvi,infile)
                ofilegrvi = self.iFolder+'/Theta_CP.bin'
                write_bin(ofilegrvi,theta_CP,infile)
                ofilegrvi1 = self.iFolder+'/Pd_CP.bin'
                write_bin(ofilegrvi1,Pd_CP,infile)
                ofilegrvi2 = self.iFolder+'/Ps_CP.bin'
                write_bin(ofilegrvi2,Ps_CP,infile)
                ofilegrvi3 = self.iFolder+'/Pv_CP.bin'
                write_bin(ofilegrvi3,Pv_CP,infile)     
    
                self.pBar.emit(100)
                self.progress.emit('->> Finished MF3CC calculation!!')


            

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
            NM3CC_fn(self.C2,self.ws)
            
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
