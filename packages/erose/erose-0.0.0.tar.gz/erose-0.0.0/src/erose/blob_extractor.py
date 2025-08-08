import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

red_white  = LinearSegmentedColormap.from_list('truncated_bone', ["#DD0D0D",  "#C8C8C8" , "#EAEAEA"], N=256)
red_white.set_bad(color='gray')

blue_red  = LinearSegmentedColormap.from_list('truncated_bone', ["#526594", "#000000", "#B14E4E"], N=256)
blue_red.set_bad(color='gray')

from .astromorth import CoordinateTransformer
from .kernels import KernelGenerator
from .isochrone_cutter import Isochroner

class BlobExtractor():
    '''
    This class extracts blob overdensities from a map obtained with the 
    'ConvolverRunner' class
    
    Parameters
    ----------
    CR_Obj : ConvolverRunner
        An object from the 'ConvolverRunner' class

    threshold : floats
        The blobs will be selected until a certain threshold. If a blob is below
        that threshold, it will not be listed in the output file        

    min_nb_stars : float
        Minimum number of stars in the overdensity, that is the number of stars 
        in the pixels above the aforementioned 'threshold' and within a same 
        overdensity (blob)

    Returns
    -------
    self.blob_properties : pd.core.frame.DataFrame 
        The different columns of the dataframe are the following:
            - peak_max : maximum value of the blob according to the density map
                        the maximum value is 36.74
            - ra : right ascension
            - dec : declination 
            - blob_dist : distance that maximised the detection of the blob
            - blob_size : size of the kernel that maximised the detection of the blob
            - noise_com : fraction of the noise kernel--which estimates the background--
                        for which we have data
            - field_edg : boolean signaling if the detection is at the edge of the field
    '''
    def __init__(self, CR_Obj: 'ConvolverRunner', threshold: float=11., min_nb_stars: float=5):
        self.CR_Obj = CR_Obj   ;    self.min_nb_stars = min_nb_stars

        self.Extraction(threshold)
        self.BlobClassifier()
        self.BlobProperties()
        self.EmptyBlobRemover()

    def Extraction(self, threshold: float=11.):
        '''
        Method making masks of the blobs using scipy
        
        Parameters
        ----------
        threshold : floats
            The blobs will be selected until a certain threshold. If a blob is below
            that threshold, it will not be listed in the output file       

        Returns
        -------
        self.blob_labels : np.ndarray
            2D map where individual overdensities are identified by integers 
        '''
        #Data smoothing to "remove" the effects of the CCD gaps
        data   = sp.ndimage.uniform_filter(self.CR_Obj.log_map, 5) #5 is the smoothing_radius
        #Making the blob by bringing the values below the threshold to the threshold
        thresh = data > threshold
        #Fills internal holes within detected blobs
        filled = sp.ndimage.binary_fill_holes(thresh)
        #Labels the blobs, the result is stored in blobs, classified from lower left to upper right
        self.blob_labels, _ = sp.ndimage.label(filled)

    def BlobClassifier(self):
        '''
        Classifies the blobs from the most promising one to the less

        Returns
        -------
        self.blob_slices : np.ndarray
            Returns a local mask of the overdensities
        '''
        #Dictionnary of the max values of each blobs (key=label: value=maximum)
        label_to_max = {}
        for label in range(1, np.max(self.blob_labels) + 1):
            label_to_max[str(label)] = np.max(self.CR_Obj.log_map[(self.blob_labels == label)])
        label_to_max = dict(sorted(label_to_max.items(), key=lambda item: item[1], reverse=True))

        #Once dictionnary ordered, we recreate the self.blob_label array with the re-ordered blobs now
        blob_array = np.zeros(np.shape(self.blob_labels), dtype=np.int16)
        for blob in range(len(label_to_max)):
            temp_mask = (self.blob_labels == int(list(label_to_max.keys())[blob]))
            blob_array[temp_mask] = blob + 1
        self.blob_labels = blob_array    ;    del blob_array

        #Gives a selection rectangle (Python slice) around each of the blobs
        self.blob_slices = sp.ndimage.find_objects(self.blob_labels)
        self.max_values  = np.array(list(label_to_max.values()))

    def BlobProperties(self):
        '''
        Extracts the different properties of the blobs   

        Returns
        -------
        self.blob_properties : pd.core.frame.DataFrame 
            For more details see the description of the class
        '''
        #Finds the "average centroid" of each blob and then converts them from (xi, eta) to (ra, dec)
        blob_centres_ra = np.zeros(len(self.blob_slices))
        blob_centres_de = np.zeros(len(self.blob_slices))
        ra_centre       = np.zeros(len(self.blob_slices))
        de_centre       = np.zeros(len(self.blob_slices))
        for blob in range(len(self.blob_slices)):
            blob_centres_ra[blob] = np.median(self.CR_Obj.hist.x_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]])
            blob_centres_de[blob] = np.median(self.CR_Obj.hist.y_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]])
            ra_centre[blob], de_centre[blob] = CoordinateTransformer.Plane_To_Sphere(blob_centres_ra[blob],
                                                        blob_centres_de[blob], self.CR_Obj.phi_c, self.CR_Obj.theta_c)

        #Finds which kernel/distance have maximised that overdensity
        blob_dist = np.zeros(len(self.blob_slices), dtype='<U32')
        blob_size = np.zeros(len(self.blob_slices))
        for blob in range(len(self.blob_slices)):
            arr = self.CR_Obj.which_distance[self.blob_slices[blob][0], self.blob_slices[blob][1]].flatten()
            unique_values, counts = np.unique(arr, return_counts=True) ; blob_dist[blob] = unique_values[np.argmax(counts[counts != 0])]
            
            arr = self.CR_Obj.which_kernel[self.blob_slices[blob][0], self.blob_slices[blob][1]].flatten()
            unique_values, counts = np.unique(arr, return_counts=True) ; blob_size[blob] = unique_values[np.argmax(counts[counts != 0])]*self.CR_Obj.resolution

        #Let's find out the number of HB stars around each blob and if it is close to the side of a field
        field_edg = np.zeros(len(self.blob_slices), dtype=np.int8) 
        dist_2edg = 120    ;    size_hist = len(self.CR_Obj.hist.x_centre) #30arcmin = 0.5deg
        for blob in range(len(self.blob_slices)):
            pix_x_centre = int((self.blob_slices[blob][1].stop + self.blob_slices[blob][1].start)/2)
            pix_y_centre = int((self.blob_slices[blob][0].stop + self.blob_slices[blob][0].start)/2)
            if (pix_x_centre < dist_2edg) or (pix_x_centre > size_hist - dist_2edg) or (pix_y_centre < dist_2edg) or (pix_y_centre > size_hist - dist_2edg):
                field_edg[blob] = 1

        #What is the completness of the noise kernel around each blob
        noise_completness   = np.zeros(len(self.blob_slices))
        noise_kernel,  _, _ = KernelGenerator.AnnulusKernel(self.CR_Obj.background_annulus_size[0],
                                                            self.CR_Obj.background_annulus_size[1])
        for blob in range(len(self.blob_slices)):
            noise_completness[blob] = self.CR_Obj.NoiseCompletness(blob_centres_ra[blob], blob_centres_de[blob], noise_kernel)
            
        d = {'peak_max':   self.max_values, 'ra':       ra_centre, 'dec':    de_centre, 
             'blob_dist': blob_dist, 'blob_size': blob_size, 'noise_com': noise_completness,
             'field_edg': field_edg}
        self.blob_properties = pd.DataFrame(data=d).round(2)
        mask = (self.blob_properties['blob_dist'] != ''
           ) & (self.blob_properties['blob_size'] != 0)
        self.blob_properties = self.blob_properties[mask].reset_index(drop=True)
    
    def EmptyBlobRemover(self):
        '''
        Removes overdensities containing less than self.min_nb_stars (default=5) stars

        Returns
        -------
        self.blob_properties : pd.core.frame.DataFrame 
            For more details see the description of the class
        '''
        #When the mask of a blob is empty it gets automatically removed
        blobs_to_remove       = []
        number_of_stars       = np.zeros(len(self.blob_properties), dtype=np.int32)
        self.field_visualiser = np.zeros(np.shape(self.blob_labels))

        for blob in range(len(self.blob_properties)):
            #Dictionnary key for the distance which maximised the blob detection
            key_distance = str(self.blob_properties['blob_dist'].loc()[blob])

            #Mask of the current blob
            current_blob_map = np.zeros(np.shape(self.blob_labels))
            current_blob_map[(self.blob_labels == blob + 1)] += 1

            #Histogram of the stars in the region at the maximised distance
            self.CR_Obj.HistogramAndFootprint(self.CR_Obj.distance_dictionnary[key_distance], False)

            #Number of stars in the overdensity
            number_of_stars[blob] = np.sum((current_blob_map*self.CR_Obj.hist.H)[(current_blob_map*self.CR_Obj.hist.H > 0)])

            if number_of_stars[blob] < self.min_nb_stars:
                blobs_to_remove.append(blob)
            else:
                self.field_visualiser += current_blob_map
        
        self.blob_properties['nb_src'] = number_of_stars
        self.blob_properties           = self.blob_properties.drop(blobs_to_remove)

    def IsochroneToVisualise(self, PARSEC_isochrone_path: str,
                             phot_sys: list, blob_id: int=0, 
                             distance: float=0):
        '''
        Loads the isochrone that will be visualised

        Parameters
        -------
        PARSEC_isochrone_path : str
            Path to the isochrone 

        phot_sys : list
            List of the column names, same as the that the user has provided if using 
            the 'DistanceSelector' class

        blob_id : int
            Blob index given in the self.blob_properties table

        distance : float
            Distance in kpc to which the isochrone should be shifted. If different 
            than 0, shifted to distance
        '''
        if distance == 0:
            self.isochrone = Isochroner(file_name=PARSEC_isochrone_path, 
                    distance=int(self.blob_properties.loc()[blob_id]['blob_dist'])*1000,
                    phot_sys=phot_sys, cardinal_steps=50)

        else:
            self.isochrone = Isochroner(file_name=PARSEC_isochrone_path, 
                         distance=distance*1000,
                         phot_sys=phot_sys, cardinal_steps=50)
        

    def FieldVisualiser(self):
        '''
        This allows one to easily visualise the different blobs listed in 
        self.blob_properties

        Returns
        -------
        A matplotlib plot to visualise the kernel
        '''
        fig, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=151)

        ax.pcolormesh(self.CR_Obj.hist.x_centre, self.CR_Obj.hist.y_centre,
                       self.field_visualiser, cmap='Greys')
        xlim, ylim = ax.get_xlim(), ax.get_ylim()

        for blob in self.blob_properties.index:
            x_centre = np.mean(self.CR_Obj.hist.x_centre[self.blob_slices[blob][0],
                                                          self.blob_slices[blob][1]])
            y_centre = np.mean(self.CR_Obj.hist.y_centre[self.blob_slices[blob][0],
                                                          self.blob_slices[blob][1]])

            angle = np.arctan2(y_centre, x_centre)

            if angle > 0:
                if angle < np.pi/2:
                    text_pos_x = -(np.max(self.CR_Obj.hist.x_centre[self.blob_slices[blob][0],self.blob_slices[blob][1]]) - np.min(self.CR_Obj.hist.x_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]))/2
                    text_pos_y = -(np.max(self.CR_Obj.hist.y_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]) - np.min(self.CR_Obj.hist.y_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]))/2
                    ax.text(x_centre + text_pos_x, y_centre + text_pos_y, f"{blob}", color="#000000", fontsize=10, horizontalalignment='left', verticalalignment='top') 
                else:
                    text_pos_x = (np.max(self.CR_Obj.hist.x_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]) - np.min(self.CR_Obj.hist.x_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]))/2
                    text_pos_y = -(np.max(self.CR_Obj.hist.y_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]) - np.min(self.CR_Obj.hist.y_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]))/2
                    ax.text(x_centre + text_pos_x, y_centre + text_pos_y, f"{blob}", color="#000000", fontsize=10, horizontalalignment='right', verticalalignment='top') 
            else:
                if angle < np.pi/2:
                    text_pos_x = -(np.max(self.CR_Obj.hist.x_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]) - np.min(self.CR_Obj.hist.x_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]))/2
                    text_pos_y = (np.max(self.CR_Obj.hist.y_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]) - np.min(self.CR_Obj.hist.y_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]))/2
                    ax.text(x_centre + text_pos_x, y_centre + text_pos_y, f"{blob}", color="#000000", fontsize=10, horizontalalignment='left', verticalalignment='bottom') 
                else:
                    text_pos_x = (np.max(self.CR_Obj.hist.x_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]) - np.min(self.CR_Obj.hist.x_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]))/2
                    text_pos_y = (np.max(self.CR_Obj.hist.y_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]) - np.min(self.CR_Obj.hist.y_centre[self.blob_slices[blob][0], self.blob_slices[blob][1]]))/2
                    ax.text(x_centre + text_pos_x, y_centre + text_pos_y, f"{blob}", color="#000000", fontsize=10, horizontalalignment='right', verticalalignment='bottom') 

            ax.scatter(x_centre, y_centre, s=1, c='#C90C0B', alpha=0.5) 

        ax.set_xlabel(r'$\xi$ (deg)')   ;   ax.set_ylabel(r'$\eta$ (deg)')
        ax.set_xlim(xlim[1], xlim[0]) ; ax.set_ylim(ylim[0], ylim[1])
        plt.show()

    def ZoomOnOverdensity(self, blob_id: int=0, distance_around: float=18,
                          mode: str='arcmin',
                          s: float=1, dpi: int=221, savefig: str=''):
        '''
        Visualise the individual stars of the overdensity with a zoom in the region

        Parameters
        -------
        blob_id : int
            Blob index given in the self.blob_properties table

        distance_around : float 
            Plus and minus limits of the plot given in arcmin. Default is 18' = 0.3 deg

        mode : str
            View displayed in either 'arcmin' or 'deg'

        s, dpi : same as matplotlib counterparts

        savefig : str
            The plot will be saved as "savefig.pdf"
        '''
        centre_x = np.median(self.CR_Obj.hist.x_centre[self.blob_slices[blob_id][0], 
                                                       self.blob_slices[blob_id][1]])
        centre_y = np.median(self.CR_Obj.hist.y_centre[self.blob_slices[blob_id][0], 
                                                       self.blob_slices[blob_id][1]])

        final_mask = np.zeros_like(self.CR_Obj.xi, dtype=bool)
        final_mask = (abs(self.CR_Obj.xi - centre_x) < distance_around/60
                 ) & (abs(self.CR_Obj.eta - centre_y) < distance_around/60)
        
        fig, ax = plt.subplots(figsize=(4,4), dpi=221)

        if mode == 'arcmin':
            ax.scatter(x=(self.CR_Obj.xi[final_mask] - centre_x)*60, 
                    y=(self.CR_Obj.eta[final_mask] - centre_y)*60,
                    c='#000000', s=s, linewidths=0)
            ax.set_xlabel(r"$\xi$ (arcmin)")   
            ax.set_ylabel(r"$\eta$ (arcmin)")
            ax.set_xlim(-distance_around, distance_around)
            ax.set_ylim(-distance_around, distance_around)

        else:
            ax.scatter(x=self.CR_Obj.xi[final_mask] - centre_x, 
                    y=self.CR_Obj.eta[final_mask] - centre_y,
                    c='#000000', s=s, linewidths=0)
            ax.set_xlabel(r"$\xi$ (deg)")   
            ax.set_ylabel(r"$\eta$ (deg)")
            ax.set_xlim(-distance_around/60, distance_around/60)
            ax.set_ylim(-distance_around/60, distance_around/60)

        ax.invert_xaxis()

        if len(savefig) != 0:
            plt.savefig(savefig +'.pdf', dpi=dpi)

        plt.show()

    def SkyAndCMD(self, blob_id: int=0, 
                  input_colour: np.ndarray=np.array([]), 
                  input_mag: np.ndarray=np.array([]), 
                  PARSEC_isochrone_path: str='', PARSEC_col_names: list=[], 
                  distance_around: float=18, isochrone_shift: float=0,
                  colour_coded_by_iso_dist: bool=False,
                  colour_coded_by_spatial_dist: bool=False,
                  cmd_axis_names: list=[], 
                  s: float=1, dpi: int=221, savefig: str=''):
        '''
        Visualise the region of the sky around a blob, along with the colour-magnitude
        diagram of those stars. 

        Note : this method was specifically made for visualising stars

        Parameters
        -------
        blob_id : int
            Blob index given in the self.blob_properties table

        input_colour, input_mag : np.ndarrays
            Colour and magnitudes of the inputs. Needs to be of the same size as the 
            input (ra, dec) from the CR_Obj

        PARSEC_isochrone_path : str
            Path to the PARSEC isochrone used by the 'DistanceSelector' class to create
            the distance dictionnary

        PARSEC_col_names : list
            List of the names of the columns in the PARSEC file
            E.g.: ['G_BPmag', 'G_RPmag', 'Gmag'] for Gaia in the case of (BP-RP, G)

        distance_around :float
            Width/height of the spatial region to be visualised (given in arcmin).
            Default is 18' = 0.3 deg

        isochrone_shift : float
            Distance (in kpc) to which the isochrone should be shifted

        colour_coded_by_iso_dist : bool
            The stars are colour-coded according to their 'distance' to the isochrone

        colour_coded_by_spatial_dist : bool
            The stars are colour-coded according to their 'distance' to the centre of 
            the considered overdensity

        cmd_axis_names : list
            Lists of the names of the (colour, magnitude) axis of the CMD
            E.g.: ['g', 'r', 'g'] for the SDSS (g-r, g)

        s, dpi : same as matplotlib counterparts

        savefig : str
            The plot will be saved as "savefig.pdf"
        '''
        #Pre-selection of the data 
        centre_x = np.median(self.CR_Obj.hist.x_centre[self.blob_slices[blob_id][0], 
                                                       self.blob_slices[blob_id][1]])
        centre_y = np.median(self.CR_Obj.hist.y_centre[self.blob_slices[blob_id][0], 
                                                       self.blob_slices[blob_id][1]])

        final_mask = np.zeros_like(self.CR_Obj.xi, dtype=bool)
        final_mask = (abs(self.CR_Obj.xi - centre_x) < distance_around/60
                 ) & (abs(self.CR_Obj.eta - centre_y) < distance_around/60)
        
        xi  = self.CR_Obj.xi[final_mask] - centre_x
        eta = self.CR_Obj.eta[final_mask] - centre_y

        temp_colour = input_colour[self.CR_Obj.rough_mask][self.CR_Obj.exact_mask][final_mask]
        temp_mag    = input_mag[self.CR_Obj.rough_mask][self.CR_Obj.exact_mask][final_mask]

        #Loads an isochrone for visualisation
        self.IsochroneToVisualise(PARSEC_isochrone_path=PARSEC_isochrone_path, 
                                  phot_sys=PARSEC_col_names,
                                  blob_id=blob_id, distance=isochrone_shift)

        #Here we determine the distances from the isochrone
        if colour_coded_by_iso_dist == True:
            distances = np.zeros(len(temp_colour))
            for i in range(len(temp_colour)):
                distance = np.sqrt((temp_colour[i] - self.isochrone.iso_colour)**2 + (temp_mag[i] - self.isochrone.iso_mag)**2)
                distances[i] = min(distance)
            distances[distances < 0.005] = 0.005

        #Determines the spatial distances of the star
        if colour_coded_by_spatial_dist == True:
            distances = np.sqrt(xi**2 + eta**2)

        fig, ax = plt.subplots(1, 2, figsize=(8.5, 4), dpi=221)

        if ((colour_coded_by_iso_dist == True
            ) | (colour_coded_by_spatial_dist == True)):
            ax[0].scatter(xi, eta, s=s, c=np.log10(distances),
                        cmap=red_white, linewidths=0)
        else:
            ax[0].scatter(xi, eta, c='#000000', s=s, linewidths=0)
        
        ax[0].set_xlim(-distance_around/60, distance_around/60)
        ax[0].set_ylim(-distance_around/60, distance_around/60)
        ax[0].set_xlabel(r'$\xi$ (deg)')
        ax[0].set_ylabel(r'$\eta$ (deg)')

        if ((colour_coded_by_iso_dist == True
            ) | (colour_coded_by_spatial_dist == True)):
            ax[1].scatter(temp_colour, temp_mag, c=np.log10(distances),
                        cmap=red_white, s=s, linewidths=0)
        else:
            ax[1].scatter(temp_colour, temp_mag, c='#000000', s=s, linewidths=0)

        ax[1].scatter(self.isochrone.iso_colour, self.isochrone.iso_mag, 
                      s=1, linewidths=0, c='#3A54A4')
        ax[1].set_xlim(min(temp_colour), max(temp_colour))
        ax[1].set_ylim(min(temp_mag), max(temp_mag))
        ax[1].invert_yaxis()

        if len(cmd_axis_names) == 0:
            ax[1].set_xlabel(r'Colour')
            ax[1].set_ylabel(r'Magnitude')
        else:
            ax[1].set_xlabel(f'$({cmd_axis_names[0]} - {cmd_axis_names[1]})_0$')
            ax[1].set_ylabel(f'${cmd_axis_names[2]}_0$')

        if len(savefig) != 0:
            plt.savefig(savefig +'.pdf', dpi=dpi)

        plt.show()

    def CMDComparator(self, blob_id: int=0,
                      input_colour: np.ndarray=np.array([]),
                      input_mag: np.ndarray=np.array([]), 
                      central_radius: float=-1,
                      PARSEC_isochrone_path: str='',
                      PARSEC_col_names: list=[], 
                      cmd_axis_names: list=[], 
                      s: float=1, dpi: int=221, savefig: str=''):
        '''
        Visualise the region of the sky around a blob, and makes the so called Hess plot

        Note : this method was specifically made for visualising stars

        Parameters
        -------
        blob_id : int
            Blob index given in the self.blob_properties table

        input_colour, input_mag : np.ndarrays
            Colour and magnitudes of the inputs. Needs to be of the same size as the 
            input (ra, dec) from the CR_Obj

        central_radius : float
            Radius where most stars of the overdensity should be located. By default, 
            the radius used is the one that maximised the detection and listed in the 
            self.blob_properties table. Otherwise, the radius should be given in arcmin

        PARSEC_isochrone_path : str
            Path to the PARSEC isochrone used by the 'DistanceSelector' class to create
            the distance dictionnary

        PARSEC_col_names : list
            List of the names of the columns in the PARSEC file
            E.g.: ['G_BPmag', 'G_RPmag', 'Gmag'] for Gaia in the case of (BP-RP, G)

        cmd_axis_names : list
            Lists of the names of the (colour, magnitude) axis of the CMD
            E.g.: ['g', 'r', 'g'] for the SDSS (g-r, g)

        s, dpi : same as matplotlib counterparts

        savefig : str
            The plot will be saved as "savefig.pdf"
        '''
        if (central_radius == -1):
            central_radius = self.blob_properties.loc()[blob_id]['blob_size']/60
        else:
            central_radius /= 60

        central_area  = np.pi*(central_radius**2)
        #Annulus starts 3sigmas away from the central circle and areas are equal
        inner_annulus = 3*central_radius
        outer_annulus = np.sqrt(inner_annulus**2 + (central_area/np.pi))

        centre_x = np.median(self.CR_Obj.hist.x_centre[self.blob_slices[blob_id][0], 
                                                       self.blob_slices[blob_id][1]])
        centre_y = np.median(self.CR_Obj.hist.y_centre[self.blob_slices[blob_id][0], 
                                                       self.blob_slices[blob_id][1]])

        final_mask = np.zeros_like(self.CR_Obj.xi, dtype=bool)
        final_mask = (abs(self.CR_Obj.xi - centre_x) < 1.1*outer_annulus
                 ) & (abs(self.CR_Obj.eta - centre_y) < 1.1*outer_annulus)
        
        xi  = self.CR_Obj.xi[final_mask] - centre_x
        eta = self.CR_Obj.eta[final_mask] - centre_y

        #Making the masks of the circle and annulus
        mask_circle  = (xi**2 + eta**2 < central_radius**2)
        mask_annulus = (xi**2 + eta**2 > inner_annulus**2
                   ) & (xi**2 + eta**2 < outer_annulus**2)

        temp_colour = input_colour[self.CR_Obj.rough_mask][self.CR_Obj.exact_mask][final_mask]
        temp_mag    = input_mag[self.CR_Obj.rough_mask][self.CR_Obj.exact_mask][final_mask]

        H_circle, X, Y = np.histogram2d(temp_colour[mask_circle], 
                                            temp_mag[mask_circle], bins=121)

        H_annulus, _, _ = np.histogram2d(temp_colour[mask_annulus], 
                                            temp_mag[mask_annulus], bins=(X, Y))

        kernel_size  = 4
        kernel, _, _ = KernelGenerator.GaussianKernel(kernel_size, kernel_size)
        im1_num      = sp.signal.fftconvolve(H_circle - H_annulus, kernel, mode='same')
        diff_smooth  = np.array(im1_num.reshape(np.shape(H_annulus.T)))

        fig, ax = plt.subplots(1, 2, figsize=(9, 4), dpi=221)

        circle1 = plt.Circle((0, 0), outer_annulus,
                             color='#000000', alpha=0.05, linewidth=0)
        circle2 = plt.Circle((0, 0), inner_annulus,
                             color="#FFFFFF", alpha=1)
        circle3 = plt.Circle((0, 0), central_radius,
                             color='#000000', alpha=0.05, linewidth=0)

        theta = np.linspace(0, 2*np.pi, 0)
        ax[0].scatter(xi, eta, c='#000000', s=s, linewidths=0, zorder=100)
        ax[0].scatter(xi[mask_circle], eta[mask_circle],
                      c="#C94343", s=s, linewidths=0, zorder=100)
        ax[0].scatter(xi[mask_annulus], eta[mask_annulus],
                      c="#C94343", s=s, linewidths=0, zorder=100)
        ax[0].add_patch(circle1)
        ax[0].add_patch(circle2)
        ax[0].add_patch(circle3)

        ax[0].set_xlabel(r'$\xi$ (deg)')
        ax[0].set_ylabel(r'$\eta$ (deg)')
        ax[0].set_xlim(-1.1*outer_annulus, 1.1*outer_annulus)
        ax[0].set_ylim(-1.1*outer_annulus, 1.1*outer_annulus)

        pcm  = ax[1].pcolormesh(X, Y, diff_smooth.T, cmap=blue_red,
                                vmin=-np.max(abs(diff_smooth)), 
                                vmax=np.max(abs(diff_smooth)))
        cbar = plt.colorbar(pcm, ax=ax[1])
        xlim = ax[1].get_xlim()  ;  ylim = ax[1].get_ylim()

        if len(PARSEC_isochrone_path) != 0:
            self.IsochroneToVisualise(PARSEC_isochrone_path=PARSEC_isochrone_path, 
                                      phot_sys=PARSEC_col_names,
                                      blob_id=blob_id, distance=0)
            
            ax[1].scatter(self.isochrone.iso_colour, self.isochrone.iso_mag, 
                      s=1, linewidths=0, c="#FFFFFF", alpha=0.5)
            
        if len(cmd_axis_names) == 0:
            ax[1].set_xlabel(r'Colour')
            ax[1].set_ylabel(r'Magnitude')
        else:
            ax[1].set_xlabel(f'$({cmd_axis_names[0]} - {cmd_axis_names[1]})_0$')
            ax[1].set_ylabel(f'${cmd_axis_names[2]}_0$')

        ax[1].set_xlim(xlim[0], xlim[1])
        ax[1].set_ylim(ylim[0], ylim[1])
        ax[1].invert_yaxis()
        ax[1].tick_params(axis='both', color='white', labelcolor='black')
        cbar.ax.tick_params(color='white')

        if len(savefig) != 0:
            plt.savefig(savefig +'.pdf', dpi=dpi)

        plt.show()
            