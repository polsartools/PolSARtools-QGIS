General Information
===================

This plugin generates derived SAR parameters (viz. vegetation indices, polarimetric decomposition parameters) from input polarimetric matrix (C3, T3, C2, T2). 

Installation
-------------------

.. note::

    PolSAR tools requires QGIS version >=3.0.


* The easiest way (requires internet connection) : 
	- Open QGIS -> Plugins -> Manage and Install Plugins... --> select ``All`` tab -> search for ``PolSAR tools`` --> select and install plugin
* Alternative way (offline installation) : 
	- Go to `releases`_ of PolSAR tools -> select desired version -> download the ``.zip`` file.
	- Open QGIS -> Plugins -> Manage and Install Plugins... --> ``install from ZIP`` tab --> select the downloaded zip --> install plugin (ignore warnings, if any).

.. _Up and running:

Up and running
--------------------

After successful installation, find the plugin by opening **QGIS** --> Plugins --> ``PolSAR tools`` --> Process. As shown in the following figure.

.. figure:: figures/open_ui.png
    :scale: 80%
    :align: center
    
    Opening the plugin 

.. figure:: figures/main_ui.png
    :scale: 60%
    :align: center
    
    GUI-Main window layout

**Layout**:

1. Data type tabs: Functions are arranged according to the data dype (full-, compact- and dual-pol).
2. Function detials viewer: Contains list of functions for respective data tab. 
3. Derived arameter selection, required input variables and constraints.
4. Input data folder
5. Logger: displays the log of procesing parameters
6. progressbar: displays the progress of current task.
7. Credits and quick help.


Additional ``reset`` button to clear the envirinment, ``view data`` button to import the data into **QGIS** environment and ``Process`` button to start processing after selecting valid input data variables. 

 

Available functionalities
--------------------------
  PolSAR tools plugin currently supports all the Full, compact and dual plarimetric functionalities avaialbel in polsartools python package. A complete list of functiones can be found `here  <https://polsartools.readthedocs.io/en/stable/files/02functions.html>`_

Example usage
--------------
.. note::

    All the following processing steps should be done in sequential manner. Sample data for all the polarization modes is provided in [sample_data](/sample_data/) folder.


**STEP 1**: Open the plugin as explained in :ref:`Up and running` section.

**STEP 2**: Select the polarimetric data type (Full/compact/dual).

.. figure:: figures/step2.png
    :scale: 50%
    :align: center
    
    Selecting the polarimetric mode

**STEP 3**: Select the parameter/descriptor from the dropdown menu.

.. figure:: figures/step3.png
    :scale: 50%
    :align: center
    
    Selecting the polarimetric descriptor

**STEP 4**: Provide the required input variables.

.. figure:: figures/step4.png
    :scale: 50%
    :align: center
    
    Selecting the input variables

**STEP 5**: Select the input matrix folder.

.. figure:: figures/step5.png
    :scale: 45%
    :align: center
    
    Selecting the input folder

**STEP 6**: Wait for the logger to prompt ```->> Ready to process.``` --> click process

.. note::
    Do not click process button more than once while it is processing. It may crash the QGIS and the plugin.
    It is possible that the plugin may show not responding for larger datasets but please wait for the process to complete.

.. figure:: figures/step6.png
    :scale: 45%
    :align: center
    
    Processing the data for selected descriptor

**STEP 7** (optional): Click view data to import the data into QGIS for vizualisation of the generated descriptors.

.. figure:: figures/step7a.png
    :scale: 45%
    :align: center
    
    Importing the data into QGIS for visualization

.. figure:: figures/step7b.png
    :scale: 45%
    :align: center
    
    Imported data in QGIS


Contributions
-------------

1) Contribute to the software

    `Contribution guidelines for this project  <https://github.com/polsartools/PolSARtools-QGIS/blob/master/help/CONTRIBUTING.md>`_


2) Report issues or problems with the software
  
  Please raise your issues here : https://github.com/polsartools/PolSARtools-QGIS/issues


.. _releases: https://github.com/polsartools/PolSARtools-QGIS/releases