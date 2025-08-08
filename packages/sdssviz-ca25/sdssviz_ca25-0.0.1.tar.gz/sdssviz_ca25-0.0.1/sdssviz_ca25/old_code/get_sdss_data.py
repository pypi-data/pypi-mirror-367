from astroquery.sdss import SDSS
from astropy import coordinates as coords
from astropy.table import Table
import numpy as np
import os
import matplotlib.pyplot as plt

"""The first function get_spectra, initiates an sql query according to the given number of objects and returns a list of
the given parameters for each object"""
def get_spectra(num):
    query = f"""
            SELECT TOP {num}
                p.objid, p.ra, p.dec,
                s.specobjid, s.z, s.class, s.subclass,
                s.plate, s.mjd, s.fiberid
            FROM
                PhotoObjAll p JOIN SpecObjAll s ON p.objid = s.bestobjid
            WHERE
                s.class = 'GALAXY' AND s.subclass LIKE '%AGN%'
            """
    results = SDSS.query_sql(query)
    spectra_list = [] #initialize a variable to store the list

    if results is not None:
        for i in range(len(results)):
            try:
                plate = int(results['plate'][i])
                mjd = int(results['mjd'][i])
                fiberid = int(results['fiberid'][i])
                objid = int(results['objid'][i])
                redshift = float(results['z'][i])
                ra = float(results['ra'][i])
                dec = float(results['dec'][i])

                spec = SDSS.get_spectra(plate=plate, mjd=mjd, fiberID=fiberid, data_release=17)
                
                # if spec:
                #     spectra_list.append(spec[0])  # append only the first HDUList if multiple are returned
                if spec:
                    spectra_list.append({ 
                        'spectrum': spec[0],  # HDUList
                        'plate': plate,
                        'mjd': mjd,
                        'fiberid': fiberid,
                        'objid': objid,
                        'ra': ra,
                        'dec': dec,
                        'z': redshift,
                        'class': results['class'][i],
                        'subclass': results['subclass'][i]
                    })
                else:
                    print(f"No spectrum for plate={plate}, mjd={mjd}, fiber={fiberid}")
            except Exception as e:
                print(f"Error for plate={plate}, mjd={mjd}, fiber={fiberid}: {e}")
    else:
        print("No results found.")

    return spectra_list

"""Once the spectra is obtained, it is then called in the plot_spectra function which plots the spectra"""      
def plot_spectra(spectra_data):
    for entry in spectra_data:
        spec_hdu = entry['spectrum']
        data = spec_hdu[1].data
        flux = data['flux']
        loglam = data['loglam']
        wavelength = 10 ** loglam

        plt.style.use('seaborn-v0_8-colorblind')
        plt.figure(figsize=(10, 4))
        plt.plot(wavelength, flux, label=f"z = {entry['z']:.2f}", color='black', lw=0.7)

        plt.xlabel("Wavelength [Å]")
        plt.ylabel("Flux [1e-17 erg/s/cm²/Å]")
        plt.title(f"Spectrum: {entry['plate']}_{entry['mjd']}_{entry['fiberid']}")
        plt.legend()
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    spectra = get_spectra(num=2) 
    if spectra:
        plot_spectra(spectra)
