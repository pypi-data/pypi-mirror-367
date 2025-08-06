

from syned.storage_ring.magnetic_structures.undulator import Undulator
from syned.storage_ring.magnetic_structures.wiggler import Wiggler
from syned.storage_ring.magnetic_structures.bending_magnet import BendingMagnet
from syned.storage_ring.light_source import LightSource
from syned.storage_ring.electron_beam import ElectronBeam

from syned.beamline.beamline import Beamline

if __name__ == "__main__":



    src1 = ElectronBeam.initialize_as_pencil_beam(energy_in_GeV=6.0,current=0.2)
    src2 = Undulator()
    src = LightSource("test",src1,src2)
    magnetic_structure = src.get_magnetic_structure()

    print(magnetic_structure)
    if isinstance(magnetic_structure, Undulator):
        print(" I am undulator")
    elif isinstance(magnetic_structure, Wiggler):
        print("I am wiggler")
    elif isinstance(magnetic_structure, BendingMagnet):
        print("I am a Bending Magnet")
    else:
        print("I do not know what I am...")


    #
    #
    #

    a = Beamline()
    magnetic_structure = a.get_light_source().get_magnetic_structure()

    print(magnetic_structure)
    if isinstance(magnetic_structure, Undulator):
        print(" I am undulator")
    elif isinstance(magnetic_structure, Wiggler):
        print("I am wiggler")
    elif isinstance(magnetic_structure, BendingMagnet):
        print("I am a Bending Magnet")
    else:
        print("I do not know what I am...")


