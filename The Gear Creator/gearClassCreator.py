from maya import cmds

class Gear(object):
    """
    This is a Gear object that lets us create and modity a gear
    """
    def __init__(self):
        #The _init_ method lets us set default values
        self.constructor = None
        self.extrude = None
        self.transform = None

    def createGear(self, teeth=10, length=0.3):
        """
    This function will create a gear with the given parameters
    Args:
        teeth: The number of teeth to create
        length: The length of the teeth

    Returns:
        A tuple of the transform, constructor, and extrude node

    """
    # Teeth are every alternate face, so spans x 2
        spans = teeth * 2

        self.transform, self.constructor = cmds.polyPipe(subdivisionsAxis=spans)

        sideFaces = range(spans*2, spans*3, 2)

        cmds.select(clear=True)

        for face in sideFaces:
            cmds.select('%s.f[%s]' % (self.transform, face), add=True)

        self.extrude = cmds.polyExtrudeFacet(localTranslateZ=length)[0]

        # return transform, constructor, extrude

    def changeTeeth(self, teeth=10, length=0.3):
        spans = teeth*2
        cmds.polyPipe(self.constructor, edit=True, subdivisionsAxis=spans)
        sideFaces = range(spans*2, spans*3,2)
        faceNames = []
        for face in sideFaces:
            faceName = 'f[%s]' % (face)
            faceNames.append(faceName)
        cmds.setAttr('%s.inputComponents' % (self.extrude), len(faceNames), *faceNames, type="componentList")

        cmds.polyExtrudeFacet(self.extrude, edit=True, ltz=length)
