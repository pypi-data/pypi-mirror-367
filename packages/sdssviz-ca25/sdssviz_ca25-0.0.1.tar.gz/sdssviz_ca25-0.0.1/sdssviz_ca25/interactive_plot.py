import matplotlib.pyplot as plt
import numpy as np
import mplcursors


def interactive_plots(agn_obj_list, paramx, paramy):
    """Interactive scatterplot

    Creates a two-panel plot with scatter plot on the left side with cursors through
    which the user can interact with the points. Clicking on a point highlights it and
    populates the plot on the right.

    Args:
        agn_obj_list (list): list of AGN objects
        paramx (string): parameter to be plotted on the x axis. select from: ra, dec, z, id
        paramy (string): parameter to be plotted on the y axis. select from: ra, dec, z, id

    Returns:
        None
    """
    # x = [getattr(agn_obj_list[i], paramx) for i in range(len(agn_obj_list))]
    # y = [getattr(agn_obj_list[i], paramy) for i in range(len(agn_obj_list))]
    # ids = [getattr(agn_obj_list[i], "id") for i in range(len(agn_obj_list))]

    if (type(paramx) != str) or (type(paramy) != str):
        raise TypeError("paramx/y must be a string.")

    if paramx != ("ra" or "dec" or "z" or "id"):
        print(paramx)
        raise ValueError("Unsupported paramx. We currently support: ra, dec, z, id")
    if (paramy == "ra") or (paramy == "dec") or (paramy == "z") or (paramy == "id"):
        print("good paramy")
    else:
        print(paramy)
        raise ValueError("Unsupported paramy. We currently support: ra, dec, z, id")

    """optimizing this chunk so we dont call the x,y,ids individually"""

    x, y, ids, redshift = zip(
        *[
            (getattr(agn, paramx), getattr(agn, paramy), agn.id, agn.z)
            for agn in agn_obj_list
        ]
    )

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    scatter = ax[0].scatter(x, y, color="k")
    ax[0].set_title("Main Interactive Plot")
    ax[0].set(xlabel=str(paramx), ylabel=str(paramy))
    ax[1].set_title("Spectrum")

    # Instead of calling plot_spectrum() every time:
    (line,) = ax[1].plot([], [], color="black", lw=0.7)

    redshift_label = ax[1].text(
        0.98, 0.98, "", transform=ax[1].transAxes, ha="right", va="top", fontsize=10
    )

    cursor_click = mplcursors.cursor(
        scatter, hover=False
    )  # or just mplcursors.cursor()
    cursor_hover = mplcursors.cursor(scatter, hover=2)

    def on_hover(sel):
        # TODO: replace 'sel.index' with AGN name
        sel.annotation.set_text(ids[sel.index])

    # def on_click(sel):
    #     # generates a new plot in the other panel
    #     ax[1].clear()

    #     sel.annotation.set_text("")
    #     ax[0].scatter(x=sel.target[0], y=sel.target[1], color="r")
    #     # plot the spectrum:
    #     plot_spectrum(agn_obj_list, sel.index, ax[1])

    """ I used google Ai and asked it to optimize the plotting code and 
    this is what I got. [This version updates an existing plot object, line, within ax[1]. 
    Instead of clearing and redrawing, it modifies the data (set_data) of an already 
    created line object. 
    It then calls ax[1].relim() and ax[1].autoscale_view() to adjust the axis limits based 
    on the new data,and fig.canvas.draw_idle() to trigger a redraw of the figure. 
    This method is generally more efficient 
    for dynamic updates as it avoids recreating plot elements.]- source (Google AI)
    """

    def on_click(sel):
        sel.annotation.set_text("")

        ax[0].scatter(x=sel.target[0], y=sel.target[1], color="r")

        agn = agn_obj_list[sel.index]
        line.set_data(agn.wavelength, agn.flux)
        ax[1].relim()
        ax[1].autoscale_view()
        ax[1].set_title(f"Spectrum of {agn.id}")
        ax[1].legend()
        redshift_label.set_text(
            f"Redshift: {agn.z:.4f}"
        )  # Format redshift to two decimal places
        ax[1].legend()
        fig.canvas.draw_idle()

    def on_remove(sel):
        ax[0].scatter(x=sel.target[0], y=sel.target[1], color="k")
        # redshift_label.set_text('')

    cursor_hover.connect("add", on_hover)
    cursor_click.connect("add", on_click)
    cursor_click.connect("remove", on_remove)

    plt.show()


def plot_spectrum(agn_obj_list, index, ax):
    """Plots a spectrum

    Args:
        agn_obj_list (list): list of AGN objects
        index (int): index of AGN object
        ax (matplotlib.axes._axes.Axes): plot axis on which we will plot the spectrum

    Returns:
        None


    """
    ax.plot(
        agn_obj_list[index].wavelength, agn_obj_list[index].flux, color="black", lw=0.7
    )
    ax.set(
        xlabel="Wavelength [Å]",
        ylabel="Flux [1e-17 erg/s/cm$^2$/Å]",
        title="Spectrum of " + str(agn_obj_list[index].id),
    )


if __name__ == "__main__":
    print("you shouldn't be calling this is as main")
