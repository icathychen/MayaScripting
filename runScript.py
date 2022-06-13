import gearClassCreator as f
import importlib
from importlib import reload


importlib.reload(f)

gear = f.Gear()
#gear.createGear()

#print(gear.extrude)

gear.changeTeeth(teeth=20, length=0.2)

print(type(gear))

