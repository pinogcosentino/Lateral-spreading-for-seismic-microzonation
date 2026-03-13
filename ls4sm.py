# -*- coding: utf-8 -*-

"""
/***************************************************************************
 SeismicMicrozonation
                                 A QGIS plugin
 Lateral spreading for seismic microzonation
        begin                : 2025-02-02
        copyright            : (C) 2025 by Giuseppe Cosentino
        email                : giuseppe.cosentino@cnr.it
 ***************************************************************************/
"""

import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication
from .ls4sm_provider import SeismicMicrozonationProvider

# Cartella del plugin — modo corretto in Python 3, senza bisogno di inspect/sys
plugin_dir = os.path.dirname(__file__)


class SeismicMicrozonationPlugin:

    def __init__(self, iface):          # iface è obbligatorio
        self.iface = iface
        self.provider = None
        self.toolbar = None
        self.action = None

    def initProcessing(self):
        """Registra il provider nel Processing Framework."""
        self.provider = SeismicMicrozonationProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

        icon_path = os.path.join(plugin_dir, 'icon.png')
        icon = QIcon(icon_path)

        self.action = QAction(icon, 'Lateral Spreading - Seismic Microzonation',
                              self.iface.mainWindow())
        self.action.setToolTip('Lateral Spreading for Seismic Microzonation')
        self.action.triggered.connect(self.run)

        self.iface.addPluginToMenu('Seismic Microzonation', self.action)

        self.toolbar = self.iface.addToolBar('Seismic Microzonation')
        self.toolbar.setObjectName('SeismicMicrozonationToolbar')
        self.toolbar.addAction(self.action)

    def unload(self):
        self.iface.removePluginMenu('Seismic Microzonation', self.action)

        if self.toolbar:
            self.toolbar.deleteLater()
            self.toolbar = None

        QgsApplication.processingRegistry().removeProvider(self.provider)

    def run(self):
        """Apre il dialogo dell'algoritmo Lateral Spreading."""
        from qgis import processing
        from qgis.core import QgsApplication

        # Trova l'algoritmo dinamicamente dal provider, senza ID hardcoded
        provider = QgsApplication.processingRegistry().providerById(
            self.provider.id()
        )
        if not provider or not provider.algorithms():
            self.iface.messageBar().pushWarning(
                'Seismic Microzonation', 'Nessun algoritmo trovato nel provider.'
            )
            return

        processing.execAlgorithmDialog(provider.algorithms()[0].id())
