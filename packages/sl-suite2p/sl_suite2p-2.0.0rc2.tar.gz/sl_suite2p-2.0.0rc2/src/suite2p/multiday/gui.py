"""This module provides an interactive Jupyter GUI used to visualize the outputs of the multi-day registration
pipeline registration step."""

from pathlib import Path

import numpy as np
from natsort import natsorted
import ipywidgets as widgets  # type: ignore
from ipywidgets import HBox, VBox
from IPython.display import display
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt


def show_images_with_masks(
    ops_path: Path,
    aspect_ratio: float = 1.5,
) -> None:
    """Provides an interactive jupyter-based GUI for visualizing session reference images and cell mask sets generated
    during multi-day registration.

    This function is primarily used in jupyter notebooks to visualize the results of the first multi-day pipeline step
    (registration). It can be used to assess the quality of multi-day registration by visually comparing various cell
    masks and images generated during runtime.

    Notes:
        The function automatically resolves and loads the necessary data from the multi-day output folders of each
        multi-day processed session based on the data inside the target folder.

        This function assumes it is called after processing the sessions with the multi-day pipeline. Calling it for
        datasets that have not been processed with the multi-day pipeline would likely result in unexpected behavior.

        In the future, this dedicated GUI may be deprecated in favor of integrating this functionality into the main
        suite2p GUI to truly unify the two pipelines under the suite2p library umbrella.

    Args:
        ops_path: The path to the multi-day suite2p pipeline ops.npy file for the multi-day dataset to be visualized.
            Note, to prevent issues associated with visualizing the data processed on a different machine, this function
            assumes that the ops.npy file is always stored inside the root multi-day output directory.
        aspect_ratio: The aspect ratio to use for the rendered images.
    """

    # Assumes that the 'ops' file is stored inside the root multi-day directory, so that the root directory to the
    # parent of 'ops'
    output_folder = ops_path.parent

    # The output folder contains .npy and .yaml files and directories named after each processed session ID.
    # This re-generates the list of session IDs from the directories stored in the output folder.
    session_ids = [folder.stem for folder in output_folder.glob("*") if folder.is_dir()]

    # Sorts session IDs for consistency
    session_ids = natsorted(session_ids)

    # Loads available masks and images
    session_folders = [output_folder.joinpath(session_id, "multi_day") for session_id in session_ids]
    images = []
    masks = []

    # Data is loaded for each session folder processed as part of the multi-day runtime specified by the 'ops'.
    for folder in session_folders:
        # Loads original and transformed images. Merges transformed images into the original image dictionary,
        # modifying the keys to include the word 'transformed' to identify various image sets to GUI users.
        original_images = np.load(folder.joinpath("original_images.npy"), allow_pickle=True).item()
        transformed_images = np.load(folder.joinpath("transformed_images.npy"), allow_pickle=True).item()
        for key in transformed_images.keys():
            original_images[f"transformed_{key}"] = transformed_images[key]

        # Imports different sets of cell masks collected as part of the multi-day registration process.
        mask_sets = {
            "unregistered_masks": np.load(folder.joinpath("unregistered_masks.npy"), allow_pickle=True),
            "registered_masks": np.load(folder.joinpath("registered_masks.npy"), allow_pickle=True),
            "shared_multiday_masks": np.load(folder.joinpath("shared_multiday_masks.npy"), allow_pickle=True),
            "session_multiday_masks": np.load(folder.joinpath("session_multiday_masks.npy"), allow_pickle=True),
        }
        images.append(original_images)
        masks.append(mask_sets)

    # Extracts image and cell mask sets names
    image_names = list(images[0].keys())
    mask_names = list(masks[0].keys())

    # Sets up UI widgets
    session_ui = widgets.IntSlider(
        min=0, max=len(session_ids) - 1, step=1, value=0, continuous_update=True, description="Session:"
    )
    img_ui = widgets.Dropdown(options=image_names, value=image_names[0], description="Img Type:")
    set_ui = widgets.Dropdown(options=mask_names, value=mask_names[0], description="Mask Type:")
    opacity_ui = widgets.FloatSlider(
        min=0, max=1, step=0.1, value=0.5, continuous_update=True, description="Mask Opacity:"
    )
    masks_ui = widgets.Checkbox(True, description="Show Cell Masks")
    ui = HBox([VBox([img_ui, session_ui]), masks_ui, VBox([set_ui, opacity_ui])])

    # Resolves the colormap to use for cell masks (each mask gets a unique color. Most calls to this function are
    # expected to have less than 10,000 cells.
    vals = np.linspace(0, 1, 10000)
    np.random.seed(4)
    np.random.shuffle(vals)

    # noinspection PyUnresolvedReferences
    colors = plt.cm.hsv(vals)  # type: ignore
    cmap = ListedColormap(colors)

    # Sets up the interactive figure
    fig = plt.figure(figsize=(6, 6), dpi=300)
    ax = fig.subplots()
    ax.axis("off")
    handle_main = ax.imshow(images[0][image_names[0]], cmap="gray", interpolation="none")
    label_mask = masks[0][mask_names[0]]
    label_mask = np.ma.masked_where(label_mask == 0, label_mask)  # type: ignore
    handle_overlay = ax.imshow(label_mask, cmap=cmap, alpha=0.5, interpolation="none", vmin=1, vmax=20000)
    ax.set_aspect(aspect_ratio)
    plt.tight_layout()
    fig.canvas.header_visible = False  # type: ignore

    def update_display(session: int, img_type: str, mask_set: str, show_masks: bool, opacity: float) -> None:
        """Updates the displayed image and mask overlay based on the widget state.

        This service function is used to re-render the figure in response to user interaction via Jupyter environment.

        Args:
            session: The index of the session to display.
            img_type: The image type to display (e.g., 'mean').
            mask_set: The cell mask set to overlay.
            show_masks: Determines whether to show cell masks.
            opacity: The opacity of the mask overlay, from 0.0 (transparent) to 1.0 (opaque).
        """

        # Sets the title to include the session ID
        ax.set_title(f"session: {session_ids[session]}", fontsize=12)

        # Shows the image with overlay
        handle_main.set_data(images[session][img_type])

        # If requested, resolves and draws the cell mask ROI overlays
        if show_masks:
            current_masks = masks[session][mask_set]
            if isinstance(current_masks, np.ndarray) and current_masks.ndim == 3:
                cell_label_mask = current_masks[0]
            else:
                cell_label_mask = current_masks
            cell_label_mask = np.ma.masked_where(cell_label_mask == 0, cell_label_mask)  # type: ignore
        else:
            cell_label_mask = np.ma.masked_where(np.zeros((1, 1)) == 0, np.zeros((1, 1)))  # type: ignore

        handle_overlay.set_data(cell_label_mask)
        handle_overlay.set_alpha(opacity)
        handle_main.autoscale()

    # Renders the figure and displays it to the user inside the Jupyter cell
    out = widgets.interactive_output(
        update_display,
        {"session": session_ui, "img_type": img_ui, "mask_set": set_ui, "show_masks": masks_ui, "opacity": opacity_ui},
    )
    display(ui, out)  # type: ignore
