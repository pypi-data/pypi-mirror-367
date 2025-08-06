import time
import warnings
warnings.filterwarnings("ignore", message="cuaev not installed")
import sys
import os
import contextlib
import torchani
from ase.optimize import BFGS
#-------------------------------------------------------------------------------
eVtokcalpermol=float(23.060548012069496)
#-------------------------------------------------------------------------------
@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
#-------------------------------------------------------------------------------
def calculator_anix_all(moleculelist, opt='ani1ccx', preclist=[1E-03, 1E-04, 1E-05]):
    moleculeout=[]
    n=len(moleculelist)
    for i,imol in enumerate(moleculelist):
        timein=time.strftime("%c")
        print('%3d from %d at %s' %(i+1,n,timein))
        id=imol.info['i']
        for prec in preclist:
            with suppress_stdout():
                calculator= {
                    'ani1x'  : torchani.models.ANI1x().ase(),
                    'ani1ccx': torchani.models.ANI1ccx().ase(),
                    'ani2x'  : torchani.models.ANI2x().ase()
                }[opt]
            imol.calc=calculator
            dyn = BFGS(imol, logfile=None)
            dyn.run(fmax=prec, steps=200)
        energy=imol.get_potential_energy()
        imol.info['e']=energy*eVtokcalpermol
        imol.info['c']=1
        moleculeout.extend([imol])
    return moleculeout
#-------------------------------------------------------------------------------
