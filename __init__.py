# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 A QGIS plugin
This plugin generates derived SAR parameters from input polarimetric matrix (C3, T3, C2, T2).
                              -------------------
        begin                : 2020-02-03
        git sha              : $Format:%H$
        copyright            : (C) 2025 by PolSAR tools team
        email                : bnarayanarao@nitw.ac.in
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PolSAR class from file SAR_Tools.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .SAR_Tools import PolSAR
    return PolSAR(iface)
