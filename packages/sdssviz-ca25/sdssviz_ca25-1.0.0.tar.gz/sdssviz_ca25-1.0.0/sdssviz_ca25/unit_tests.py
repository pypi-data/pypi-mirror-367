from package_skeleton import astro_ob, AGN
import interactive_plot as ip
import numpy as np


def UNIT_TEST1():
    """This test makes sure that we get the number of objects we query for
    and that the ids are all unique



    """
    ex_num = 3
    astroob_inst = astro_ob("AGN")  # instance of astronomical object, its an AGN!
    output = astroob_inst.get_spectra(ex_num)
    instance_list = []
    for entry in output:
        instance = AGN("AGN", entry)
        instance_list.append(instance)

    # make sure the number of objects we get is the same as the nubmer we asked for
    assert len(instance_list) == ex_num

    ids = [i.id for i in instance_list]
    assert len(np.unique(ids)) == len(instance_list)
    return
    # ip.interactive_plots(instance_list, 'ra', 'dec')


UNIT_TEST1()
