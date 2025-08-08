import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle 
import re
    
def _PhotometricUncertainties(u_phot: list, g_isochrone: np.ndarray):
    '''
    Returns the photometric uncertainties corresponding closest to the input magnitude
    
    Parameters
    ----------
    u_phot : list
        list of files listing the uncertainties at a given magnitude. The files must be
        ordered as follows if we consider the CMD as (colour, mag) = (c1 - c2, m)
            [path_to_file_c1, path_to_file_c2, path_to_file_m]
        The file must have the following format:
            mag,u_mag
            21.01,0.4
            21.03,0.41
            21.05,0.42

    g_isochrone : np.ndarray
        Array containing the magnitudes for which we want to compute the uncertainties

    Returns
    -------
    x1_mag_u, x2_mag_u, y_mag_u : np.ndarrays
        Arrays of the uncertianties along each of the input magnitudes
        If (colour, mag) = (c1 - c2, m) then it returns c1, c2 and m
    '''
    x1_mag = pd.read_csv(u_phot[0])
    x2_mag = pd.read_csv(u_phot[1])
    y_mag  = pd.read_csv(u_phot[2])
    
    indices = np.searchsorted(y_mag["mag"][:-1], g_isochrone)
    y_mag_u = y_mag["u_mag"][indices]

    #For x1
    indices = np.searchsorted(x1_mag["mag"][:-1], g_isochrone)
    x1_mag_u = x1_mag["u_mag"][indices]

    #For x2
    indices = np.searchsorted(x2_mag["mag"][:-1], g_isochrone)
    x2_mag_u = x2_mag["u_mag"][indices]

    return np.array(y_mag_u), np.array(x1_mag_u), np.array(x2_mag_u)

def _IsochroneOpener(name, distance: float, 
                     phot_sys: list=['G_BPmag', 'G_RPmag', 'Gmag']):
    '''
    Function opening a given PARSEC isochrone and shifting it to a certain distance
    
    Parameters
    ----------
    distance : float
        Distance in parsecs

    phot_sys : list
        Names of the filters making the CMD
        (colour, magnitude) = [colour_1, colour_2, magnitude]

    Returns
    -------
    in_file : pd.dataframe
        All points from the isochrone (white dwarf excluded)

    evolutionary_stage : tuple(np.ndarray)
        Masks of the different stages of the life of stars
        0=PMS (pre-main sequence)
        1=MS (main sequence)
        2=SGB (subgiant branch)
        3=RGB (red giant branch)
        (4,5,6)=different stages of CHEB (core-helium burning)
        7=EAGB (early asymptotic giant branch)
        8=TP-AGB (thermally pulsing AGB)
        9=post-AGB
    '''
    #Read all the lines in the PARSEC file
    with open(name) as f:
        lines = f.readlines()

    #Finds the line containing the column names
    condition = False 
    line_nb   = 0
    while (condition == False):
        x = re.search("# Zini", lines[line_nb]) 
        if (x is None) == True: line_nb+=1
        else: condition = True

    #Column names to open the file
    column_names = lines[line_nb].split()[1:]
    
    parsec_file = pd.read_csv(name, delim_whitespace=True, comment='#', 
                              header=None, names=column_names)

    #Places the isochrone at the distance it should be
    parsec_file[phot_sys[2] + "_modulus"] = 5*np.log10(distance) - 5 + parsec_file[phot_sys[2]]

    #Removes the white dwarfs
    m           = parsec_file[phot_sys[2] + "_modulus"] < max(parsec_file[phot_sys[2] + "_modulus"]) 
    parsec_file = parsec_file[m].dropna()

    evolutionary_stage = []
    for different_labels in range(1, 9):
        m = np.array((parsec_file["label"] == different_labels))
        evolutionary_stage.append(m)
    
    return parsec_file, evolutionary_stage

class _CardinalSpline():
    '''
    Give it any set of points, and it will link them beautifully
    It follows what is decribed: https://youtu.be/jvPPXbo87ds starting at 40min

    Parameters
    ----------
    x, y : np.array
        Set of points in a 2D (x, y) space

    Returns
    -------
    self.x_curve, self.y_curve : np.array, np.array
        The final spline
    '''
    def __init__(self, x: np.array, y: np.array, parameter_step: int):
        self.x  = x
        self.y  = y

        self.time_res = parameter_step
        self.x_curve  = np.zeros((len(x)-1)*self.time_res)
        self.y_curve  = np.zeros((len(y)-1)*self.time_res)

        self.EndPoints()
        self.Velocity()
        self.CurverFit()

    def EndPoints(self):
        l = len(self.x) - 1

        #Gradient between point 0 and 1, and last and before last
        x_fir = self.x[1] - self.x[0]   ; y_fir = self.y[1] - self.y[0]
        x_las = self.x[l-1] - self.x[l] ; y_las = self.y[l-1] - self.y[l]

        #Where are the new end points?
        x_fir -= self.x[0] ; y_fir -= self.y[0] ; x_las -= self.x[l] ; y_las -= self.y[l]

        #Insert those points
        self.x = np.insert(self.x, 0, - x_fir) ; self.y = np.insert(self.y, 0, - y_fir)
        self.x = np.insert(self.x, l + 2, - x_las) ; self.y = np.insert(self.y, l + 2, - y_las)


    def Velocity(self):
        self.vx = np.zeros(len(self.x))
        self.vy = np.zeros(len(self.y))

        #Deduces what should be all of the velocities
        for i in range(1, len(self.x) - 1):
            self.vx[i] = self.x[i + 1] - self.x[i - 1]
            self.vy[i] = self.y[i + 1] - self.y[i - 1]

    def PolynomSolver(self, p0, v0, p1, v1, t):
        result = np.zeros(2)
        for i in range(2):
            P0, V0, P1, V1 = p0[i], v0[i], p1[i], v1[i]
            res = (V1 + 2*P0 + V0 - 2*P1)*t**3 + (3*P1 - 2*V0 - 3*P0 - V1)*t**2 + V0*t + P0
            result[i] = res
        return result

    def PointLinker(self, index: int):
        P0 = np.array([self.x[index],   self.y[index]])
        P1 = np.array([self.x[index+1], self.y[index+1]])

        V0 = np.array([self.vx[index],   self.vy[index]])/2
        V1 = np.array([self.vx[index+1], self.vy[index+1]])/2

        times     = np.linspace(0, 1, self.time_res)
        current_x = np.zeros(len(times))
        current_y = np.zeros(len(times))

        for i in range(len(times)):
            temp = self.PolynomSolver(P0, V0, P1, V1, times[i])
            current_x[i] = temp[0]   ;   current_y[i] = temp[1]
            self.x_curve[i + (index-1)*self.time_res] = temp[0]
            self.y_curve[i + (index-1)*self.time_res] = temp[1]

    def CurverFit(self):
        for i in range(1, len(self.x) - 2):
            self.PointLinker(i)

class _IsochroneMasker():
    '''
    Masks only the stars of interest around an isochrone
    
    Parameters
    ----------
    bin_colour, bin_mag : np.ndarray, np.ndarray
        Positions of the bins

    SplineObj : "_CardinalSpline"
        Object from the class _CardinalSpline interpolating points along a given isochrone

    size : float
        Size of the selection criteria

    Returns
    -------
    self.mask : np.ndarray
        Mask returning which (bin_colour, bin_mag) are around our isochrone of interest
    '''
    def __init__(self, bin_colour: np.ndarray, bin_mag: np.ndarray, SplineObj: "_CardinalSpline",
                 size: float, u_phot: list):
        #Constructor:
        self._bin_colour = bin_colour         ;  self._bin_mag = bin_mag
        self.x_spline    = SplineObj.x_curve  ;  self.y_spline = SplineObj.y_curve
        self.size        = size               ;  self._u_phot  = u_phot

        #Execution:
        self.SelectionCriteria() 
        self.Masking() 

    def SelectionCriteria(self):
        if len(self._u_phot) != 0:
            x1_u, x2_u, y_u = _PhotometricUncertainties(self._u_phot, self.y_spline)
            self.x_u = np.array(np.sqrt(self.size**2 + x1_u**2 + x2_u**2))
            self.y_u = np.array(np.sqrt(self.size**2 + y_u**2))

        elif len(self._u_phot) == 0:
            size_array = np.ones(len(self.y_spline))*self.size
            self.x_u = np.array(np.sqrt(size_array**2))
            self.y_u = np.array(np.sqrt(size_array**2))

    def Masking(self):
        self.mask = np.zeros(len(self._bin_colour), dtype=int)
        for i in range(len(self.y_u)):
            mask_temp = (self._bin_colour - self.x_spline[i])**2/(self.x_u[i]**2) + (self._bin_mag - self.y_spline[i])**2/(self.y_u[i]**2) < 1
            self.mask += mask_temp

        self.mask[self.mask > 0.5] = 1
        self.mask = self.mask.astype(bool)

class Isochroner():
    '''
    Give it a PARSEC isochrone and it will fit/potentially mask the stars around

    Parameters 
    ----------
    file_name : str
        Location and name of the PARSEC file

    distance : float
        Distance at which we want the isochrone (in pc)

    cardinal_steps : int
        Number of steps used for the spline fitting

    horizontal_branch : str
        'all':     the whole isochrone track
        'no_hb':   not the horizontal branch
        'only_hb': only the horizontal branch

    phot_sys : list
        Names of the filters making the CMD
        (colour, magnitude) = [colour_1, colour_2, magnitude]

    gaia_cut : bool
        Cut in magnitude, below which we don't have Gaia data

    Returns
    -------
    self.iso_colour, self.iso_mag : np.array, np.array
        Fit of the isochrone

    self.selected_star_colour, self.selected_star_mag : np.array, np.array
        Stars contained within the region around the isochrone
    '''
    def __init__(self, file_name: str='x_x', distance: float=10,
                 phot_sys: list=['G_BPmag', 'G_RPmag', 'Gmag'],
                 star_stage: str='all', cardinal_steps: int=10,):
        self._file_name = file_name
        self._distance  = distance 
        self._phot_sys   = phot_sys

        isochrone, evol_stage = _IsochroneOpener(self._file_name, distance, self._phot_sys)

        self.total_mask = [] 
        self.iso_colour = np.array([]) ; self.iso_mag = np.array([])

        if star_stage == 'all':
            ms_rgb = (evol_stage[0] == True) | (evol_stage[1] == True) | (evol_stage[2] == True) 

            A = _CardinalSpline(np.array(isochrone[self._phot_sys[0]][ms_rgb] - isochrone[self._phot_sys[1]][ms_rgb]),
                            np.array(isochrone[self._phot_sys[2] + "_modulus"][ms_rgb]), cardinal_steps) 
            
            self.total_mask.append(A)
            self.iso_colour = np.concatenate((self.iso_colour, A.x_curve))
            self.iso_mag = np.concatenate((self.iso_mag, A.y_curve))

            hb = (evol_stage[3] == True) | (evol_stage[6] == True)
            A = _CardinalSpline(np.array(isochrone[self._phot_sys[0]][hb] - isochrone[self._phot_sys[1]][hb]),
                            np.array(isochrone[self._phot_sys[2] + "_modulus"][hb]), cardinal_steps) 
            
            self.total_mask.append(A)
            self.iso_colour = np.concatenate((self.iso_colour, A.x_curve))
            self.iso_mag = np.concatenate((self.iso_mag, A.y_curve))

        elif star_stage == 'no_hb':
            ms_rgb = (evol_stage[0] == True) | (evol_stage[1] == True) | (evol_stage[2] == True) 

            A = _CardinalSpline(np.array(isochrone[self._phot_sys[0]][ms_rgb] - isochrone[self._phot_sys[1]][ms_rgb]),
                            np.array(isochrone[self._phot_sys[2] + "_modulus"][ms_rgb]), cardinal_steps) 
            
            self.total_mask.append(A)
            self.iso_colour = np.concatenate((self.iso_colour, A.x_curve))
            self.iso_mag = np.concatenate((self.iso_mag, A.y_curve))

        elif star_stage == 'only_hb':
            hb = (evol_stage[3] == True) | (evol_stage[6] == True)
            A = _CardinalSpline(np.array(isochrone[self._phot_sys[0]][hb] - isochrone[self._phot_sys[1]][hb]),
                            np.array(isochrone[self._phot_sys[2] + "_modulus"][hb]), cardinal_steps) 
            
            self.total_mask.append(A)
            self.iso_colour = np.concatenate((self.iso_colour, A.x_curve))
            self.iso_mag = np.concatenate((self.iso_mag, A.y_curve))

    def _GridMaker(self, grid_density: int):
        '''
        Creates the grid for which the centres are determined to fall along the 
        isochrone or not

        Parameters
        ----------
        grid_density : int
            Same as "grid_density" in the "MaskGenerator" method

        Returns
        -------
        self._bin_colour_edges, self._bin_mag_edges : np.ndarrays
            Edges of the grid bins in colour and magnitude

        self._bin_colour, self._bin_mag : np.ndarrays
            2D arrays of the centre of the grid bins 

        self.H : np.ndarray
            Counts in the bins
        '''
        x_range, y_range = max(self._input_star_colour) - min(self._input_star_colour), max(self._input_star_mag) - min(self._input_star_mag)

        self._bin_colour_edges = np.arange(min(self._input_star_colour), max(self._input_star_colour)+0.00001, x_range/grid_density)
        self._bin_mag_edges    = np.arange(min(self._input_star_mag), max(self._input_star_mag)+0.00001, y_range/grid_density)

        #The centres of the bins of the histogram and a meshgrid of those
        x_centre = self._bin_colour_edges + x_range/grid_density/2
        y_centre = self._bin_mag_edges + y_range/grid_density/2
        self._bin_colour, self._bin_mag = np.meshgrid(x_centre[:-1], y_centre[:-1])
        del x_centre, y_centre

        H, _, _ = np.histogram2d(self._input_star_colour, self._input_star_mag, bins=(self._bin_colour_edges, self._bin_mag_edges))
        self.H  = np.transpose(H)

    def _MaskMaker(self, mask_size: float, u_phot: list):
        '''
        Makes the actual mask by calling the "_IsochroneMasker" class

        Parameters
        ----------
        mask_size : float
            Same as "mask_size" in the "MaskGenerator" method

        u_phot : list
            Same as "u_phot" in the "MaskGenerator" method

        Returns
        -------
        self.iso_mask : np.ndarray
            Mask of the size of the input stars listing the ones along the isochrone
        '''
        mask_tot = np.zeros(np.shape(self.H))
        for i in range(len(self.total_mask)):
            B = _IsochroneMasker(self._bin_colour.flatten(), self._bin_mag.flatten(),
                                self.total_mask[i], mask_size, u_phot) 
            mask_tot += B.mask.reshape(np.shape(self.H))
        mask_tot = mask_tot.astype(bool) ; self.H1 = self.H.copy() ; self.H1[~mask_tot] = 0 ; self.mask_grid = mask_tot.copy()

        # Compute bin indices
        x_bin_indices = np.digitize(self._input_star_colour, self._bin_colour_edges) - 1
        y_bin_indices = np.digitize(self._input_star_mag, self._bin_mag_edges) - 1

        # Get the bin indices for the histogram
        indice_y, indice_x = np.indices(np.shape(self.H.T))

        # Create a boolean mask of the selected bins
        selected_bins = set(zip(indice_x[mask_tot].ravel(), indice_y[mask_tot].ravel()))

        # Vectorized check for membership
        star_blob_mask = np.array([(xi, yi) in selected_bins for xi, yi in zip(x_bin_indices, y_bin_indices)], dtype=bool)

        self.iso_mask = star_blob_mask

    def MaskGenerator(self, star_colours: np.ndarray, star_magnitudes: np.ndarray, 
                      grid_density: int=100, mask_size: float=0.1, u_phot: list=[]):
        '''
        Creates a mask of the stars along an isochrone by creating a grid reducing 
        the computational time for big datasets

        Parameters
        ----------
        star_colours, star_magnitudes : np.ndarray
            Input colours and magnitudes of the stars

        grid_density : int
            The density of the grid used to say if a star falls along an isochrone

        mask_size : float 
            On top of the photometrical uncertainties, this is the colour width and
            the magnitude height of the mask

        u_phot : list
            list of files listing the uncertainties at a given magnitude. The files must
            be ordered as follows if we consider the CMD as (colour, mag) = (c1 - c2, m)
                [path_to_file_c1, path_to_file_c2, path_to_file_m]
            The file must have the following format:
                mag,u_mag
                21.01,0.4
                21.03,0.41
                21.05,0.42
                
        Returns
        -------
        self.x_curve, self.y_curve : np.array, np.array
            The final spline
        '''
        self._input_star_colour = star_colours ; self._input_star_mag = star_magnitudes 
        self._GridMaker(grid_density) 
        self._MaskMaker(mask_size, u_phot)

    def Visualiser(self, histogram: bool=False,
                   xlabel: str='$G_{\mathrm{BP}}-G_{\mathrm{RP}}$',
                   ylabel: str='$G$', xlim: list=[], ylim: list=[]):
        '''
        This allows one to easily visualise the isochrones and its selection
        
        Parameters
        ----------
        histogram: bool
            By default, the selected and unselected stars are plotted as a scatter plot
            In the case of a BIGGG dataset, one can instead plot a histogram of the 
            selected stars

        xlabel, ylabel : str
            They are the labels of the x (colour) and y (magnitude) axis

        xlim, ylim : list
            List of the limits along the x (colour) and y (magnitude) axis
            E.g.: [x_min, x_max] with x_min and x_max floats

        Returns
        -------
        A matplotlib plot to visualise the kernel
        '''
        fig, ax = plt.subplots(figsize=(4,4), dpi=221)

        if histogram == True:
            ax.pcolormesh(self._bin_colour, self._bin_mag, self.H1, cmap='Greys')

        else:
            ax.scatter(self._input_star_colour, self._input_star_mag, c='black', s=1, linewidths=0)
            ax.scatter(self._input_star_colour[self.iso_mask], self._input_star_mag[self.iso_mask],
                         c='#C90B0B', s=1, linewidths=0)
            
        ax.scatter(self.iso_colour, self.iso_mag, c='#3D55A4', s=2, linewidths=0)
        
        ax.set_xlabel(xlabel) ; ax.set_ylabel(ylabel)

        if len(xlim) == 0:
            xlim = ax.get_xlim()   ;   ylim = ax.get_ylim()

        ax.set_xlim(xlim[0], xlim[1])   ;   ax.set_ylim(ylim[0], ylim[1])
        ax.invert_yaxis()
        
        plt.show()