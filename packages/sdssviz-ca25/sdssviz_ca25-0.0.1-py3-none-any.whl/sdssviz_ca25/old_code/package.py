import numpy as np
import matplotlib.pyplot as plt
from astroquery.sdss import SDSS
from astropy import coordinates as coords
from astropy.table import Table, unique, hstack  # type: ignore
from astropy.io import fits, ascii  # type: ignore
import os
import mplcursors

# waiting to add things fully:

# import get_sdss_data as getdata
# x = getdata.get_spectra(num=10)

"""
DEFINING STAGE 
"""
# function: get_sdss_data(number_of_files)

# define classes:
# overall astronomical object class

### subclass of AGN

### ### AGN class init:
### ### ### read in fits file & define self.


"""
RUNNING STAGE


get_sdss_data(nfiles = )

agn_object_list = []
for loop thru nfiles:
    agn = AGN(file)
    agn_object_list.append(agn)

interactive_plot(agn_object_list, plotparamx, plotparamy)
    
"""
