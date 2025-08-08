import mdtraj
import numpy as np
three_to_one = {
    'ALA': 'A', 'CYS': 'C', 'ASP': 'D', 'GLU': 'E', 'PHE': 'F',
    'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LYS': 'K', 'LEU': 'L',
    'MET': 'M', 'ASN': 'N', 'PRO': 'P', 'GLN': 'Q', 'ARG': 'R',
    'SER': 'S', 'THR': 'T', 'VAL': 'V', 'TRP': 'W', 'TYR': 'Y'
}


def compute_asphericity(trajectory: mdtraj.Trajectory):
    gyration_tensors = mdtraj.compute_gyration_tensor(trajectory)
    asphericities = []
    for gyration_tensor in gyration_tensors:
        # Calculate eigenvalues
        eigenvalues = np.linalg.eigvals(gyration_tensor)
        
        # Sort eigenvalues in ascending order
        eigenvalues.sort()
        
        # Calculate asphericity
        lambda_max = eigenvalues[-1]
        lambda_mid = eigenvalues[1]  # Middle eigenvalue
        lambda_min = eigenvalues[0]
        
        asphericity = 1-3*((eigenvalues[0]*eigenvalues[1] + eigenvalues[1]*eigenvalues[-1] + eigenvalues[-1]*eigenvalues[0])/np.power(eigenvalues[0]+eigenvalues[1]+eigenvalues[-1],2))
        asphericities.append(asphericity)
    
    return np.array(asphericities)

def compute_prolateness(trajectory: mdtraj.Trajectory):
    gyration_tensors = mdtraj.compute_gyration_tensor(trajectory)
    prolateness_values = []
    for gyration_tensor in gyration_tensors:
        # Calculate eigenvalues
        eigenvalues = np.linalg.eigvals(gyration_tensor)
        eigenvalues.sort()  # Sort eigenvalues in ascending order

        # Calculate prolateness
        lambda_max = eigenvalues[-1]
        lambda_mid = eigenvalues[1]
        lambda_min = eigenvalues[0]

        prolateness = (lambda_mid - lambda_min) / lambda_max
        prolateness_values.append(prolateness)
    
    return np.array(prolateness_values)

def compute_ensemble_sasa(trajectory: mdtraj.Trajectory):
    sasa = mdtraj.shrake_rupley(trajectory)
    total_sasa = sasa.sum(axis=1)
    return total_sasa

def compute_end_to_end_distances(trajectory: mdtraj.Trajectory, atom_selector:str, rg_norm: bool = False):
    ca_indices = trajectory.topology.select(atom_selector)
    dist = mdtraj.compute_distances(
        trajectory, [[ca_indices[0], ca_indices[-1]]]
    ).ravel()
    if rg_norm:
        rg_i = mdtraj.compute_rg(trajectory).mean()
        dist = dist / rg_i
    return dist

