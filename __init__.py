# -*- coding: utf-8 -*-
"""
/***************************************************************************
 cow
                                 A QGIS plugin
 collar localizador
                             -------------------
        begin                : 2015-11-30
        copyright            : (C) 2015 by yo
        email                : yo
        git sha              : $Format:%H$
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
    """Load cow class from file cow.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .cow import cow
    return cow(iface)
