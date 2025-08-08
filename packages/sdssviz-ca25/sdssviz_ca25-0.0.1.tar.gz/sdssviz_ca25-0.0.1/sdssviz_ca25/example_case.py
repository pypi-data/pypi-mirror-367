from package_skeleton import astro_ob, AGN
import interactive_plot as ip


astroob_inst = astro_ob("AGN")  # instance of astronomical object, its an AGN!
output = astroob_inst.get_spectra(3)
instance_list = []
for entry in output:
    instance = AGN("AGN", entry)
    instance_list.append(instance)
ip.interactive_plots(instance_list, "ra", "dec")
