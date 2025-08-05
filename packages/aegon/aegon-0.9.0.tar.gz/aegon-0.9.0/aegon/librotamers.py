import random
import numpy as np
import networkx as nx
from ase import Atoms
from aegon.libutils import adjacency_matrix, rodrigues_rotation_matrix, rotate_vector_angle_deg
#-------------------------------------------------------------------------------
def get_bridge_left_right(adjmatrix):
    G = nx.from_numpy_array(adjmatrix)
    bridges = list(nx.bridges(G))
    all=[]
    for bridge in bridges:
        [u, v] = bridge
        G_temp = G.copy()
        G_temp.remove_edge(u, v)
        componentes = list(nx.connected_components(G_temp))
        left,right=list(componentes[0]),list(componentes[1])
        if len(left)>1 and len(right)>1:
            (a,b)=bridge
            if len(left) <= len(right):
                all.append([a, b, left, right])
            else:
                all.append([b, a, right, left])
    return all
#-------------------------------------------------------------------------------
def dihedral_rotation(moleculein, bridgelist, ibridge, qdeg):
    sua=bridgelist[ibridge][0]
    nua=bridgelist[ibridge][1]
    lista=bridgelist[ibridge][2]
    kvec=moleculein[sua].position - moleculein[nua].position
    rodriguesrm=rodrigues_rotation_matrix(kvec, qdeg)
    vet=(moleculein[sua].position + moleculein[nua].position)/2.0
    for ii in range(len(moleculein)):
        if ii in lista:
            vri = np.matmul(rodriguesrm, moleculein[ii].position - vet)
            moleculein[ii].position=vri + vet
    return moleculein
#-------------------------------------------------------------------------------
def check_connectivity(atoms, adjmatrix_ref):
    adjmatrix_x=adjacency_matrix(atoms)
    return ( np.array_equiv(adjmatrix_x,adjmatrix_ref) or np.array_equal(adjmatrix_x,adjmatrix_ref) )
#-------------------------------------------------------------------------------
def rattle(moleculeseed, adjmatrix, bridgelist, qdegamp=180.0):
    nbridges=len(bridgelist)
    moleculeout=moleculeseed.copy()
    for ibridge in range(nbridges):
        fall = True
        while fall:
            qdeg=random.randint(-int(qdegamp),int(qdegamp))
            dihedral_rotation(moleculeout, bridgelist, ibridge, qdeg)
            fall = False if ( check_connectivity(moleculeout, adjmatrix) ) else True
    return moleculeout
#-------------------------------------------------------------------------------
def make_rotamers_check(moleculeseed, number, adjmatrix, bridgelist):
    qdegamp=180
    print("\nBuild the rotamer 1 (copy initial seed.xyz file as reference)")
    moleculeout=[]
    moleculetmp=moleculeseed.copy()
    moleculetmp.info['i']='seed_m001'
    moleculeout.extend([moleculetmp])
    for key in range(number-1):
        print("Build the rotamer %d" %(key+2))
        moleculetmp=rattle(moleculeseed, adjmatrix, bridgelist, qdegamp)
        moleculetmp.info['i']='random'+str(int(key+2)).zfill(3)
        moleculeout.extend([moleculetmp])
    return moleculeout
#-------------------------------------------------------------------------------
def align_bond_to_z(atoms, i, j):
    """Rota la molécula para alinear el enlace i-j con el eje z."""
    kvec=atoms[j].position - atoms[i].position
    gv1=kvec/np.linalg.norm(kvec)
    ##TMATRIX DEFINITION
    vz=np.array([0.0, 0.0, 1.0])
    vo=np.array([0.0, 0.0, 0.0])
    moleculeout=atoms.copy()
    if ( np.cross(gv1,vz) == vo).all():
        return moleculeout
    else:
        m1 = np.array([gv1[1], -gv1[0], 0.0])
        m2 = np.cross(gv1, m1)
        tmatrix = np.array([m1, m2, gv1])
    vet=(atoms[j].position + atoms[i].position)/2.0
    moleculeout.set_positions(np.dot(atoms.get_positions() - vet, tmatrix.T))
    return moleculeout
#-------------------------------------------------------------------------------
def crossover_rotamers(mola, molb, bridgelist, adjmatrix):
    n=len(mola)
    lista=[[i, np.abs(len(xa[2])-len(xa[3]))] for i,xa in enumerate(bridgelist)]
    liste = sorted(lista, key=lambda x: float(x[1]))
    indexes=[x[0] for x in liste]
    zeta=[0.0,0.0,1.0]
    moleculeout=[]
    for index in indexes:
        i=bridgelist[index][0]
        j=bridgelist[index][1]
        left=bridgelist[index][2]
        right=bridgelist[index][3]
        aliga=align_bond_to_z(mola, i, j)
        aligb=align_bond_to_z(molb, i, j)
        up = Atoms()
        for ii in right: up.append(aligb[ii])
        for angle in range(0, 360, 5):
            var=up.copy()
            rotate_vector_angle_deg(var, zeta, angle)
            hijo=Atoms()
            count=0
            for k in range(n):
                if k in left:
                    hijo.append(aliga[k])
                else:
                    hijo.append(var[count])
                    count=count+1
            test=check_connectivity(hijo, adjmatrix)
            if test:
                hijo.info['e']=float(0.0)
                hijo.info['i']='pre_child'+str(angle).zfill(4)
                return hijo
    if test is False:
        return False    
#-------------------------------------------------------------------------------
def make_random_rotamers(papy, mamy, bridgelist, adjmatrix):
    moleculeout=[]
    total_molecules=len(papy)
    for imol in range(total_molecules):
         ichildren=crossover_rotamers(papy[imol],mamy[imol],bridgelist, adjmatrix)
         if ichildren: moleculeout.extend([ichildren])
    return moleculeout
#-------------------------------------------------------------------------------    
