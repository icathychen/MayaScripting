from maya import cmds
import pymel.core as pm
import os
import maya.OpenMaya as OpenMaya

USERAPPDIR = cmds.internalVar(userAppDir=True)
DIRECTORY = os.path.join(USERAPPDIR, 'Stairs')

def createDirectory(directory=DIRECTORY):
    if not os.path.exists(directory):
        os.mkdir(directory)

class Stairs(object):

    face = []
    currentSize = 0

    def __init__(self):
        #The _init_ method lets us set default values
        createDirectory()
        self.constructor = None
        self.shape = None
        self.extrude = None
        self.transform = None

    def createStairs(self,size=10, gap=1):
        step = size - 1
        counter = 0
        amount = 1
        extrudeAmount = 0
        complete = False
        i = 0
        direction = 0
        count = 0
        face = []

        #Create plane
        transform, constructor = cmds.polyPlane(subdivisionsHeight=size, subdivisionsWidth=size)
        self.transform = transform
        while(not complete):
            cmds.select(clear=True)
            if counter <= step:
                if direction == 0:
                    amount = 1
                elif direction == 1:
                    amount = size
                elif direction == 2:
                    amount = -1
                elif direction == 3:
                    amount = -size
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
                if step == size - 1:
                    step -= 1
                elif count == 0:
                    count += 1
                elif count == 1:
                    count = 0
                    step -= 1
                continue

        self.outsideToInside(face, transform, size, gap)
        cmds.delete(transform, constructor)
        return face

    def findCenterCoordinate(self,transform, index):
        face = pm.MeshFace("%s.f[%s]" % (transform, index))
        pt = face.__apimfn__().center(OpenMaya.MSpace.kWorld)
        centerPoint = pm.datatypes.Point(pt)
        return centerPoint

    def createCube(self, index, amount, centerPoint, size):
        cmds.polyCube(n="cube%s" % index, height=0.01*1/size, width=1/size,
                                             depth=1/size)
        cmds.setAttr('%s.translateX' % ("cube%s" % index), centerPoint[0])
        cmds.setAttr('%s.translateZ' % ("cube%s" % index), centerPoint[2])

    def changeSize(self, size):
        for i in range(self.currentSize * self.currentSize):
            cmds.delete('cube%s'% i)
        self.createStairs(size=size)
        self.currentSize = size

    def changeGap(self, gap):
        for i in range(self.currentSize * self.currentSize):
            cmds.delete('cube%s'% i)
        self.createStairs(size=self.currentSize, gap=gap)


    def transformCube(self, index, amount, centerPoint, gap):
        if amount == 0:
            amount = 0.5
        cmds.setAttr('%s.sy' % ("cube%s" % index), amount*5)
        cmds.setAttr('%s.translateY' % ("cube%s" % index), (gap * (amount*0.005/2)))

    def outsideToInside(self, face, transform, size, gap):
        count = 1
        counter = 1
        frame = 1

        #Create cubes
        for i in face:
            centerPoint = self.findCenterCoordinate(transform, i)
            self.createCube(i, count, centerPoint, size)
            cmds.setKeyframe('%s.translateY' % ("cube%s" % i), t=1)
            cmds.setKeyframe('%s.sy' % ("cube%s" % i), t=1)
            cmds.autoKeyframe(edit=True)

        #Transform Cubes
        for i in range(len(face)):
            centerPoint = self.findCenterCoordinate(transform, face[i])
            self.transformCube(face[i], i, centerPoint, gap)
            cmds.setKeyframe('%s.translateY' % ("cube%s" % face[i]), t=frame)
            cmds.setKeyframe('%s.sy' % ("cube%s" % face[i]), t=frame)
            if i < size*size-1:
                cmds.setKeyframe('%s.translateY' % ("cube%s" % face[i+1]), t=frame)
                cmds.setKeyframe('%s.sy' % ("cube%s" % face[i+1]), t=frame)
            frame += 1
            # if count == size or count == 0:
            #     counter = -1*counter
            count += counter

    def deleteStairs(self):
        for i in range(self.currentSize*self.currentSize):
            cmds.delete('cube%s' % i)

    def saveScreenshot(self, name, directory=DIRECTORY):
        frame = cmds.currentTime(q=True)
        path = os.path.join(directory, '%s[%s].jpg' % (name, frame))
        for i in range(self.currentSize*self.currentSize):
            cmds.select('cube%s' % i, add=True)

        cmds.viewFit()

        cmds.select(clear=True, visible=False)

        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)

        cmds.playblast(completeFilename=path,forceOverwrite=True, format="image", viewer=True, width=480, height=480,
                       showOrnaments=False)

        return path



