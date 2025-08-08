from package_skeleton import astro_ob, AGN
import interactive_plot as ip


astroob_inst = astro_ob("AGN")  # instance of astronomical object, its an AGN!
output = astroob_inst.get_known_spectra(40)
# output = astroob_inst.get_spectra(5)

instance_list = []
for entry in output:
    instance = AGN("AGN", entry, known=True)
    # instance = AGN("AGN", entry, known=False), this is the default version

    instance_list.append(instance)
# print(instance_list)
ip.interactive_plots(instance_list, "ra", "dec")
