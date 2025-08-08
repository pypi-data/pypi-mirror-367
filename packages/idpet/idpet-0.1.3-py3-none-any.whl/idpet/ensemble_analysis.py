import os
import itertools
from pathlib import Path
import re
from typing import Dict, List, Optional, Union, Tuple
import numpy as np
import zipfile
import pandas as pd
import mdtraj
from idpet.featurization.distances import rmsd
from idpet.data.api_client import APIClient
from idpet.ensemble import Ensemble
from idpet.data.io_utils import setup_data_dir, extract_tar_gz
from idpet.dimensionality_reduction import DimensionalityReductionFactory
from idpet.featurization.ensemble_level import ensemble_features
from idpet.comparison import all_vs_all_comparison
from idpet.utils import logger


class EnsembleAnalysis:
    """
    Data analysis pipeline for ensemble data.

    Initializes with a list of ensemble objects and a directory path
    for storing data.

    Parameters
    ----------
    ensembles : List[Ensemble])
        List of ensembles.
    output_dir : str, optional
        Directory path for storing data. If not provided, a directory named
        ${HOME}/.idpet/data will be created.
    """
    def __init__(self,
            ensembles: List[Ensemble],
            output_dir: str = None,
        ):
        if output_dir is None:
            self.output_dir = os.getenv(
                "IDPET_OUTPUT_DIR",  # If defined, gets an environmental variable.
                str(Path.home() / ".idpet" / "data")  # Else, uses a default path.
            )
        else:
            self.output_dir = output_dir
        self.api_client = APIClient()
        self.feature_names = []
        self.all_labels = []
        self.ensembles: List[Ensemble] = ensembles
        self.param_feat = None
        self.reduce_dim_method = None

    @property
    def ens_codes(self) -> List[str]:
        """
        Get the ensemble codes.

        Returns
        -------
        List[str]
            A list of ensemble codes.
        """
        return [ensemble.code for ensemble in self.ensembles]

    @property
    def trajectories(self) -> Dict[str, mdtraj.Trajectory]:
        """
        Get the trajectories associated with each ensemble.

        Returns
        -------
        Dict[str, mdtraj.Trajectory]
            A dictionary where keys are ensemble IDs and values are the corresponding MDTraj trajectories.
        """
        return {ensemble.code: ensemble.trajectory for ensemble in self.ensembles}

    @property
    def features(self) -> Dict[str, np.ndarray]:
        """
        Get the features associated with each ensemble.

        Returns
        -------
        Dict[str, np.ndarray]
            A dictionary where keys are ensemble IDs and values are the corresponding feature arrays.
        """
        return {ensemble.code: ensemble.features for ensemble in self.ensembles}
    
    @property
    def reduce_dim_data(self) -> Dict[str, np.ndarray]:
        """
        Get the transformed data associated with each ensemble.

        Returns
        -------
        Dict[str, np.ndarray]
            A dictionary where keys are ensemble IDs and values are the corresponding feature arrays.
        """
        return {ensemble.code: ensemble.reduce_dim_data for ensemble in self.ensembles}
    
    def __getitem__(self, code):
        for e in self.ensembles:
            if e.code == code:
                return e
        raise KeyError(f"Ensemble with code '{code}' not found")

    def __del__(self):
        if hasattr(self, 'api_client'):
            self.api_client.close_session()

    def _download_from_ped(self, ensemble: Ensemble):
        ped_pattern = r'^(PED\d{5})(e\d{3})$'

        code = ensemble.code
        match = re.match(ped_pattern, code)
        if not match:
            raise ValueError(f"Entry {code} does not match the PED ID pattern.")
        
        ped_id = match.group(1)
        ensemble_id = match.group(2)
        tar_gz_filename = f'{code}.tar.gz'
        setup_data_dir(self.output_dir)
        tar_gz_file = os.path.join(self.output_dir, tar_gz_filename)

        pdb_filename = f'{code}.pdb'
        pdb_file = os.path.join(self.output_dir, pdb_filename)

        if not os.path.exists(tar_gz_file) and not os.path.exists(pdb_file):
            url = f'https://deposition.proteinensemble.org/api/v1/entries/{ped_id}/ensembles/{ensemble_id}/ensemble-pdb'
            
            logger.warn(f"Downloading entry {code} from PED.")
            headers = {'accept': '*/*'}

            response = self.api_client.perform_get_request(url, headers=headers)
            if response is None:
                raise ConnectionError(f"Failed to connect to PED server for entry {code}.")
            if response.status_code != 200:
                raise ConnectionError(f"Failed to download entry {code} from PED. HTTP status code: {response.status_code}")
            
            # Download and save the response content to a file
            self.api_client.download_response_content(response, tar_gz_file)
            logger.info(f"Downloaded file {tar_gz_filename} from PED.")
        else:
            logger.info(f"Ensemble {code} already downloaded. Skipping.")

        # Extract the .tar.gz file
        if not os.path.exists(pdb_file):
            extract_tar_gz(tar_gz_file, self.output_dir, pdb_filename)
            logger.info(f"Extracted file {pdb_filename}.")
        else:
            logger.info(f"File {pdb_filename} already exists. Skipping extraction.")

        # Set the data path to the downloaded file
        # If the trajectory is already generated it will be used instead of the pdb file
        ensemble.data_path = pdb_file      
        chain_ids = ensemble.get_chains_from_pdb()
        if len(chain_ids) > 1 and ensemble.chain_id is not None and ensemble.chain_id in chain_ids:
            traj_suffix = f'_{ensemble.chain_id.upper()}'
        else:
            traj_suffix = ''

        traj_dcd = os.path.join(self.output_dir, f'{ensemble.code}{traj_suffix}.dcd')
        traj_top = os.path.join(self.output_dir, f'{ensemble.code}{traj_suffix}.top.pdb')

        if os.path.exists(traj_dcd) and os.path.exists(traj_top):
            logger.info(f'Trajectory file already exists for ensemble {code}.')
            ensemble.data_path = traj_dcd
            ensemble.top_path = traj_top

    def _download_from_atlas(self, ensemble: Ensemble):
        pdb_pattern = r'^\d\w{3}_[A-Z]$'
        code = ensemble.code
        if not re.match(pdb_pattern, code):
            raise ValueError(f"Entry {code} does not match the PDB ID pattern.")

        setup_data_dir(self.output_dir)
        zip_filename = f'{code}.zip'
        zip_file = os.path.join(self.output_dir, zip_filename)

        if not os.path.exists(zip_file):
            logger.warn(f"Downloading entry {code} from ATLAS.")
            url = f"https://www.dsimb.inserm.fr/ATLAS/database/ATLAS/{code}/{code}_protein.zip"
            headers = {'accept': '*/*'}

            response = self.api_client.perform_get_request(url, headers=headers)
            if response is None:
                raise ConnectionError(f"Failed to connect to Atlas server for entry {code}.")
            if response.status_code != 200:
                raise ConnectionError(f"Failed to download entry {code} from Atlas. HTTP status code: {response.status_code}")
            
            # Download and save the response content to a file
            self.api_client.download_response_content(response, zip_file)
            logger.info(f"Downloaded file {zip_filename} from Atlas.")
        else:
            logger.info("File already exists. Skipping download.")

        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Map reps to original ensemble code
                zip_contents = zip_ref.namelist()
                new_ensembles = []
                for fname in zip_contents:
                    if fname.endswith('.xtc'):
                        new_code = fname.split('.')[0]
                        data_path = os.path.join(self.output_dir, fname)
                        top_path = os.path.join(self.output_dir, f"{code}.pdb")
                        ensemble = Ensemble(code=new_code, data_path=data_path, top_path=top_path)
                        new_ensembles.append(ensemble)
                # Unzip
                zip_ref.extractall(self.output_dir)
                logger.info(f"Extracted file {zip_file}.")

                # Remove unused files.
                for unused_path in Path(self.output_dir).glob("*.tpr"):
                    os.remove(unused_path)
                readme_path = os.path.join(self.output_dir, "README.txt")
                if os.path.exists(readme_path):
                    os.remove(readme_path)

        except zipfile.BadZipFile:
            raise zipfile.BadZipFile(f"Failed to unzip file {zip_file}. The file may be corrupted.")

        return new_ensembles

    def load_trajectories(self) -> Dict[str, mdtraj.Trajectory]:
        """
        Load trajectories for all ensembles.

        This method iterates over each ensemble in the `ensembles` list and downloads
        data files if they are not already available. 
        Trajectories are then loaded for each ensemble.

        Returns
        -------
        Dict[str, mdtraj.Trajectory]
            A dictionary where keys are ensemble IDs and values are the corresponding MDTraj trajectories.

        Note
        ----
        This method assumes that the `output_dir` attribute of the class specifies the directory
        where trajectory files will be saved or extracted.
        """
        new_ensembles_mapping = {}
        for ensemble in self.ensembles:
            if ensemble.database == 'ped':
                self._download_from_ped(ensemble)
            elif ensemble.database == 'atlas':
                new_ensembles = self._download_from_atlas(ensemble)
                new_ensembles_mapping[ensemble.code] = new_ensembles
            elif ensemble.database is None:
                pass
            else:
                raise KeyError(f"Unknown database: {ensemble.database}")

        # Update self.ensembles using the mapping
        updated_ensembles = []
        for ensemble in self.ensembles:
            new_ensembles = new_ensembles_mapping.get(ensemble.code, [ensemble])
            updated_ensembles.extend(new_ensembles)
        self.ensembles = updated_ensembles
        
        for ensemble in self.ensembles:
            ensemble.load_trajectory(self.output_dir)
        
        return self.trajectories

    def random_sample_trajectories(self, sample_size: int):
        """
        Sample a defined random number of conformations from the ensemble 
        trajectory. 

        Parameters
        ----------
        sample_size: int
            Number of conformations sampled from the ensemble. 
        """
        for ensemble in self.ensembles:
            ensemble.random_sample_trajectory(sample_size)
        return self.trajectories

    def _join_ensemble_traj(self, atom_selector = 'backbone'):
        merge_traj = []
        for traj in self.trajectories:
            
            atom_indices = self.trajectories[traj].topology.select(atom_selector)
            new_ca_traj = self.trajectories[traj].atom_slice(atom_indices)
            merge_traj.append(new_ca_traj)
        joined_traj = mdtraj.join(merge_traj, check_topology=False, discard_overlapping_frames=False)
        
        return joined_traj


    def extract_features(self, featurization: str, normalize: bool = False, *args, **kwargs) -> Dict[str, np.ndarray]:
        """
        Extract the selected feature.

        Parameters
        ----------
        featurization : str
            Choose between "phi_psi", "ca_dist", "a_angle", "tr_omega", "tr_phi", "rmsd".

        normalize : bool, optional
            Whether to normalize the data. Only applicable to the "ca_dist" method. Default is False.

        min_sep : int or None, optional
            Minimum separation distance for "ca_dist", "tr_omega", and "tr_phi" methods. Default is 2.

        max_sep : int, optional
            Maximum separation distance for "ca_dist", "tr_omega", and "tr_phi" methods. Default is None.

        Returns
        -------
        Dict[str, np.ndarray]
            A dictionary where keys are ensemble IDs and values are the corresponding feature arrays.
        """
        if featurization == 'rmsd':
            self.param_feat = 'rmsd'
            j_traj = self._join_ensemble_traj()
            rmsd_matrix = rmsd(j_traj)
            self._create_all_labels()
            self.featurization = featurization
            return rmsd_matrix
            
        else:
            self.param_feat = featurization
            self._featurize(featurization=featurization, *args, **kwargs)
            self._create_all_labels()
            if normalize and featurization == "ca_dist":
                self._normalize_data()
            return self.features

    def exists_coarse_grained(self) -> bool:
        """
        Check if at least one of the loaded ensembles is coarse-grained after loading trajectories.

        Returns
        -------
        bool
            True if at least one ensemble is coarse-grained, False otherwise.
        """
        return any(ensemble.coarse_grained for ensemble in self.ensembles)

    def _featurize(self, featurization: str, *args, **kwargs):
        if featurization in ("phi_psi", "tr_omega", "tr_phi") and self.exists_coarse_grained():
            raise ValueError(f"{featurization} feature extraction is not possible when working with coarse-grained models.")
        self.featurization = featurization
        for ensemble in self.ensembles:
            ensemble.extract_features(featurization, *args, **kwargs)
        self.feature_names = list(self.ensembles)[0].names
        logger.debug(f"Feature names: {self.feature_names}")


    def _create_all_labels(self):
        self.all_labels = []
        for ensemble, traj in zip(self.ensembles,self.trajectories):
            num_data_points = self.trajectories[traj].n_frames
            self.all_labels.extend([ensemble.code] * num_data_points)

    def _normalize_data(self):
        feature_sizes = set(ensemble.features.shape[1] for ensemble in self.ensembles)
        if len(feature_sizes) > 1:
            raise ValueError("Error: Features from ensembles have different sizes. Cannot normalize data.")
        self.concat_features = self._get_concat_features()
        mean = self.concat_features.mean(axis=0)
        std = self.concat_features.std(axis=0)
        self.concat_features = (self.concat_features - mean) / std
        for ensemble in self.ensembles:
            ensemble.normalize_features(mean, std)

    def _get_concat_features(self, fit_on: List[str] = None, get_ensembles: bool = False):
        if fit_on and any(f not in self.ens_codes for f in fit_on):
            raise ValueError("Cannot fit on ensembles that were not provided as input.")
        if fit_on is None:
            fit_on = self.ens_codes
        ensembles = [ensemble for ensemble in self.ensembles if ensemble.code in fit_on]
        concat_features = [ensemble.features for ensemble in ensembles]
        concat_features = np.concatenate(concat_features, axis=0)
        logger.info(f"Concatenated featurized ensemble shape: {concat_features.shape}")
        if not get_ensembles:
            return concat_features
        else:
            return concat_features, ensembles

    def reduce_features(self, method: str, fit_on:List[str]=None, *args, **kwargs) -> np.ndarray:
        """
        Perform dimensionality reduction on the extracted features.

        Parameters
        ----------
        method : str
            Choose between "pca", "tsne", "kpca" and "umap".

        fit_on : List[str], optional
            if method is "pca" or "kpca", specifies on which ensembles the models should be fit. 
            The model will then be used to transform all ensembles.

        Additional Parameters
        ---------------------
        The following optional parameters apply based on the selected reduction method:

        - pca:
            - n_components : int, optional
                Number of components to keep. Default is 10.

        - tsne:
            - perplexity_vals : List[float], optional
                List of perplexity values. Default is range(2, 10, 2).
            - metric : str, optional
                Metric to use. Default is "euclidean". 
            - circular : bool, optional
                Whether to use circular metrics. Default is False.
            - n_components : int, optional
                Number of dimensions of the embedded space. Default is 2.
            - learning_rate : float, optional
                Learning rate. Default is 100.0.
            - range_n_clusters : List[int], optional
                Range of cluster values. Default is range(2, 10, 1).
            - random_state: int, optional
                Random seed for sklearn.
        - umap:
            - n_neighbors : List[int], optional
                List of number of neighbors. Default is [15].
            - min_dist : float, optional
                Minimum distance between points in the embedded space. Default is 0.1.
            - circular : bool, optional
                Whether to use circular metrics. Default is False.
            - n_components : int, optional
                Number of dimensions of the embedded space. Default is 2.
            - metric : str, optional
                Metric to use. Default is "euclidean".
            - random_state: int, optional
                Random seed for sklearn.    
            - range_n_clusters : List[int], optional
                Range of cluster values. Default is range(2, 10, 1).

        - kpca:
            - circular : bool, optional
                Whether to use circular metrics. Default is False.
            - n_components : int, optional
                Number of components to keep. Default is 10.
            - gamma : float, optional
                Kernel coefficient. Default is None.

        Returns
        -------
        np.ndarray
            Returns the transformed data.

        For more information on each method, see the corresponding documentation:
            - PCA: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
            - t-SNE: https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
            - Kernel PCA: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.KernelPCA.html
            - UMAP: https://umap-learn.readthedocs.io/en/latest/
        """

        if self.param_feat == 'rmsd':
            self.reducer = DimensionalityReductionFactory.get_reducer(method, *args, **kwargs)
            self.reduce_dim_method = method
            self.transformed_data = self.reducer.fit_transform(data=self.extract_features(featurization=self.param_feat))
            self.reduce_dim_model = self.reducer.fit(data=self.transformed_data)
            self._assign_concat_features(self.ensembles)
            return self.transformed_data

        else:
            # Check if all ensemble features have the same size
            feature_sizes = set(ensemble.features.shape[1] for ensemble in self.ensembles)
            if len(feature_sizes) > 1:
                raise ValueError("Features from ensembles have different sizes. Cannot concatenate.")

            self.concat_features, _ensembles = self._get_concat_features(get_ensembles=True)
            self.reducer = DimensionalityReductionFactory.get_reducer(method, *args, **kwargs)
            self.reduce_dim_method = method
            if method in ("pca", "kpca"):
                fit_on_data = self._get_concat_features(fit_on=fit_on)
                self.reduce_dim_model = self.reducer.fit(data=fit_on_data)
                for ensemble in self.ensembles:
                    ensemble.reduce_dim_data = self.reducer.transform(ensemble.features)
                    logger.info(f"Reduced dimensionality ensemble shape: {ensemble.reduce_dim_data.shape}")
                self.transformed_data = self.reducer.transform(data=self.concat_features)
            else:
                self.transformed_data = self.reducer.fit_transform(data=self.concat_features)
                self._assign_concat_features(_ensembles)
            return self.transformed_data
    
    def _assign_concat_features(self, ensembles):
        """
        Extract the dimensionality reduction features of each ensembles from the
        contatenated array, we need to store them in case users want to analyze
        them individually.
        """
        element_count = 0
        for ensemble in ensembles:
            ens_size = ensemble.get_size()
            ensemble.reduce_dim_data = self.transformed_data[element_count:ens_size+element_count]
            element_count += ens_size
            logger.info(f"Reduced dimensionality ensemble shape: {ensemble.reduce_dim_data.shape}")
        

    def execute_pipeline(self, featurization_params:Dict, reduce_dim_params:Dict, subsample_size:int=None):
        """
        Execute the data analysis pipeline end-to-end. The pipeline includes:
            1. Download from database (optional)
            2. Generate trajectories
            3. Randomly sample a number of conformations from trajectories (optional)
            4. Perform feature extraction
            5. Perform dimensionality reduction

        Parameters
        ----------
        featurization_params: Dict
            Parameters for feature extraction. The only required parameter is "featurization",
            which can be "phi_psi", "ca_dist", "a_angle", "tr_omega" or "tr_phi". 
            Other method-specific parameters are optional.
        reduce_dim_params: Dict
            Parameters for dimensionality reduction. The only required parameter is "method",
            which can be "pca", "tsne" or "kpca".
        subsample_size: int, optional
            Optional parameter that specifies the trajectory subsample size. Default is None.
        """
        self.load_trajectories()
        if subsample_size is not None:
            self.random_sample_trajectories(subsample_size)
        self.extract_features(**featurization_params)
        self.reduce_features(**reduce_dim_params)

    def get_features(self, featurization: str, normalize: bool = False, *args, **kwargs) -> Dict[str, np.ndarray]:
        """
        Extract features for each ensemble without modifying any fields in the EnsembleAnalysis class.

        Parameters:
        -----------
        featurization : str
            The type of featurization to be applied. Supported options are "phi_psi", "tr_omega", "tr_phi", "ca_dist", "a_angle", "rg", "prolateness", "asphericity", "sasa", "end_to_end" and "flory_exponent".

        min_sep : int, optional
            Minimum sequence separation distance for "ca_dist", "tr_omega", and "tr_phi" methods. Default is 2.

        max_sep : int or None, optional
            Maximum sequence separation distance for "ca_dist", "tr_omega", and "tr_phi" methods. Default is None.

        normalize : bool, optional
            Whether to normalize the extracted features. Normalization is only supported when featurization is "ca_dist". Default is False.

        Returns:
        --------
        Dict[str, np.ndarray]
            A dictionary containing the extracted features for each ensemble, where the keys are ensemble IDs and the 
            values are NumPy arrays containing the features.

        Raises:
        -------
        ValueError:
            If featurization is not supported, or if normalization is requested for a featurization method other than "ca_dist".
            If normalization is requested and features from ensembles have different sizes.
            If coarse-grained models are used with featurization methods that require atomistic detail.
        """
        if featurization in ("phi_psi", "tr_omega", "tr_phi") and self.exists_coarse_grained():
            raise ValueError(f"{featurization} feature extraction is not possible when working with coarse-grained models.")
        
        if normalize and featurization not in ("ca_dist", "end_to_end"):
            raise ValueError("Normalization is only supported when featurization is 'ca_dist'.")
        
        features_dict = {}
        for ensemble in self.ensembles:
            features = ensemble.get_features(featurization=featurization, normalize=normalize, *args, **kwargs)
            if featurization != "flory_exponent":
                features_dict[ensemble.code] = features
            else:
                features_dict[ensemble.code] = features[0]
            
        if normalize and featurization == "ca_dist":
            feature_sizes = set(features.shape[1] for features in features_dict.values())
            if len(feature_sizes) > 1:
                raise ValueError("Error: Features from ensembles have different sizes. Cannot normalize data.")
            concat_features = np.concatenate(list(features_dict.values()), axis=0)
            mean = concat_features.mean(axis=0)
            std = concat_features.std(axis=0)
            for key, features in features_dict.items():
                features_dict[key] = (features - mean) / std
        
        return features_dict
    
    def get_features_summary_dataframe(self, selected_features: List[str] = ["rg", "asphericity", "prolateness", "sasa", "end_to_end", "flory_exponent"], show_variability: bool = True) -> pd.DataFrame:
        """
        Create a summary DataFrame for each ensemble.

        The DataFrame includes the ensemble code and the average for each feature.

        Parameters
        ----------
        selected_features : List[str], optional
            List of feature extraction methods to be used for summarizing the ensembles.
            Default is ["rg", "asphericity", "prolateness", "sasa", "end_to_end", "flory_exponent"].
        show_variability: bool, optional
            If True, include a column  a measurment of variability for each
            feature (e.g.: standard deviation or error).

        Returns
        -------
        pd.DataFrame
            DataFrame containing the summary statistics (average and std) for each feature in each ensemble.
        
        Raises
        ------
        ValueError
            If any feature in the selected_features is not a supported feature extraction method.
        """
        supported_features = {"rg", "asphericity", "prolateness", "sasa", "end_to_end", "ee_on_rg", "flory_exponent"}

        # Validate the selected_features
        invalid_features = [feature for feature in selected_features if feature not in supported_features]
        if invalid_features:
            raise ValueError(f"Unsupported feature extraction methods: {', '.join(invalid_features)}")

        summary_data = []

        for ensemble in self.ensembles:
            ensemble_code = ensemble.code
            summary_row = [
                ensemble_code,
                ensemble.trajectory.n_residues,
                len(ensemble.trajectory)
            ]
            
            for feature in selected_features:
                features = ensemble.get_features(featurization=feature, normalize=False)
                if feature not in ensemble_features:
                    features_array = np.array(features)
                    feature_mean = features_array.mean()
                    feature_std = features_array.std()
                    summary_row.extend([feature_mean, feature_std])
                else:
                    summary_row.extend([features[0], features[1]])
            
            summary_data.append(summary_row)

        columns = ['ensemble_code', 'n_residues', 'n_conformers']
        for feature in selected_features:
            if feature not in ensemble_features:
                columns.extend([f"{feature}_mean", f"{feature}_std"])
            else:
                columns.extend([feature, f"{feature}_err"])

        summary_df = pd.DataFrame(summary_data, columns=columns)
        if not show_variability:
            summary_df = summary_df[[c for c in summary_df.columns \
                                     if not c.endswith(("_std", "_err"))]]
        
        return summary_df
    
    
    def comparison_scores(
            self,
            score: str,
            featurization_params: dict = {},
            bootstrap_iters: int = None,
            bootstrap_frac: float = 1.0,
            bootstrap_replace: bool = True,
            bins: Union[int, str] = 50,
            random_seed: int = None,
            verbose: bool = False
        ) -> Tuple[np.ndarray, List[str]]:
        """
        Compare all pair of ensembles using divergence/distance scores.
        See `dpet.comparison.all_vs_all_comparison` for more information.
        """

        return all_vs_all_comparison(
            ensembles=self.ensembles,
            score=score,
            featurization_params=featurization_params,
            bootstrap_iters=bootstrap_iters,
            bootstrap_frac=bootstrap_frac,
            bootstrap_replace=bootstrap_replace,
            bins=bins,
            random_seed=random_seed,
            verbose=verbose,
        )