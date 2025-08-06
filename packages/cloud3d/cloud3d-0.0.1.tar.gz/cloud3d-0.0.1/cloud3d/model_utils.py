import numpy as np

def inverse_min_max_normalize(
    norm_array: np.ndarray,
    min_val: float = -30,
    max_val: float = 20
) -> np.ndarray:
    """Inverse min-max scaling to convert normalized values back to original range.

    Args:
        norm_array (np.ndarray): Normalized array with values in the range [-1, 1].
        min_val (float): _minimum value of the original data range.
        max_val (float): _maximum value of the original data range.

    Returns:
        np.ndarray: _description_
    """
    return ((norm_array + 1) / 2) * (max_val - min_val) + min_val

def min_max_normalize(
    data: np.ndarray,
    bt_min: float = 180,
    bt_max: float = 350,
    nr_min: float = 0,
    nr_max: float = 100,
) -> np.ndarray:
    """
    Normalize each band in 'data' to the range [-1, 1] using min-max scaling.

    Args:
        data (np.ndarray): Input array of shape (C, H, W).
        band_names (list): List of band name strings, length C.
        sensor_info (dict): Mapping from band name to metadata dict containing 'band_type'.
        bt_min, bt_max: Clipping and scaling range for brightness temperature bands.
        nr_min, nr_max: Clipping and scaling range for reflectance bands.

    Returns:
        np.ndarray: Normalized data array of same shape.
    """
    norm = data.copy()
    band_names = [
        "CMI_C02", "CMI_C03", "CMI_C05", "CMI_C07", "CMI_C08",
        "CMI_C10", "CMI_C11", "CMI_C12", "CMI_C14", "CMI_C15",
        "CMI_C16"
    ]    
    sensor_info = [
        "TOA Reflectance", "TOA Reflectance", "TOA Reflectance",
        "TOA Normalised Brightness Temperature", "TOA Normalised Brightness Temperature",
        "TOA Normalised Brightness Temperature", "TOA Normalised Brightness Temperature",
        "TOA Normalised Brightness Temperature", "TOA Normalised Brightness Temperature",
        "TOA Normalised Brightness Temperature", "TOA Normalised Brightness Temperature"
    ]

    for i, key in enumerate(band_names):
        band_type = sensor_info[i]
        if band_type == 'TOA Normalised Brightness Temperature':
            band = np.clip(norm[i], bt_min, bt_max)
            norm[i] = ((band - bt_min) / (bt_max - bt_min) * 2) - 1
        elif band_type == 'TOA Reflectance':            
            band = np.clip(norm[i]*100, nr_min, nr_max)
            norm[i] = ((band - nr_min) / (nr_max - nr_min) * 2) - 1             
    return norm
