from astroquery.sdss import SDSS

SDSS.clear_cache()
# from astropy import coordinates as coords
# from astropy.table import Table
# import numpy as np
# import os
# import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


class astro_ob(object):
    """
    Contains all possible catgeories of astronomical object within dataset. For now, contains only AGN.
    """

    def __init__(self, name):
        self.category = name

    def get_spectra(self, num):
        """The first function get_spectra, initiates an sql query
        according to the given number of objects and returns a list of
        the given parameters for each object. This function uses concurrent
        parallelism to optiize the getting spectrum and running it concurrently.
        Documentation: https://docs.python.org/3/library/concurrent.futures.html

        Args:
            num (int): numer of AGN you want to query

        Returns:
            spectra_list (list): A list of lists of parameters (might want to edit later)
        """

        query = f"""
                SELECT DISTINCT TOP {num}
                    p.objid, p.ra, p.dec,
                    s.specobjid, s.z, s.class, s.subclass,
                    s.plate, s.mjd, s.fiberid
                FROM PhotoObjAll p 
                JOIN SpecObjAll s ON p.objid = s.bestobjid
                WHERE
                    s.class = 'GALAXY' AND s.subclass LIKE '%AGN%'
                """
        results = SDSS.query_sql(query)
        spectra_list = []  # initialize a variable to store the list

        for i in tqdm(range(num), desc="Processing Items"):

            def fetch_spec(i):
                try:
                    plate = int(results["plate"][i])
                    mjd = int(results["mjd"][i])
                    fiberid = int(results["fiberid"][i])
                    objid = int(results["objid"][i])
                    redshift = float(results["z"][i])
                    ra = float(results["ra"][i])
                    dec = float(results["dec"][i])
                    spec = SDSS.get_spectra(
                        plate=plate, mjd=mjd, fiberID=fiberid, data_release=17
                    )
                    print("tried")
                    if spec:
                        return {
                            "spectrum": spec[0],
                            "plate": plate,
                            "mjd": mjd,
                            "fiberid": fiberid,
                            "objid": objid,
                            "ra": ra,
                            "dec": dec,
                            "z": redshift,
                            "class": results["class"][i],
                            "subclass": results["subclass"][i],
                        }
                    print("done")
                except Exception as e:
                    print(f"Error fetching spectrum at index {i}: {e}")
                return None

        if results is not None:
            print("starting listing")
            with ThreadPoolExecutor(max_workers=5) as executor:
                spectra_list = list(
                    filter(None, executor.map(fetch_spec, range(len(results))))
                )
        else:
            print("No results found.")

        return spectra_list


class AGN(astro_ob):
    """For an AGN in spectra_list, extract its properties."""

    def __init__(self, name, entry):
        """Function that is run to initialize the class. Pulls information from table.

        Args:
            name (str): Type of astronomical object (inherited from astro_ob class).
            entry (dict): Contains properties of an AGN within dataset.
        """
        super().__init__(name)  # initializing parent class

        # load in the spectra
        spec_hdu = entry["spectrum"]
        data = spec_hdu[1].data
        # save flux as an attribute
        self.flux = data["flux"]
        # convert loglamnda to wavelength and save as attribute
        loglam = data["loglam"]
        self.wavelength = 10**loglam  # Flux [1e-17 erg/s/cm²/Å]

        self.plate = entry["plate"]  # Plate number
        self.mjd = entry["mjd"]  # MJD
        self.fiber_id = entry["fiberid"]  # Fiber ID
        self.id = entry["objid"]  # Object ID
        self.ra = entry["ra"]  # right ascension [units]
        self.dec = entry["dec"]  # Declination [deg]
        self.z = entry["z"]  # Redshift

    def __repr__(self):
        """Reprocesses information for an AGN.

        Returns: RA [deg]. Dec [deg], and redshift.
        """
        return f"AGN: {self.id} RA = {round(self.ra,5)}, DEC= {round(self.dec,5)}, Z = {round(self.z,5)}"

    def __str__(self):
        """Output message when AGN object is printed.
        Returns: RA [deg]. Dec [deg], and redshift.
        """
        return f"Information for AGN: {self.id}\n RA = {round(self.ra,5)}\n DEC= {round(self.dec,5)}\n Z = {round(self.z,5)}"


# possible implementation?
# from package_skeleton import astro_ob, AGN
# import tj_plotting as tj
# astroob_inst = astro_ob("AGN") instance of astronomical object, its an AGN!
# output = astroob_inst.get_spectra(num)
# instance_list = []
# for entry in output:
#   instance = AGN(entry)
#   instance_list.append(instance)
# tj.plotting_function(instance_list)
#
#
