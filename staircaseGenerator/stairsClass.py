from maya import cmds
import pymel.core as pm
import os
import maya.OpenMaya as OpenMaya
from PySide2 import QtWidgets, QtGui, QtCore

USERAPPDIR = cmds.internalVar(userAppDir=True)
DIRECTORY = os.path.join(USERAPPDIR, 'Stairs')

def createDirectory(directory=DIRECTORY):
    if not os.path.exists(directory):
        os.mkdir(directory)

class Stairs(QtWidgets.QWidget):

    face = []
    created = False
    cubeCreated = False
    currentDivision = 10
    currentSize = 1
    currentGap = 1
    height = 0.3
    width = 1
    depth = 1

    def __init__(self):
        #The _init_ method lets us set default values
        createDirectory()
        self.constructor = None
        self.shape = None
        self.extrude = None
        self.transform = None
        self.face = None
        self.cubeCreated = False
        self.currentDivision = 10
        self.currentSize = 1
        self.currentGap = 1
        self.height = 0.3
        self.width = 1
        self.depth = 1
        self.colour = None

    def createStairs(self, size=currentSize, division=currentDivision, gap=currentGap):
        step = division - 1
        counter = 0
        amount = 1
        extrudeAmount = 0
        complete = False
        self.created = True
        i = 0
        direction = 0
        count = 0
        face = []

        #Create plane
        transform, constructor = cmds.polyPlane(subdivisionsHeight=division, subdivisionsWidth=division)
        cmds.setAttr('%s.sx' % transform, size);
        cmds.setAttr('%s.sz' % transform, size);
        self.transform = transform
        self.currentSize = size
        self.currentDivision = division
        self.currentGap = gap

        while(not complete):
            cmds.select(clear=True)
            if counter <= step:
                if direction == 0:
                    amount = 1
                elif direction == 1:
                    amount = division
                elif direction == 2:
                    amount = -1
                elif direction == 3:
                    amount = -division
                counter += 1
                cmds.select('%s.f[%s]' % (transform, i))
                i += amount
                face.append(i-1)
                #print("select: %s" % (i-1))
                extrudeAmount += 1
                #print("extrude: %s" % (extrudeAmount-1))
            else:
                if step == -1:
                    cmds.select('%s.f[%s]' % (transform, 7))
                    break
                counter = 0
                if direction == 3:
                    direction = 0
                else:
                    direction += 1
                if step == division - 1:
                    step -= 1
                elif count == 0:
                    count += 1
                elif count == 1:
                    count = 0
                    step -= 1
                continue

        self.outsideToInside(face, transform, division, gap)
        #self.insideToOutside(face, transform, division, gap)
        cmds.delete(transform, constructor)
        self.face = face
        return face

    def findCenterCoordinate(self,transform, index):
        face = pm.MeshFace("%s.f[%s]" % (transform, index))
        pt = face.__apimfn__().center(OpenMaya.MSpace.kWorld)
        centerPoint = pm.datatypes.Point(pt)
        return centerPoint

    def createCube(self, index, centerPoint, division=currentDivision, amount=0):
        if self.cubeCreated:
            cmds.polyCube(n="cube%s" % index, height=self.currentSize * 0.2 * self.height * (self.currentSize / self.currentDivision), width= self.currentSize * self.width * (self.currentSize / self.currentDivision),
                                             depth=self.currentSize * self.depth * (self.currentSize / self.currentDivision), edit=True)
        else:
            cmds.polyCube(n="cube%s" % index, height=self.currentSize * 0.2 * self.height * (self.currentSize / self.currentDivision), width= self.currentSize * self.width * (self.currentSize / self.currentDivision),
                                             depth=self.currentSize * self.depth * (self.currentSize / self.currentDivision))
        #cmds.setAttr('%s.sx' % ("cube%s" % index), self.currentSize)
        #cmds.setAttr('%s.sz' % ("cube%s" % index), self.currentSize)
        cmds.setAttr('%s.translateX' % ("cube%s" % index), self.currentSize * centerPoint[0])
        cmds.setAttr('%s.translateZ' % ("cube%s" % index), self.currentSize * centerPoint[2])
        cmds.setAttr("cube%s.visibility" % index, 0)
        #cmds.hide("cube%s" % index)

    def changeDivision(self, division):
        if self.created:
            self.deleteAll()
        self.currentDivision = division
        self.createStairs(division=division)

    def changeSize(self, size):
        if self.created:
            self.deleteAll()
        self.currentSize = size
        self.createStairs(size=size)

    def changeGap(self, gap):
        if self.created:
            self.deleteAll()
        self.currentGap = gap
        self.createStairs(gap=gap)

    def changeHeight(self, height):
        self.height = height

    def changeWidth(self, width):
        self.width = width

    def changeDepth(self, depth):
        self.depth = depth

    def transformCube(self, index, amount, centerPoint, gap):
        if amount == 0:
            amount = 0.5
        #cmds.setAttr('%s.sy' % ("cube%s" % index), amount*5)
        cmds.setAttr('%s.translateY' % ("cube%s" % index), ( 0.01 * self.height * self.currentSize * gap * self.currentSize * amount))

    def transformDimension(self):
        #Transform Cubes
        self.deleteStairs()
        self.outsideToInside(self.face, self.transform, self.currentDivision, self.currentGap)



    def outsideToInside(self, face, transform, division, gap):
        count = 1
        counter = 1
        frame = 1

        #Create cubes
        for i in face:
            centerPoint = self.findCenterCoordinate(transform, i)
            self.createCube(i, centerPoint)
            cmds.setKeyframe('%s.translateY' % ("cube%s" % i), t=1)
            cmds.setKeyframe('%s.sy' % ("cube%s" % i), t=1)
            cmds.setKeyframe("cube%s.visibility" % i, t=1)


        #Transform Cubes
        for i in range(len(face)):
            centerPoint = self.findCenterCoordinate(transform, face[i])
            self.transformCube(face[i], i, centerPoint, gap)
            cmds.setAttr("cube%s.visibility" % face[i], 1)
            cmds.setKeyframe('%s.translateY' % ("cube%s" % face[i]), t=frame)
            cmds.setKeyframe('%s.sy' % ("cube%s" % face[i]), t=frame)
            cmds.setKeyframe("cube%s.visibility" % face[i], t=frame)
            if i < division*division-1:
                cmds.setKeyframe('%s.translateY' % ("cube%s" % face[i+1]), t=frame)
                cmds.setKeyframe('%s.sy' % ("cube%s" % face[i+1]), t=frame)
                cmds.setKeyframe("cube%s.visibility" % face[i+1], t=frame)
            frame += 1
            # if count == size or count == 0:
            #     counter = -1*counter
            count += counter
        self.cubeCreated = True

    def insideToOutside(self, face, transform, division, gap):
        count = 1
        counter = 1
        frame = 1

        #Create cubes
        for i in face:
            centerPoint = self.findCenterCoordinate(transform, i)
            self.createCube(i, count, centerPoint)
            cmds.setKeyframe('%s.translateY' % ("cube%s" % i), t=1)
            #cmds.setKeyframe('%s.sy' % ("cube%s" % i), t=1)
            cmds.autoKeyframe(edit=True)

        #Transform Cubes
        for i in range(len(face)-1, -1, -1):
            centerPoint = self.findCenterCoordinate(transform, face[i])
            self.transformCube(face[i], i, centerPoint, gap)
            cmds.setKeyframe('%s.translateY' % ("cube%s" % face[i]), t=frame)
            #cmds.setKeyframe('%s.sy' % ("cube%s" % face[i]), t=frame)
            if i < division*division-1:
                cmds.setKeyframe('%s.translateY' % ("cube%s" % face[i-1]), t=frame)
                #cmds.setKeyframe('%s.sy' % ("cube%s" % face[i-1]), t=frame)
            frame += 1
            # if count == size or count == 0:
            #     counter = -1*counter
            count += counter

    def deleteStairs(self):
        for i in range(self.currentDivision * self.currentDivision):
            cmds.delete('cube%s' % i)
        self.cubeCreated = False

    def deleteAll(self):
        for i in range(self.currentDivision * self.currentDivision):
            cmds.delete('cube%s' % i)
        self.face = []
        self.created = False
        self.cubeCreated = False


    def saveScreenshot(self, name, directory=DIRECTORY):
        frame = cmds.currentTime(q=True)
        path = os.path.join(directory, '%s[%s].jpg' % (name, frame))
        for i in range(self.currentDivision * self.currentDivision):
            cmds.select('cube%s' % i, add=True)

        cmds.viewFit()

        cmds.select(clear=True, visible=False)

        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)

        cmds.playblast(completeFilename=path,forceOverwrite=True, format="image", viewer=True, width=480, height=480,
                       showOrnaments=False, startTime=frame,endTime=frame)

        return path

    def setShader(self):
        cmds.shadingNode("phong", asShader=True, name="treeTexture")
        cmds.connectAttr('filePathImage.outColor', 'treeTexture.color')
        imagePath = 'D:/fly.jpg'
        cmds.setAttr('filePathImage.fileTextureName', imagePath, type="string")

    def setColour(self):
        self.colour = (0,0,0)

    def apply_texture(self):
        object = cmds.ls(sl=True)
        cmds.optionMenu('optionMenu')
        selectedMenuItem = cmds.optionMenu('optionMenu', q=True, value=True)
        cmds.sets(name='imageMaterialGroup', renderable=True, empty=True)
        shaderNode = cmds.shadingNode('phong', name='shaderNode', asShader=True)
        fileNode = cmds.shadingNode('file', name='fileTexture', asTexture=True)
        cmds.setAttr('fileTexture'+'.fileTextureName', self.myDir[0]+'/'+selectedMenuItem, type="string")
        shadingGroup = cmds.sets(name='textureMaterialGroup', renderable=True, empty=True)
        cmds.connectAttr('shaderNode'+'.outColor','textureMaterialGroup'+'.surfaceShader')
        cmds.connectAttr('fileTexture'+'.outColor','shaderNode'+'.color')
        cmds.surfaceShaderList('shaderNode', add='imageMaterialGroup')
        cmds.sets(object, e=True, forceElement='imageMaterialGroup')

    def applyMaterial(self, type):
        for i in range(self.currentDivision * self.currentDivision):
            node = 'cube%s' % i
            shd = cmds.shadingNode('%s' % type, name="%s_%s" % (node,type) , asShader=True)
            shdSG = cmds.sets(name='%sSG' % shd, empty=True, renderable=True, noSurfaceShader=True)
            cmds.connectAttr('%s.outColor' % shd, '%s.surfaceShader' % shdSG)
            cmds.sets(node, e=True, forceElement=shdSG)



