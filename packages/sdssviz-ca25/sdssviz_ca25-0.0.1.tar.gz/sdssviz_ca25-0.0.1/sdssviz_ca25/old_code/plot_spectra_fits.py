import os
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np

spectra_dir = "/home/anika/codeastro/codeastro_project/spectra"
fits_files = [f for f in os.listdir(spectra_dir) if f.endswith(".fits")]

for fname in fits_files:
    path = os.path.join(spectra_dir, fname)
    with fits.open(path) as hdulist:
        
        data = hdulist[1].data
        header = hdulist[0].header

        #I wanted to print the ra, dec and redshift for the objects
        ra = header.get("RA", "N/A")
        dec = header.get("DEC", "N/A")
        redshift = header.get("z", "N/A")

        print(f"File: {fname}")
        print(f"RA: {ra}")
        print(f"DEC: {dec}")
        # print(f"Redshift (z): {redshift}")
        
        

        flux = data['flux']
        loglam = data['loglam']
        wavelength = 10**loglam

        plt.style.use('seaborn-v0_8-colorblind')

        plt.figure(figsize=(10, 4))
        plt.plot(wavelength, flux, color='black', lw=0.7)
        plt.xlabel("Wavelength [Å]")
        plt.ylabel("Flux [1e-17 erg/s/cm²/Å]")
        plt.title(f"Spectrum: {fname}")
        plt.tight_layout()
        plt.show()
