import importlib
import pymel.core as pm
from maya import cmds
import os
import stairsClass
from stairsClass import Stairs
from maya import OpenMayaUI as omui
from PySide2 import QtWidgets, QtGui, QtCore
importlib.reload(stairsClass)

cmds.file(force=True, newFile=True)
USERAPPDIR = cmds.internalVar(userAppDir=True)
DIRECTORY = os.path.join(USERAPPDIR, 'Stairs')

def createDirectory(directory=DIRECTORY):
    if not os.path.exists(directory):
        os.mkdir(directory)

class staircaseGeneratorUI(QtWidgets.QWidget):
    '''
    import staircaseGenerator as s
    importlib.reload(s)
    s.staircaseGeneratorUI().show()
    '''

    windowName = "Stairs Generator"

    def __init__(self):
        self.stairs = None
        self.textField = None

    def show(self):
        if cmds.window(self.windowName, query=True, exists=True, width=800, height=100):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName)

        self.buildUI()

        cmds.showWindow()

    def buildUI(self):
        column = cmds.columnLayout(columnAttach=('left',10))
        cmds.rowLayout(numberOfColumns=2)
        self.textfield = pm.textField()
        #name = cmds.textField(self.textfield, q=True, text=True)
        cmds.button(label="Save", command=self.save)

        cmds.setParent(column)
        cmds.separator(style='double', height=6)

        #  # This will be our button to display the color of the light
        # self.colourBtn = QtWidgets.QPushButton()
        # self.colourBtn.setMaximumWidth(20)
        # self.colourBtn.setMaximumHeight(20)
        # # Finally we call a method to sat the buttons color based on the lights current color
        # self.setButtonColour()
        # self.colourBtn.clicked.connect(self.setColour)

        #self.colour = cmds.colorInputWidgetGrp( label='Color', rgb=(1, 0, 0),columnAlign=[1,'left'] )
        # cmds.setParent(column)
        # self.colour = cmds.colorSliderGrp( rgb=(0, 0, 1),columnAlign=[1,'left'],dragCommand=self.setColour())

        cmds.setParent(column)
        cmds.separator(style='double', height=6)
        cmds.text(label="Modify the size of the stairs")
        cmds.rowLayout(numberOfColumns=2)
        self.labelSize = cmds.text(label="1")
        self.sliderSize = cmds.intSlider(min=1, max=10, value=1, step=1, dragCommand=self.makeStairs)
        #cmds.button(label="Add size", command=self.modifySize)
        #cmds.button(label="Reset", command=self.reset)

        cmds.setParent(column)
        cmds.separator(style='double', height=6)
        cmds.text(label="Modify the divisions of the stairs")
        cmds.rowLayout(numberOfColumns=2)
        self.labelDivision = cmds.text(label="10")
        self.sliderDivision = cmds.intSlider(min=2, max=15, value=10, step=1, dragCommand=self.makeStairs)
        #cmds.button(label="Add division", command=self.modifyDivision)
        #cmds.button(label="Reset", command=self.reset)

        cmds.setParent(column)
        cmds.separator(style='double', height=6)
        cmds.text(label="Modify the elevation of the stairs")
        cmds.rowLayout(numberOfColumns=2)
        self.labelGap = cmds.text(label="1")
        self.sliderGap = cmds.intSlider(min=1, max=15, value=1, step=1, dragCommand=self.makeStairs)
        #cmds.button(label="Add gap", command=self.modifyGap)

        cmds.setParent(column)
        cmds.separator(style='double', height=6)
        cmds.text(label="Modify the height of the stairs")
        cmds.rowLayout(numberOfColumns=2)
        self.labelHeight = cmds.text(label="1")
        self.sliderHeight = cmds.intSlider(min=1, max=10, value=1, step=1, dragCommand=self.makeStairs)
        #cmds.button(label="Add gap", command=self.modifyGap)

        cmds.setParent(column)
        cmds.separator(style='double', height=6)
        cmds.rowLayout(numberOfColumns=4, columnAlign4=('right','right','right','right'))
        cmds.button(label="standard", command=self.applyTexture_S)
        cmds.button(label="lambert", command=self.applyTexture_L)
        cmds.button(label="phong", command=self.applyTexture_P)
        cmds.button(label="blinn", command=self.applyTexture_B)

        cmds.setParent(column)
        cmds.separator(style='double', height=6)
        cmds.rowLayout(numberOfColumns=4, columnAlign4=('right','right','right','right'))
        self.createButton = cmds.button(label="Create", command=self.makeStairs)
        cmds.button(label="Screenshot", command=self.saveScreenshot)
        cmds.button(label="Delete", command=self.delete)
        cmds.button(label="Close", command=self.close)


    def makeStairs(self, *args):
        self.modifyText()
        gap = cmds.intSlider(self.sliderGap, query=True, value=True)
        size = cmds.intSlider(self.sliderSize, query=True, value=True)
        division = cmds.intSlider(self.sliderDivision, query=True, value=True)
        if self.stairs:
            self.delete()
        if not self.stairs:
            self.stairs = Stairs()
            self.stairs.currentDivision = division
            self.stairs.currentSize = size
            self.stairs.currentGap = gap
            self.modifyDimension()
            self.stairs.createStairs(size=size,division=division,gap=gap)

    def modifyDivision(self, *args):
        self.modifyText()
        division = cmds.intSlider(self.sliderDivision, query=True, value=True)
        if self.stairs:
            self.stairs.changeDivision(division=division)

    def modifyGap(self, *args):
        self.modifyText()
        gap = cmds.intSlider(self.sliderGap, query=True, value=True)

        if self.stairs:
            self.stairs.changeGap(gap=gap)

    def modifyDimension(self, *args):
        height = cmds.intSlider(self.sliderHeight, query=True, value=True)
        cmds.text(self.labelHeight, edit=True,label=str(height))

        # width = cmds.intSlider(self.sliderWidth, query=True, value=True)
        # cmds.text(self.labelWidth, edit=True,label=str(width))
        #
        # depth = cmds.intSlider(self.sliderDepth, query=True, value=True)
        # cmds.text(self.labelDepth, edit=True,label=str(depth))

        if self.stairs:
            self.stairs.changeHeight(height)
            # self.stairs.changeWidth(width)
            # self.stairs.changeDepth(depth)
            #self.refreshModel()


    def modifySize(self, *args):
        self.modifyText()
        size = cmds.intSlider(self.sliderSize, query=True, value=True)
        if self.stairs:
            self.stairs.changeSize(size=size)

    def modifyText(self, *args):
        size = cmds.intSlider(self.sliderSize, query=True, value=True)
        cmds.text(self.labelSize, edit=True,label=str(size))

        gap = cmds.intSlider(self.sliderGap, query=True, value=True)
        cmds.text(self.labelGap, edit=True,label=str(gap))

        division = cmds.intSlider(self.sliderDivision, query=True, value=True)
        cmds.text(self.labelDivision, edit=True,label=str(division))

        height = cmds.intSlider(self.sliderHeight, query=True, value=True)
        cmds.text(self.labelHeight, edit=True,label=str(height))

        # width = cmds.intSlider(self.sliderWidth, query=True, value=True)
        # cmds.text(self.labelWidth, edit=True,label=str(width))
        #
        # depth = cmds.intSlider(self.sliderDepth, query=True, value=True)
        # cmds.text(self.labelDepth, edit=True,label=str(depth))


    def reset(self, *args):
        self.stairs = None
        # We will reset the slider value
        cmds.intSlider(self.slider, edit=True, value=10)
        cmds.text(self.label,edit=True,label=str(10))

    def close(self, *args):
        cmds.deleteUI(self.windowName)

    def delete(self, *args):
        if self.stairs:
            self.stairs.deleteAll()
            self.stairs = None
        else: print("You need to make a stair first.")

    def saveScreenshot(self, *args):
        if self.stairs:
            self.stairs.saveScreenshot(name="Stairs")

    def saveFile(self, name, directory=DIRECTORY):
        createDirectory(directory)
        path = os.path.join(directory, "%s.ma" % name)
        cmds.file(rename=path)

        if cmds.ls(selection=True):
            cmds.file(force=True, type="mayaAscii",exportSelected=True)
        else:
            cmds.file(save=True,type="mayaAscii",force=True)

    def refreshModel(self):
        self.stairs.transformDimension()

    def save(self, *args):
        createDirectory()
        name = self.textfield.getText()
        print(name)
        self.saveFile(name=name)

    def setColour(self,*args):
        if self.stairs:
            self.stairs.colour = cmds.colorSliderGrp(self.colour, query=True, value=True)



    def setButtonColour(self, colour=None):
        if self.stairs:
            if not colour:
                    colour = self.stairs.colour.get()
            assert len(colour) == 3, "You must provide a list of 3 colours"

            r,g,b = [c*255 for c in colour]
            self.colourBtn.setStyleSheet('background-color: rgba(%s, %s, %s, 1.0)' % (r,g,b))

    def applyTexture_L(self, type):
        if self.stairs:
            self.stairs.applyMaterial(type='lambert')

    def applyTexture_S(self, type):
        if self.stairs:
            self.stairs.applyMaterial(type="standardSurface")

    def applyTexture_B(self, type):
        if self.stairs:
            self.stairs.applyMaterial(type="blinn")

    def applyTexture_P(self, type):
        if self.stairs:
            self.stairs.applyMaterial(type="phong")


    def create_shader(name, node_type="lambert"):
        material = cmds.shadingNode(node_type, name=name, asShader=True)
        sg = cmds.sets(name="%sSG" % name, empty=True, renderable=True, noSurfaceShader=True)
        cmds.connectAttr("%s.outColor" % material, "%s.surfaceShader" % sg)
        return material, sg

def getDock(name='LightingManagerDock'):
    """
    This function creates a dock with the given name.
    It's an example of how we can mix Maya's UI elements with Qt elements
    Args:
        name: The name of the dock to create
    Returns:
        QtWidget.QWidget: The dock's widget
    """
    # First lets delete any conflicting docks
    deleteDock(name)

    # Then we create a workspaceControl dock using Maya's UI tools
    # This gives us back the name of the dock created
    ctrl = pm.workspaceControl(name, dockToMainWindow=('right', 1), label="Stairs Generator")

     # We can use the OpenMayaUI API to get the actual Qt widget associated with the name
    qtCtrl = omui.MQtUtil_findControl(ctrl)

     # Finally we use wrapInstance to convert it to something Python can understand, in this case a QWidget
    ptr = wrapInstance(Qt.long(qtCtrl), QtWidgets.QWidget)

    # And we return that QWidget back to whoever wants it.
    return ptr

def deleteDock(name="Stairs Generator"):
    """
    A simple function to delete the given dock
    Args:
        name: the name of the dock
    """
    # We use the workspaceControl to see if the dock exists
    if pm.workspaceControl(name, query=True, exists=True):
         # If it does we delete it
        pm.deleteUI(name)
