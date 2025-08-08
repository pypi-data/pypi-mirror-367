import numpy as np
import pickle 

from .isochrone_cutter import Isochroner

class DistanceSelector():
    @staticmethod
    def IsochroneSelector(input_colour: np.ndarray, input_magnitude: np.ndarray, 
                          distances: list, PARSEC_isochrone_path: str,
                          column_names_PARSEC_file: list, 
                          photometric_uncertainties: list,
                          mask_height_width: float=0.1, grid_density: int=500):
        '''
        This method selects stars falling along an input PARSEC isochrone that can 
        be shifted to different distances (provided in kpc)
        
        Parameters
        ----------
        input_colour, input_magnitude : np.ndarrays
            Colours and magnitudes of the input data
        
        distances : list
            List of the various distances to be probed (in kpc)

        PARSEC_isochrone_path : str
            Path to the PARSEC isochrone output file

        column_names_PARSEC_file : list
            List of the names of the columns in the PARSEC file
            E.g.: ['G_BPmag', 'G_RPmag', 'Gmag'] for Gaia in the case of (BP-RP, G)

        photometric_uncertainties : list
            List of files of the photometric uncertainties as a function of magnitude.
            E.g.: ['BP_uncer_path', 'RP_uncer_path', 'G_uncer_path'] for Gaia in 
            the case of (BP-RP, G)
            The individual files must have the following format:
            mag,u_mag
            21.01,0.4
            21.03,0.41
            21.05,0.42

        mask_height_width : float
            On top of the photometrical uncertainties, this is the colour width and
            the magnitude height of the mask

        grid_density : int
            The density of the grid used to say if a star falls along an isochrone

        Returns
        -------
        distance_dictionary : dict
            The keys correspond to the distances (in kpc). The values correspond to 
            np.ndarrays of the size of the "input_colour" and "input_magnitude", 
            masking stars falling along an isochrone
        '''
        distance_dictionary = {}

        for i in range(len(distances)):
            isochrone = Isochroner(file_name=PARSEC_isochrone_path, distance=distances[i]*1000,
                                   phot_sys=column_names_PARSEC_file)
            isochrone.MaskGenerator(star_colours=input_colour, star_magnitudes=input_magnitude,
                                   grid_density=grid_density, mask_size=mask_height_width, 
                                   u_phot=photometric_uncertainties)
            distance_dictionary[str(int(distances[i]))] = isochrone.iso_mask

        return distance_dictionary
        
    @staticmethod
    def SaveDictionary(distance_dictionary: dict, file_path_name: str):
        '''
        This method saves a dictionary in a pickle file
        
        Parameters
        ----------
        distance_dictionary : dict
            Input dictionary, should be like:
                {'11': array([False, ..., False]),
                 '21': array([False, ..., True]),}
        
        file_path_name : str
            Path and name of the file to be saved
        '''
        with open(file_path_name, 'wb') as f:
            pickle.dump((distance_dictionary), f)
    
    @staticmethod
    def LoadExistingDictionary(dictionary_path_name: str):
        '''
        This method loads a file from a pickle file
        
        Parameters
        ----------
        dictionary_path_name : str
            Path and name of the file to be saved
        
        Returns
        ----------
        distance_dictionary : dict
            Input dictionary, should be like:
                {'11': array([False, ..., False]),
                 '21': array([False, ..., True]),}
        '''
        with open(dictionary_path_name, 'rb') as f:
            distance_dictionary = pickle.load(f)
        return distance_dictionary