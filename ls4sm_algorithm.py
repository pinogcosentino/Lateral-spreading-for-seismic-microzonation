# -*- coding: utf-8 -*-

"""
/***************************************************************************
 SeismicMicrozonation
                                 A QGIS plugin
 Lateral spreading for seismic microzonation
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2025-01-08
        copyright            : (C) 2025 by Giuseppe Cosentino
        email                : giuseppe.cosentino@cnr.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Giuseppe Cosentino'
__date__ = '2025-01-08'
__copyright__ = '(C) 2025 by Giuseppe Cosentino'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing


class SeismicMicrozonationAlgorithm(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('polygon_layer', 'Polygon Layer', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterField('liquefaction_index_il', 'Liquefaction Index (IL)', type=QgsProcessingParameterField.Numeric, parentLayerParameterName='polygon_layer', allowMultiple=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('digital_terrain_model', 'Digital Terrain Model', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Slope', 'Slope %', createByDefault=True, defaultValue=''))
        self.addParameter(QgsProcessingParameterFeatureSink('RespectZonesZrLsSlope15AndIl0', 'Respect Zones (ZR LS) Slope% > 15 and IL> 0', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('RespectZonesZrLs2Slope5AndIl15', 'Respect Zones (ZR LS) 2 < Slope% ≤ 5 and IL >15', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('SusceptibilityZonesZsLs2Slope5And2Il15', 'Susceptibility Zones (ZS  LS) 2 < Slope% ≤ 5 and 2< IL ≤ 15', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('LowSusceptibilityZones', 'Low Susceptibility Zones', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('SusceptibilityLateralSpreadingZonesZsLs5Slope15And0Il2', 'Susceptibility Lateral Spreading Zones - ZS  LS (5 < Slope% ≤ 15 and 0 < IL ≤ 2)', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('RespectZonesZrLs2Slope15And2Il5', 'Respect  Zones (ZR LS) 2 < Slope% ≤ 15 and 2 < IL≤ 5', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('RespectZones', 'Respect Zones', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('SusceptibilityZones', 'Susceptibility Zones', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('LiquefactionIndexPonit', 'Liquefaction index ponit', type=QgsProcessing.TypeVectorPoint, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(23, model_feedback)
        results = {}
        outputs = {}

        # Punto sulla superficie
        alg_params = {
            'ALL_PARTS': True,
            'INPUT': parameters['polygon_layer'],
            'OUTPUT': parameters['LiquefactionIndexPonit']
        }
        outputs['PuntoSullaSuperficie'] = processing.run('native:pointonsurface', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['LiquefactionIndexPonit'] = outputs['PuntoSullaSuperficie']['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Pendenza
        alg_params = {
            'AS_PERCENT': True,
            'BAND': 1,
            'COMPUTE_EDGES': False,
            'EXTRA': '',
            'INPUT': parameters['digital_terrain_model'],
            'OPTIONS': '',
            'SCALE': 1,
            'ZEVENBERGEN': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Pendenza'] = processing.run('gdal:slope', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Ritaglia raster con maschera
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,  # Usa Il Tipo Dati del Layer in Ingresso
            'EXTRA': '',
            'INPUT': outputs['Pendenza']['OUTPUT'],
            'KEEP_RESOLUTION': True,
            'MASK': parameters['polygon_layer'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': QgsCoordinateReferenceSystem('EPSG:32633'),
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:32633'),
            'TARGET_EXTENT': None,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': parameters['Slope']
        }
        outputs['RitagliaRasterConMaschera'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Slope'] = outputs['RitagliaRasterConMaschera']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Calcolatore raster
        # slope%>15
        alg_params = {
            'CELL_SIZE': None,
            'CRS': QgsCoordinateReferenceSystem('EPSG:32633'),
            'EXPRESSION': '"A@1">15',
            'EXTENT': None,
            'LAYERS': outputs['RitagliaRasterConMaschera']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcolatoreRaster'] = processing.run('native:modelerrastercalc', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Calcolatore raster
        # 5 < Slope% <= 15
        alg_params = {
            'CELL_SIZE': None,
            'CRS': QgsCoordinateReferenceSystem('EPSG:32633'),
            'EXPRESSION': '"A@1" > 5 AND "A@1" <= 15',
            'EXTENT': None,
            'LAYERS': outputs['RitagliaRasterConMaschera']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcolatoreRaster'] = processing.run('native:modelerrastercalc', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Calcolatore raster
        # 2 < slope% <= 5 
        alg_params = {
            'CELL_SIZE': None,
            'CRS': QgsCoordinateReferenceSystem('EPSG:32633'),
            'EXPRESSION': '"A@1" > 2 \nAND\n"A@1"<= 5 ',
            'EXTENT': None,
            'LAYERS': outputs['RitagliaRasterConMaschera']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcolatoreRaster'] = processing.run('native:modelerrastercalc', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Poligonizzazione (da raster a vettore)
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['CalcolatoreRaster']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoligonizzazioneDaRasterAVettore'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Poligonizzazione (da raster a vettore)
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['CalcolatoreRaster']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoligonizzazioneDaRasterAVettore'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Poligonizzazione (da raster a vettore)
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['CalcolatoreRaster']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoligonizzazioneDaRasterAVettore'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Estrai per attributo
        # Estrazione dei soli oggetti del layer che avevano il requisito (1) , valore originario del pixel (DN=1)
        alg_params = {
            'FIELD': 'DN',
            'INPUT': outputs['PoligonizzazioneDaRasterAVettore']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': '1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['EstraiPerAttributo'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Estrai per attributo
        # Estrazione dei soli oggetti del layer che avevano il requisito (1) , valore originario del pixel (DN=1)
        alg_params = {
            'FIELD': 'DN',
            'INPUT': outputs['PoligonizzazioneDaRasterAVettore']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': '1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['EstraiPerAttributo'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Estrai per attributo
        # Estrazione dei soli oggetti del layer che avevano il requisito (1) , valore originario del pixel (DN=1)
        alg_params = {
            'FIELD': 'DN',
            'INPUT': outputs['PoligonizzazioneDaRasterAVettore']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': '1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['EstraiPerAttributo'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Intersezione
        # Intersezione Slope (vettoriale)  con il layer "Instab"
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': parameters['polygon_layer'],
            'INPUT_FIELDS': [''],
            'OVERLAY': outputs['EstraiPerAttributo']['OUTPUT'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersezione'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Estrai tramite espressione
        alg_params = {
            'EXPRESSION': '"IL" >0 AND "IL"<=2',
            'INPUT': outputs['Intersezione']['OUTPUT'],
            'OUTPUT': parameters['SusceptibilityLateralSpreadingZonesZsLs5Slope15And0Il2']
        }
        outputs['EstraiTramiteEspressione'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['SusceptibilityLateralSpreadingZonesZsLs5Slope15And0Il2'] = outputs['EstraiTramiteEspressione']['OUTPUT']

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Intersezione
        # Intersezione Slope (vettoriale)  con il layer "Instab"
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': parameters['polygon_layer'],
            'INPUT_FIELDS': [''],
            'OVERLAY': outputs['EstraiPerAttributo']['OUTPUT'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersezione'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Intersezione
        # Intersezione Slope (vettoriale)  con il layer "Instab"
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': parameters['polygon_layer'],
            'INPUT_FIELDS': [''],
            'OVERLAY': outputs['EstraiPerAttributo']['OUTPUT'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersezione'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Estrai tramite espressione
        # Estrazione degli oggetti con 2 < Slope% ≤ 5; IL >15
        alg_params = {
            'EXPRESSION': '"IL" > 15',
            'INPUT': outputs['Intersezione']['OUTPUT'],
            'OUTPUT': parameters['RespectZonesZrLs2Slope5AndIl15']
        }
        outputs['EstraiTramiteEspressione'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RespectZonesZrLs2Slope5AndIl15'] = outputs['EstraiTramiteEspressione']['OUTPUT']

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Estrai tramite espressione
        alg_params = {
            'EXPRESSION': '"IL" > 0',
            'INPUT': outputs['Intersezione']['OUTPUT'],
            'OUTPUT': parameters['RespectZonesZrLsSlope15AndIl0']
        }
        outputs['EstraiTramiteEspressione'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RespectZonesZrLsSlope15AndIl0'] = outputs['EstraiTramiteEspressione']['OUTPUT']

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Estrai tramite espressione
        alg_params = {
            'EXPRESSION': '"IL" > 2 AND "IL" <= 15',
            'INPUT': outputs['Intersezione']['OUTPUT'],
            'OUTPUT': parameters['SusceptibilityZonesZsLs2Slope5And2Il15']
        }
        outputs['EstraiTramiteEspressione'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['SusceptibilityZonesZsLs2Slope5And2Il15'] = outputs['EstraiTramiteEspressione']['OUTPUT']

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Estrai tramite espressione
        alg_params = {
            'EXPRESSION': '"IL" > 0 AND "IL" <= 2',
            'INPUT': outputs['Intersezione']['OUTPUT'],
            'OUTPUT': parameters['LowSusceptibilityZones']
        }
        outputs['EstraiTramiteEspressione'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['LowSusceptibilityZones'] = outputs['EstraiTramiteEspressione']['OUTPUT']

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Estrai tramite espressione
        alg_params = {
            'EXPRESSION': '"IL" >2 AND "IL"<=15',
            'INPUT': outputs['Intersezione']['OUTPUT'],
            'OUTPUT': parameters['RespectZonesZrLs2Slope15And2Il5']
        }
        outputs['EstraiTramiteEspressione'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RespectZonesZrLs2Slope15And2Il5'] = outputs['EstraiTramiteEspressione']['OUTPUT']

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Fondi vettori
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:32633'),
            'LAYERS': [outputs['EstraiTramiteEspressione']['OUTPUT'],outputs['EstraiTramiteEspressione']['OUTPUT'],outputs['EstraiTramiteEspressione']['OUTPUT']],
            'OUTPUT': parameters['RespectZones']
        }
        outputs['FondiVettori'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RespectZones'] = outputs['FondiVettori']['OUTPUT']

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Fondi vettori
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:32633'),
            'LAYERS': [outputs['EstraiTramiteEspressione']['OUTPUT'],outputs['EstraiTramiteEspressione']['OUTPUT']],
            'OUTPUT': parameters['SusceptibilityZones']
        }
        outputs['FondiVettori'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['SusceptibilityZones'] = outputs['FondiVettori']['OUTPUT']
        return results

    def name(self):
        return 'Lateral spreading for seismic microzonation'

    def displayName(self):
        return 'Lateral spreading for seismic microzonation'

    def group(self):
        return 'Seismic Microzonation'

    def groupId(self):
        return 'Seismic Microzonation'

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:9.5pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-weight:600; color:#0000ab; background-color:transparent;">Lateral spreading</span><span style=" font-size:12pt; background-color:transparent;"> </span><span style=" background-color:transparent;">is a term used in geotechnical and earthquake engineering. It refers to the horizontal movement of soil or rock, often occurring during an earthquake. This phenomenon typically happens in areas with loose, saturated soils, and it can cause significant ground deformation, impacting structures, pipelines, and other infrastructure.</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" background-color:transparent;">Lateral spreading usually occurs when:</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" background-color:transparent;">- There is a liquefaction of loose, water-saturated soils.</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" background-color:transparent;">- The ground surface slopes gently.</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" background-color:transparent;">- There are nearby free faces, like riverbanks or sea cliffs, providing an unconfined direction for the soil to move.</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" background-color:transparent;">This type of ground failure is especially dangerous because it can lead to the collapse of buildings, bridges, and other critical infrastructure.</span></p></body></html></p>
<h2>Parametri in ingresso
</h2>
<h3>Polygon Layer</h3>
<p>Layer</p>
<h3>Liquefaction Index (IL)</h3>
<p>IL</p>
<h3>Digital Terrain Model</h3>
<p>DTM</p>
<h2>Risultati</h2>
<h3>Slope %</h3>
<p>Slope %</p>
<h3>Low Susceptibility Zones</h3>
<p>Z0LS</p>
<h3>Respect Zones</h3>
<p>ZRLS </p>
<h3>Susceptibility Zones</h3>
<p>ZSLS </p>
<h2>Esempi</h2>
<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:9.5pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; color:#0000d8;">The plugin identifies Zones subject to lateral spreading:</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">- Low Susceptibility Zones (Z0): 2 &lt; Slope% ≤ 5 and 0 &lt; IL ≤ 2;</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">- Susceptibility Zones (ZS): 2 &lt; Slope% ≤ 5 and 2&lt; IL ≤ 15;</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">- Susceptibility Zones (ZS): 5 &lt; Slope% ≤ 15 and 0 &lt; IL ≤ 2;</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">- Respect Zones (ZR): 2 &lt; Slope% ≤ 5 and IL &gt;15;</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">- Respect Zones (ZR): 2 &lt; Slope% ≤ 15 and 2 &lt; IL≤ 5;</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">- Respect Zone(ZR): Slope (%) &gt; 15% and IL &gt; 0.</p></body></html></p><br><p align="right">Autore algoritmo: Giuseppe Cosentino e Francesco Pennica</p><p align="right">Versione algoritmo: Version 1.0. 20241202</p></body></html>"""

    def createInstance(self):
        return SeismicMicrozonationAlgorithm()
