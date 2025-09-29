---
title: 'PolSAR tools: A QGIS plugin for generating SAR descriptors'
tags:
  - SAR
  - QGIS
  - Vegetation indices
  - Polarimetric decompositions
authors:
  - name: Narayanarao Bhogapurapu
    orcid: 0000-0002-6496-7283
    affiliation: 1
  - name: Subhadip Dey
    orcid: 0000-0002-4979-0192
    affiliation: 1
  - name: Dipankar Mandal
    orcid: 0000-0001-8407-7125
    affiliation: 1
  - name: Avik Bhattacharya
    orcid: 0000-0001-6720-6108
    affiliation: 1
  - name: Y. S. Rao
    orcid: 0000-0002-6351-2391
    affiliation: 1
affiliations:
 - name: Microwave Remote Sensing Lab, Centre of Studies in Resources Engineering, Indian Institute of Technology Bombay, Mumbai-400076, India
   index: 1

date: 2 December 2020
bibliography: paper.bib

---

# Statement of need

The demand for processing tools increases with the increasing number of ***Synthetic Aperture Radar (SAR)*** satellite missions and datasets. However, to process SAR data, a minimal number of free tools are available ([PolSARpro](https://earth.esa.int/web/polsarpro/home), [SNAP](https://step.esa.int/main/toolboxes/snap/)), which consolidates all necessary pre-processing steps. Bearing this in mind, there is a need to develop specific tools for the remote sensing user community to derive polarimetric descriptors like the vegetation indices and decomposition parameters. Besides, to the best of our knowledge, there are no such free tools available on the GIS platform, which are quite necessary for SAR remote sensing. 

Hence we have developed a plugin for ```QGIS``` that supports data for the three available polarimetric modes (i.e., full-, compact, and dual). The ```PolSAR tools``` plugin generates polarimetric descriptors (viz., vegetation indices, polarimetric decomposition parameters) from the 3x3 (C3/T3) or the 2x2 (C2/T2) covariance (coherency) matrices obtained from the ESA's [PolSARpro](https://earth.esa.int/web/polsarpro/home) software. The input data needs to be in PolSARpro format (```*.bin``` and ```*.hdr```). The plugin is coded in Python and is dependant on the Quantum GIS framework. It uses the following libraries (bundled with Quantum GIS): [numpy](https://numpy.org/), [gdal](https://gdal.org/) and [QGIS](https://qgis.org/en/site/index.html) core library.

# Background
Conventional model-based decomposition methods utilize diverse scattering models and typical hierarchical rule to enumerate power components leading to numerous limitations. The ***polarimetric decomposition techniques*** incorporated in this ```QGIS``` plugin are model-free, i.e., no prior scattering models are assumed to compute the powers. The proposed decomposition techniques utilize certain novel roll-invariant target characterization parameters to decompose the total power into even bounce, odd bounce, and diffused power components. It is guaranteed that the proposed technique's powers are non-negative, which is seldom true with the existing methodologies.

In terms of target descriptors, we often use ***vegetation indices*** as plant growth proxies. While appreciating the potential of vegetation indices derived from optical remote sensing sensors, regional to global products have been supported for operational uses. These days, the ```Earth Observation (EO) community``` relies on SAR imaging technology due to its all-weather imaging capability among its numerous advantages. The SAR images are presently processed by several downstream users and are more frequently interpreted by non-radar specialists. This paradigm shift allows the utility of radar-derived vegetation indices towards a quintessential goal of ```Analysis Ready Data (ARD)``` products.

Recently, we proposed three vegetation indices: ```GRVI``` (Generalized Radar Vegetation Index) [@ratha2019generalized], ```CpRVI``` (Compact-pol Radar Vegetation Index) [@mandal2020radar], and Dual-pol Radar Vegetation Index (```DpRVI```) [@mandal2020dual] for distinct acquisition modes. These vegetation indices have provided a better opportunity to estimate biophysical parameters with fitted models directly. The retrieval of biophysical parameters from SAR observations is of vital importance for in-season monitoring of crop growth.

# PolSAR tools Audience
***PolSAR tools*** are intended for students, researchers, and polarimetry experts to derive different SAR descriptors, utilizing the ```QGIS``` and ```python``` ecosystem of diverse tools. Especially for non-domain and application users, the plugin interface provides an easy way to process the pre-processed ***polarimetric SAR data***. 


# PolSAR tools Functionality

The functionalities of ```PolSAR tools``` are organized into three modules to handle the data from three different SAR polarization modes. The following is the list of the available functions in the ```PolSAR tools```:

* Full-pol : 
    * Radar Vegetation Index (RVI) [@Kim_2009]
    * Generalized volume Radar Vegetation Index (GRVI) [@ratha2019generalized]
    * Polarimetric Radar Vegetation Index (PRVI) [@chang2018polarimetric] 
    * Model free 3-Component decomposition for full-pol data (MF3CF) [@dey2020target]
    * Degree of Polarization (DOP) [@barakat1977degree]
* Compact-pol :
    * Model free 3-Component decomposition for compact-pol data (MF3CC) [@dey2020target]
    * Improved S-Omega decomposition for compact-pol data (iS-Omega) [@kumar2020crop]
    * Compact-pol Radar Vegetation Index (CpRVI) [@mandal2020radar]
    * Degree of Polarization (DOP) 
 * Dual-pol :
    * Radar Vegetation Index (RVI) 
    * Dual-pol Radar Vegetation Index (DpRVI) [@mandal2020dual], 
    * Polarimetric Radar Vegetation Index (PRVI) 
    * Degree of Polarization (DOP) [@barakat1977degree]

# Acknowledgements
The authors would like to thank the developers of [QGIS Plugin Builder](https://github.com/g-sherman/Qgis-Plugin-Builder). Authors acknowledge the [GEO-AWS Earth Observation Cloud Credits Program](https://www.earthobservations.org/aws.php), which supported the computation, development, and testing of ```PolSAR tools``` on AWS cloud platform through the project: ```AWS4AgriSAR-Crop inventory mapping from SAR data on cloud computing platform.```
	
# References
