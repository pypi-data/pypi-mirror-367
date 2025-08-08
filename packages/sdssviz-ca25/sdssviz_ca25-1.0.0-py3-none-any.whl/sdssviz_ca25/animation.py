import matplotlib.pyplot as plt
import numpy as np
import mplcursors
from matplotlib.widgets import Button
from matplotlib.animation import FuncAnimation

# Generate mock data
num_points = 10
x = np.random.rand(num_points)
y = np.random.rand(num_points)

# Create plotting environment
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
scatter = ax[0].scatter(x, y, color='k')
ax[0].set_xlim(0, 1)
ax[0].set_ylim(0, 1)
ax[0].set_title("Main Interactive Plot")
ax[1].set_title("Spectrum")

# Set up mplcursors
cursor_click = mplcursors.cursor(scatter, hover=False)
cursor_hover = mplcursors.cursor(scatter, hover=2)

highlighted_points = []
active_selection = None
anim = None
frames = 30  # number of frames for animation

# --- Cursor callbacks ---

def on_hover(sel):
    sel.annotation.set_text(sel.index)

def on_click(sel):
    global active_selection

    # Remove previous highlight overlays
    for artist in highlighted_points:
        artist.remove()
    highlighted_points.clear()

    # Remove previous selection annotation properly
    if active_selection and active_selection != sel:
        cursor_click.remove_selection(active_selection)

    active_selection = sel

    # Update right panel
    ax[1].clear()
    ax[1].set_title("Spectrum")
    ax[1].scatter(x, y)

    sel.annotation.set_text("")  # Hide annotation text if desired

    # Add red highlight overlay on selected point
    highlight = ax[0].scatter(sel.target[0], sel.target[1], color='r', zorder=3)
    highlighted_points.append(highlight)

def on_remove(sel):
    ax[0].scatter(x=sel.target[0], y=sel.target[1], color='k')

cursor_hover.connect("add", on_hover)
cursor_click.connect("add", on_click)
cursor_click.connect("remove", on_remove)

# --- Animation function ---

def animate_shuffle(i, start_x, start_y, end_x, end_y):
    t = i / (frames - 1)
    interp_x = (1 - t) * start_x + t * end_x
    interp_y = (1 - t) * start_y + t * end_y
    scatter.set_offsets(np.column_stack((interp_x, interp_y)))
    return scatter,

# --- Shuffle logic ---

def shuffle_points(event):
    global anim, x, y, active_selection, scatter, cursor_click, cursor_hover

    # Clear previous highlights
    for artist in highlighted_points:
        artist.remove()
    highlighted_points.clear()

    # Remove active selection
    if active_selection:
        cursor_click.remove_selection(active_selection)
        active_selection = None

    # Generate new shuffled positions
    new_x = np.random.rand(num_points)
    new_y = np.random.rand(num_points)

    # Get current positions
    current_offsets = scatter.get_offsets()
    start_x = current_offsets[:, 0]
    start_y = current_offsets[:, 1]

    # --- Clear both axes and reset ---
    ax[0].clear()
    ax[1].clear()
    ax[0].set_xlim(0, 1)
    ax[0].set_ylim(0, 1)
    ax[0].set_title("Main Interactive Plot")
    ax[1].set_title("Spectrum")

    # Recreate scatter artist on ax[0]
    scatter = ax[0].scatter(start_x, start_y, color='k')

    # Recreate mplcursors on new scatter artist
    cursor_click = mplcursors.cursor(scatter, hover=False)
    cursor_hover = mplcursors.cursor(scatter, hover=2)

    cursor_click.connect("add", on_click)
    cursor_click.connect("remove", on_remove)
    cursor_hover.connect("add", on_hover)

    # Start animation
    def on_anim_end():
        global x, y
        x = new_x.copy()
        y = new_y.copy()
        scatter.set_offsets(np.column_stack((new_x, new_y)))
        fig.canvas.draw_idle()

    anim = FuncAnimation(
        fig,
        animate_shuffle,
        fargs=(start_x, start_y, new_x, new_y),
        frames=frames,
        interval=30,
        blit=True,
        repeat=False,
    )

    anim._stop = lambda: (on_anim_end(), setattr(anim, "_running", False))
    fig.canvas.draw_idle()

# --- Add shuffle button ---

button_ax = fig.add_axes([0.4, 0.01, 0.2, 0.05])
shuffle_button = Button(button_ax, "Shuffle")
shuffle_button.on_clicked(shuffle_points)

plt.tight_layout()
plt.show()
