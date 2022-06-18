import Qt
import os
import json
import time
from PySide2 import QtWidgets, QtGui, QtCore
import pymel.core as pm
from functools import partial
from past.types import basestring
from shiboken2 import wrapInstance
import logging
from maya import OpenMayaUI as omui



logging.basicConfig()
logger = logging.getLogger('LightingManager')
logger.setLevel(logging.DEBUG)
logger.debug('Using PySide2 with shiboken2')

def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(Qt.long(win), QtWidgets.QMainWindow) #Convert the memory address into integer
    return ptr

def getDock(name='LightingManagerDock'):
    deleteDock(name)
    ctrl = pm.workspaceControl(name, dockToMainWindow=('right', 1), label="Lighting Manager")
    qtCtrl = omui.MQtUtil_findControl(ctrl)
    ptr = wrapInstance(Qt.long(qtCtrl), QtWidgets.QWidget)
    return ptr

def deleteDock(name='LightingManagerDock'):
    if pm.workspaceControl(name, query=True, exists=True):
        pm.deleteUI(name)



class LightManager(QtWidgets.QWidget):

    lightTypes = {
        "Point Light": pm.pointLight,
        "Spot Light": pm.spotLight,
        "Directional Light": pm.directionalLight,
        "Area Light": partial(pm.shadingNode, 'areaLight', asLight=True),
        "Volume Light": partial(pm.shadingNode, 'volumeLight', asLight=True)
    }

    def __init__(self, dock=True):
        if dock:
            parent = getDock()
        else:
            deleteDock()

            try:
                pm.deleteUI('lightingManager')
            except:
                logger.debug("No previous UI exists")

            parent = QtWidgets.QDialog(parent=getMayaMainWindow())
            parent.setObjectName('lightManager')
            parent.setWindowTitle('Lighting Manager')
            layout = QtWidgets.QVBoxLayout(parent)

        super(LightManager, self).__init__(parent=parent)

        self.buildUI()
        self.populate()

        self.parent().layout().addWidget(self)
        if not dock:
            parent.show()

    def populate(self):
        while self.scrollLayout.count():
            widget = self.scrollLayout.takeAt(0).widget()
            if widget:
                widget.setVisible(False)
                widget.deleteLater()
        for light in pm.ls(type=["areaLight", "spotLight", "pointLight", "directionalLight", "volumeLight"]):
            self.addLight(light)

    def buildUI(self):
        layout = QtWidgets.QGridLayout(self)

        self.lightTypeCB = QtWidgets.QComboBox()
        for lightType in sorted(self.lightTypes):
            self.lightTypeCB.addItem(lightType)
        layout.addWidget(self.lightTypeCB, 0, 0, 1, 2)

        createBtn = QtWidgets.QPushButton('Create')
        createBtn.clicked.connect(self.createLight)
        layout.addWidget(createBtn, 0, 2)

        scrollWidget = QtWidgets.QWidget()
        scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(scrollWidget)
        layout.addWidget(scrollArea, 1, 0, 1, 3)

        refreshBtn = QtWidgets.QPushButton('Refresh')
        refreshBtn.clicked.connect(self.populate())
        layout.addWidget(refreshBtn, 2, 1)

        saveBtn = QtWidgets.QPushButton('Save')
        saveBtn.clicked.connect(self.saveLights)
        layout.addWidget(saveBtn, 2, 0)

        importBtn = QtWidgets.QPushButton('Import')
        importBtn.clicked.connect(self.importLights)
        layout.addWidget(importBtn, 2, 2)

    def saveLights(self):
        properties = { }

        for lightWidget in self.findChildren(LightWidget):
            light = lightWidget.light
            transform = light.getTransform()

            properties[str(transform)] = {
                'translate': list(transform.translate.get()),
                'rotation': list(transform.rotate.get()),
                'lightType':pm.objectType(light),
                'intensity': light.intensity.get(),
                'colour': light.color.get()
            }

        directory = self.getDirectory()
        lightFile = os.path.join(directory, 'lightFile_%s.json' % time.strftime('%m%d'))

        with open(lightFile, 'w') as f:
            json.dump(properties, f, indent=4)
            logger.info('Saving file to %s' % lightFile)

    def getDirectory(self):
        directory = os.path.join(pm.internalVar(userAppDir=True), 'lightManager')
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory

    def importLights(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Light Browser", directory)
        with open(fileName[0], 'r') as f:
            properties = json.load(f)

        for light, info in properties.items():
            lightType = info.get('lightType')
            for lt in self.lightTypes:
                if '%sLight' % lt.split()[0].lower() == lightType:
                    break
            else:
                logger.info('Cannot find a corresponding light type for %s (%s)' % (light, lightType))
                continue
            light = self.createLight(lightType=lt)
            light.intensity.set(info.get('intensity'))

            light.color.set(info.get('colour'))

            transform = light.getTransform()
            transform.translate.set(info.get('translate'))
            transform.rotate.set(info.get('rotation'))


    def createLight(self, lightType=None, add=True):
        if not lightType:
            lightType = self.lightTypeCB.currentText()
        func = self.lightTypes[lightType]

        light = func()
        if add:
            self.addLight(light)
        return light

    def addLight(self, light):
        widget = LightWidget(light)
        self.scrollLayout.addWidget(widget)
        widget.onSolo.connect(self.onSolo)

    def onSolo(self, value):
        lightWidgets = self.findChildren(LightWidget)
        for widget in lightWidgets:
            if widget != self.sender():
                widget.disableLight(value)


class LightWidget(QtWidgets.QWidget):

    onSolo = QtCore.Signal(bool)

    def __init__(self, light):
        super(LightWidget, self).__init__()
        if isinstance(light, basestring):
            light = pm.PyNode(light)
        if isinstance(light, pm.nodetypes.Transform):
            light = light.getShape()

        self.light = light
        self.buildUI()

    def buildUI(self):
        layout = QtWidgets.QGridLayout(self)
        self.name = QtWidgets.QCheckBox(str(self.light.getTransform()))
        self.name.setChecked(self.light.visibility.get())
        self.name.toggled.connect(lambda val: self.light.getTransform().visibility.set(val))
        layout.addWidget(self.name, 0, 0)

        soloBtn = QtWidgets.QPushButton('Solo')
        soloBtn.setCheckable(True)
        soloBtn.toggled.connect(lambda val: self.onSolo.emit(val))
        layout.addWidget(soloBtn, 0, 1)

        deleteBtn = QtWidgets.QPushButton('X')
        deleteBtn.clicked.connect(self.deleteLight)
        deleteBtn.setMaximumWidth(10)
        layout.addWidget(deleteBtn, 0, 2)

        intensity = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        intensity.setMinimum(1)
        intensity.setMaximum(1000)
        intensity.setValue(self.light.intensity.get())
        intensity.valueChanged.connect(lambda val: self.light.intensity.set(val))
        layout.addWidget(intensity, 1, 0, 1, 2)

        self.colourBtn = QtWidgets.QPushButton()
        self.colourBtn.setMaximumWidth(20)
        self.colourBtn.setMaximumHeight(20)
        self.setButtonColour()
        self.colourBtn.clicked.connect(self.setColour)
        layout.addWidget(self.colourBtn, 1, 2)


    def setButtonColour(self, colour=None):
        if not colour:
            colour = self.light.color.get()
        assert len(colour) == 3, "You must provide a list of 3 colours"

        r,g,b = [c*255 for c in colour]
        self.colourBtn.setStyleSheet('background-color: rgba(%s, %s, %s, 1.0)' % (r,g,b))

    def setColour(self):
        lightColour = self.light.color.get()
        colour = pm.colorEditor(rgbValue=lightColour)

        r,g,b,a = [float(c) for c in colour.split()]
        colour = (r,g,b)
        self.light.color.set(colour)
        self.setButtonColour(colour)

    def disableLight(self, value):
        self.name.setChecked(not value)

    def deleteLight(self):
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()

        pm.delete(self.light.getTransform())


