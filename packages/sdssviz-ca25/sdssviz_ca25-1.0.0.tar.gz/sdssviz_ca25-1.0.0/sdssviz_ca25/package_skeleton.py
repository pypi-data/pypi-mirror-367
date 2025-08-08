from astroquery.sdss import SDSS
import numpy as np

SDSS.clear_cache()
# from astropy import coordinates as coords
# from astropy.table import Table
# import numpy as np
# import os
# import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map
import pandas as pd
import os


class astro_ob(object):
    """
    Contains all possible catgeories of astronomical object within dataset. For now, contains only AGN.
    """

    def __init__(self, name):
        self.category = name

    def get_known_spectra(self, num):
        """_summary_

        Args:
            num (int): number of spectra you want to load in
        """

        colnames = ["Wavelength", "Flam", "Flam_err", "_", "__"]
        path = "./"
        # path = "/mnt/c/Users/Lauren/Documents/codeastro/sdssviz_ca25/sdssviz_ca25/"
        obj_list = []
        all_files = list(os.listdir(path + "sdss_data/"))

        coord = pd.read_csv(
            path + "sdssrm_ra_dec.dat",
            index_col=False,
            skiprows=1,
            names=["RMID", "ra", "dec"],
            sep="\    ",
            engine="python",
        )

        redshift_info = pd.read_csv(
            path + "updated_object_redshifts.dat",
            index_col=False,
            skiprows=2,
            names=["RMID", "Z"],
            sep=" ",
            engine="python",
        )

        for item in np.arange(0, num):
            # print(item)
            data = pd.read_csv(
                path + "sdss_data/" + all_files[item],
                skiprows=7,
                sep=r"\s+",
                names=colnames,
                header=None,
                engine="python",
            )
            # print(all_files[item])

            # READ IN RA / DEC
            ra = coord["ra"][item + 1]
            dec = coord["dec"][item + 1]
            # READ IN REDSHIFT
            z = redshift_info["Z"][item + 1]

            info = {
                "RMID": item,
                "z": z,
                "ra": ra,
                "dec": dec,
                "wavelength": list(data["Wavelength"][:-50]),
                "flux": list(data["Flam"][:-50]),
            }
            obj_list.append(info)
        return obj_list

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
                    s.sciencePrimary = 1 AND
                    s.class = 'GALAXY' AND
                    s.subclass LIKE '%AGN%' AND
                    p.ra IS NOT NULL AND
                    p.dec IS NOT NULL AND
                    s.z IS NOT NULL AND
                    s.plate IS NOT NULL AND
                    s.mjd IS NOT NULL AND
                    s.fiberid IS NOT NULL
                """
        results = SDSS.query_sql(query)
        print(results)
        spectra_list = []  # initialize a variable to store the list

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
            except Exception as e:
                print(f"Error fetching spectrum at index {i}: {e}")
            return None

        if results is not None:
            with ThreadPoolExecutor(
                max_workers=5
            ) as executor:  # Example: max_workers = 5
                futures = executor.map(fetch_spec, range(len(results)))
                spectra_list = list(
                    tqdm(futures, total=len(results), desc="Processing Spectra")
                )

            # with ThreadPoolExecutor(max_workers=5) as executor:
            #     spectra_list = list(filter(None, executor.map(fetch_spec, range(len(results)))))

        else:
            print("No results found.")

        return spectra_list


class AGN(astro_ob):
    """For an AGN in spectra_list, extract its properties."""

    def __init__(self, name, entry, known=False):
        """Function that is run to initialize the class. Pulls information from table.

        Args:
            name (str): Type of astronomical object (inherited from astro_ob class).
            entry (dict): Contains properties of an AGN within dataset.
        """
        super().__init__(name)  # initializing parent class

        if known:
            self.id = entry["RMID"]  # Object ID
            self.ra = entry["ra"]  # right ascension [units]
            self.dec = entry["dec"]  # Declination [deg]
            self.z = entry["z"]  # Redshift
            self.wavelength = entry["wavelength"]
            self.flux = entry["flux"]

        else:
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
