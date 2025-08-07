import numpy as np
import os
from typing import Optional, Tuple, List, Union
import skimage.io as skio
import scipy.stats as scistats
import marimo as mo


__version__: str = "2025.8.6.1"
__test_path__: str = os.path.join(os.path.dirname(__file__), "tests", "test_im_5d.tif")


def load(image: Union[str, np.ndarray], channel_strs: Optional[Tuple[str]] = ('',), setup_ui: bool = True) -> \
        Tuple[Optional[np.ndarray], Optional[mo._plugins.ui._impl.dictionary.dictionary]]:
    """
    Reads and formats the image from the given path.

    :param image: the image to be rendered. Can be the path to a file (.tif, .tiff, .jpg, .jpeg, .gif, .png, or .bmp) or to a directory containing the image files.
    :param channel_strs: if image is a path and points to a directory, channel_strs is a list of unique strings identifying the channels to be loaded. If empty, all images will be loaded into the same channel.
    :param setup_ui: whether to instantiate the monkie ui elements.
    :return: the image in 5-d array format (t, z, c, x, y) and the marimo UI dictionary (or None if setup_ui is False).
    """

    im: np.ndarray = None

    if os.path.isfile(image):
        _, ext = os.path.splitext(image)

        # First try to read images within the allowed extensions.
        if str.lower(ext) in ('.tif', '.tiff', '.jpg', '.jpeg', '.gif', '.png', '.bmp'):
            im = skio.imread(image)
        # If the extension is unknown, try to read as a tiff file.
        else:
            try:
                im = skio.imread(image, plugin='tifffile')
            except:
                return None, None

    elif os.path.isdir(image):
        channels: List[np.ndarray] = [[] for _ in channel_strs]

        for filename in os.listdir(image):
            img, _ = load(os.path.join(image, filename), setup_ui=False)

            if img is not None:
                index_list = [theindex for theindex in range(len(channel_strs)) if channel_strs[theindex] in filename]

                if index_list != []:
                    channels[index_list[0]].append(img)

        im = np.asarray(channels)

    elif isinstance(image, np.ndarray):
        im = image

    match im.ndim:
        case 2:
            im = np.expand_dims(im, axis=(0, 1, 2,))
        case 3:
            im = np.expand_dims(im, axis=(0, 1,))
        case 4:
            im = np.expand_dims(im, axis=(0,))
        case 5:
            im = im
        case _:
            im = None

    if setup_ui:
        ui = __setup_ui__(im)
    else:
        ui = None

    return im, ui


def __setup_ui__(im: np.ndarray) -> Optional[mo._plugins.ui._impl.dictionary.dictionary]:
    """
    Sets up the UI elements using information from the image array.

    :param im: the image in 5-d array format (t, z, c, x, y) as output from read_image.
    :return: a marimo UI dictionary containing all the UI elements.
    """

    if im is None:
        return None

    ui = mo.ui.dictionary({
        "t_slider": mo.ui.slider(start=1, stop=im.shape[0], step=1, label="t"),
        "z_slider": mo.ui.slider(start=1, stop=im.shape[1], step=1, label="z"),
        "c_slider": mo.ui.slider(start=1, stop=im.shape[2], step=1, label="c"),
        "invert_switch": mo.ui.switch(value=False, label="Invert image"),
        "fliph_switch": mo.ui.switch(value=False, label="Horizontal flip"),
        "flipv_switch": mo.ui.switch(value=False, label="Vertical flip"),
        "plane_radio": mo.ui.radio(["x-y", "z-y", "z-x"], value="x-y", label="slicing plane"),
        "vmin_slider": mo.ui.slider(start=0, stop=np.max(im), step=1, value=0,
                                    label="minimum pixel value", show_value=True),
        "vmax_slider": mo.ui.slider(start=0, stop=np.max(im), step=1, value=np.max(im),
                                    label="maximum pixel value", show_value=True),
        "autocontrast_button": mo.ui.button(label="auto contrast", value=False, on_click=lambda value: not value),
    })
    return ui


def show(im: Optional[np.ndarray], ui: Optional[mo._plugins.ui._impl.dictionary.dictionary]) -> \
        mo._output.hypertext.Html:
    """
    Displays the MoNkIE UI. This function can be run directly off of the outputs from read_image and setup_ui.

    :param im: the image in 5-d array format (t, z, c, x, y) as output from read_image.
    :param ui: the marimo UI dictionary containing the UI elements as output from setup_ui.
    :return: the marimo UI interface which can be displayed by outputting it from a cell.
    """

    if im is None:
        return mo.md(
            "/// attention | Image Error! Could not display the image. Check that the image path is correct and that the image is loaded correctly.")
    if ui is None:
        return mo.md("/// attention | UI Error! No UI provided to display.")

    t, z, c = ui["t_slider"].value - 1, ui["z_slider"].value - 1, ui["c_slider"].value - 1

    orientations = {'x-y': [0, 1, 2, 3, 4], 'z-x': [0, 3, 2, 4, 1], 'z-y': [0, 4, 2, 3, 1]}
    im = np.transpose(im, orientations[ui["plane_radio"].value])
    im = im[t, z, c, :, :]

    if ui["autocontrast_button"].value:
        low, high = scistats.mode(im.ravel())[0], np.percentile(im, 99)
    else:
        low, high = ui["vmin_slider"].value, max(ui["vmin_slider"].value, ui["vmax_slider"].value)
    im = np.clip(im, low, high)

    if ui["invert_switch"].value:
        im = 1 - im
    if ui["fliph_switch"].value:
        im = im[..., ::-1]
    if ui["flipv_switch"].value:
        im = im[..., ::-1, :]

    disp = mo.image(src=im,
                    width=500,
                    height=500)
    widg = __construct_interface__(ui)
    return mo.vstack([widg, disp])


def __construct_interface__(ui: mo._plugins.ui._impl.dictionary.dictionary) -> mo._output.hypertext.Html:
    """
    Lays out the MoNkIE UI. This function can be run from the ui dictionary output of setup_ui.

    :param ui: the marimo UI dictionary containing all of the elements to lay out.
    :return: the marimo UI layout for MoNkIE.
    """

    contrast_selection = mo.vstack([ui["vmin_slider"], ui["vmax_slider"], ui["autocontrast_button"]], justify="start")
    channel_selection = mo.hstack([mo.vstack([ui["t_slider"], ui["z_slider"], ui["c_slider"]], gap=0.8),
                                   ui["plane_radio"],
                                   contrast_selection],
                                  widths=[1, 3, 24])
    switches = mo.hstack([ui["invert_switch"], ui["fliph_switch"], ui["flipv_switch"]], justify="start", align="center")

    return mo.vstack([channel_selection, switches])

