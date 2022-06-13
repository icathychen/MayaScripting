from maya import cmds

print(renaming(selection=True))


SUFFIXES = {
    "mesh": "geo",
    "joint": "jnt",
    "camera": None,
    "ambientLight": "lgt"
}

DEFAULT_SUFFIX = "grp"

def fun():
    print("Cathy")

def renaming(selection=False):
    """
    This function will rename any objects to have the correct suffix
    Args:
        selection:  Whether or not we use the current selection

    Returns:
        A list of all the objects we operated on
    """

    objects = cmds.ls(selection=selection, dag= True, long=True)

    # This function cannot run if there is no selection and no objects
    if selection and not objects:
        raise RuntimeError("You don't have anything selected! How dare you!")

    objects.sort(key=len, reverse=True)

    for obj in objects:
        shortName = (obj.split("|")[-1])
        children = cmds.listRelatives(obj, children=True, fullPath=True) or []
        if len(children) == 1:
            child = children[0]
            objType = cmds.objectType(child)
        else:
            objType = cmds.objectType(obj)
        suffix = SUFFIXES.get(objType, DEFAULT_SUFFIX)

        if not suffix:
            continue

        if obj.endswith('_' +suffix):
            continue

        newName = "%s_%s" % (shortName, suffix)
        cmds.rename(obj, newName)

        index = objects.index(obj)
        objects[index] = obj.replace(shortName, newName)

    return objects

