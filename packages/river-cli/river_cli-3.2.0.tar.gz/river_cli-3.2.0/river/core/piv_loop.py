from pathlib import Path
import numpy as np
import river.core.image_preprocessing as impp
from river.core.piv_fftmulti import piv_fftmulti

def piv_loop(
    path_images: Path,
    mask: np.ndarray,
    bbox: list,
    interrogation_area_1: int,
    interrogation_area_2: int,
    mask_auto: bool,
    multipass: bool,
    standard_filter: bool,
    standard_threshold: bool,
    median_test_filter: bool,
    epsilon: float,
    threshold: float,
    step: int,
    filter_grayscale: bool,
    filter_clahe: bool,
    clip_limit_clahe: int,
    filter_sub_background: bool,
    background: np.ndarray,
    start: int,
    end: int,
) -> dict:
    """
    Perform PIV analysis over a range of frames.
    """
    fr = start
    last_fr = end

    dict_cumul = {"u": 0, "v": 0, "x": 0, "y": 0}

    # Create mask_piv for PIV calculations
    mask_piv = np.ones_like(mask, dtype=np.uint8)

    # Preprocess the first frame only once
    image1 = impp.preprocess_image(
        path_images[fr], filter_grayscale, filter_clahe, clip_limit_clahe, filter_sub_background, background
    )

    while fr < last_fr:
        image2 = impp.preprocess_image(
            path_images[fr + 1], filter_grayscale, filter_clahe, clip_limit_clahe, filter_sub_background, background
        )

        xtable, ytable, utable, vtable, typevector, gradient = piv_fftmulti(
            image1,
            image2,
            mask=mask_piv,
            bbox=bbox,
            interrogation_area_1=interrogation_area_1,
            interrogation_area_2=interrogation_area_2,
            mask_auto=mask_auto,
            multipass=multipass,
            standard_filter=standard_filter,
            standard_threshold=standard_threshold,
            median_test_filter=median_test_filter,
            epsilon=epsilon,
            threshold=threshold,
            step=step,
        )

        x_indices = np.clip(xtable.astype(int), 0, mask.shape[1] - 1)
        y_indices = np.clip(ytable.astype(int), 0, mask.shape[0] - 1)
        in_mask = mask[y_indices, x_indices] > 0

        utable = utable.astype(float)
        vtable = vtable.astype(float)
        utable[~in_mask] = np.nan
        vtable[~in_mask] = np.nan

        try:
            dict_cumul["u"] = np.hstack((dict_cumul["u"], utable.reshape(-1, 1)))
            dict_cumul["v"] = np.hstack((dict_cumul["v"], vtable.reshape(-1, 1)))
            dict_cumul["typevector"] = np.hstack((dict_cumul["typevector"], typevector.reshape(-1, 1)))
            dict_cumul["gradient"] = np.hstack((dict_cumul["gradient"], gradient.reshape(-1, 1)))

        except ValueError:
            dict_cumul["u"] = utable.reshape(-1, 1)
            dict_cumul["v"] = vtable.reshape(-1, 1)
            dict_cumul["typevector"] = typevector.reshape(-1, 1)
            dict_cumul["gradient"] = gradient.reshape(-1, 1)
            dict_cumul["x"] = xtable
            dict_cumul["y"] = ytable

        image1 = image2
        fr += 1

    return dict_cumul
