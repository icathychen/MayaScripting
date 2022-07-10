import importlib
import pymel.core as pm
from maya import cmds
import os
import stairsClass
from stairsClass import Stairs
importlib.reload(stairsClass)

USERAPPDIR = cmds.internalVar(userAppDir=True)
DIRECTORY = os.path.join(USERAPPDIR, 'Stairs')

def createDirectory(directory=DIRECTORY):
    if not os.path.exists(directory):
        os.mkdir(directory)

class staircaseGeneratorUI(object):
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
        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName)

        self.buildUI()

        cmds.showWindow()

    def buildUI(self):
        column = cmds.columnLayout()
        cmds.rowLayout(numberOfColumns=2)
        self.textfield = pm.textField()
        #name = cmds.textField(self.textfield, q=True, text=True)
        cmds.button(label="Save", command=self.save)

        cmds.setParent(column)
        cmds.separator(style='double', height=6)
        cmds.text(label="Use the slider to modify the size of the stair")
        cmds.rowLayout(numberOfColumns=4)
        self.label = cmds.text(label="10")
        self.slider = cmds.intSlider(min=2, max=15, value=10, step=1, dragCommand=self.modifyStairs)
        cmds.button(label="Make stairs", command=self.makeStairs)
        cmds.button(label="Reset", command=self.reset)

        cmds.setParent(column)
        cmds.text(label="Use the slider to modify the gap of the stair")
        cmds.rowLayout(numberOfColumns=2)
        self.labelGap = cmds.text(label="0")
        self.sliderGap = cmds.intSlider(min=0, max=15, value=0, step=1, dragCommand=self.modifyGap)

        cmds.setParent(column)
        cmds.rowLayout(numberOfColumns=3)
        cmds.button(label="Screenshot", command=self.saveScreenshot)
        cmds.button(label="Close", command=self.close)
        cmds.button(label="Delete", command=self.delete)

    def modifyStairs(self, size):
        cmds.text(self.label, edit=True,label=str(size))
        if self.stairs:
            self.stairs.changeSize(size=size)

    def makeStairs(self, *args):
        # We first need to see what the slider is set to, to find how many teeth we need to make
        size = cmds.intSlider(self.slider, query=True, value=True)
        self.stairs = Stairs()
        self.stairs.currentSize = size
        self.stairs.createStairs(size=size)

    def modifyGap(self, gap):
        cmds.text(self.labelGap, edit=True,label=str(gap))
        if self.stairs:
            self.stairs.changeGap(gap=gap)


    def reset(self, *args):
        self.stairs = None
        # We will reset the slider value
        cmds.intSlider(self.slider, edit=True, value=10)
        cmds.text(self.label,edit=True,label=str(10))

    def close(self, *args):
        cmds.deleteUI(self.windowName)

    def delete(self, *args):
        if self.stairs:
            self.stairs.deleteStairs()
        else: print("You need to make a stair first.")

    def saveScreenshot(self, *args):
        self.stairs.saveScreenshot(name="Stairs")

    def saveFile(self, name, directory=DIRECTORY):
        createDirectory(directory)
        path = os.path.join(directory, "%s.ma" % name)
        cmds.file(rename=path)

        if cmds.ls(selection=True):
            cmds.file(force=True, type="mayaAscii",exportSelected=True)
        else:
            cmds.file(save=True,type="mayaAscii",force=True)

    def save(self, *args):
        createDirectory()
        name = self.textfield.getText()
        print(name)
        self.saveFile(name=name)


