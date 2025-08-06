import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
import warnings
from scipy import ndimage

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _get_heights(height_levels: Optional[np.ndarray], n_levels: int) -> np.ndarray:
    """Get height array, using indices if height_levels not provided."""
    if height_levels is None:
        return np.arange(n_levels, dtype=np.float32)
    return np.asarray(height_levels)

def _apply_nan_mask(data: np.ndarray, threshold: float = -40.0) -> np.ndarray:
    """Apply NaN mask to data below threshold (for radar reflectivity)."""
    masked = data.copy()
    masked[data < threshold] = np.nan
    return masked

def _get_valid_mask(data: np.ndarray, threshold: float = 0.0) -> np.ndarray:
    """Get boolean mask for valid (non-NaN, above threshold) data."""
    return (~np.isnan(data)) & (data > threshold)

def _find_connected_regions(mask: np.ndarray) -> int:
    """Count number of connected regions in a 1D boolean mask."""
    if not np.any(mask):
        return 0
    # Use scipy's label function for 1D connectivity
    labeled, n_features = ndimage.label(mask)
    return n_features

# =============================================================================
# RADAR REFLECTIVITY VARIABLES
# =============================================================================
def max_reflectivity(radar_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Maximum dBZ value in each column."""
    masked_radar = _apply_nan_mask(radar_cube)
    return np.nanmax(masked_radar, axis=0)

def mean_reflectivity(radar_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Mean reflectivity of valid values in each column."""
    masked_radar = _apply_nan_mask(radar_cube)
    return np.nanmean(masked_radar, axis=0)

def integrated_reflectivity(radar_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Total (summed) reflectivity — proxy for hydrometeor loading."""
    masked_radar = _apply_nan_mask(radar_cube)
    return np.nansum(masked_radar, axis=0)

def cloud_top_height(radar_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Height of the highest valid dBZ in each column."""
    heights = _get_heights(height_levels, radar_cube.shape[0])
    valid_mask = _get_valid_mask(radar_cube, threshold=-18.0)

    result = np.full(radar_cube.shape[1:], np.nan)
    for i in range(radar_cube.shape[1]):
        for j in range(radar_cube.shape[2]):
            col_valid = valid_mask[:, i, j]
            if np.any(col_valid):
                # Find highest valid level (maximum index with valid data)
                valid_indices = np.where(col_valid)[0]
                result[i, j] = heights[valid_indices[-1]]
    return result

def cloud_base_height(radar_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Height of the lowest valid dBZ in each column."""
    heights = _get_heights(height_levels, radar_cube.shape[0])
    valid_mask = _get_valid_mask(radar_cube, threshold=-18.0)
    
    result = np.full(radar_cube.shape[1:], np.nan)
    for i in range(radar_cube.shape[1]):
        for j in range(radar_cube.shape[2]):
            col_valid = valid_mask[:, i, j]
            if np.any(col_valid):
                # Find lowest valid level (minimum index with valid data)
                valid_indices = np.where(col_valid)[0]
                result[i, j] = heights[valid_indices[0]]
    return result

def cloud_thickness(radar_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Cloud depth: top - base height."""
    top = cloud_top_height(radar_cube, height_levels)
    base = cloud_base_height(radar_cube, height_levels)
    return top - base

def reflectivity_centroid_height(radar_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Reflectivity-weighted vertical centroid height."""
    heights = _get_heights(height_levels, radar_cube.shape[0])
    masked_radar = _apply_nan_mask(radar_cube)
    
    # Convert dBZ to linear units for proper weighting
    linear_radar = 10**(masked_radar / 10.0)
    
    result = np.full(radar_cube.shape[1:], np.nan)
    for i in range(radar_cube.shape[1]):
        for j in range(radar_cube.shape[2]):
            col_data = linear_radar[:, i, j]
            valid_mask = ~np.isnan(col_data)
            if np.any(valid_mask):
                weights = col_data[valid_mask]
                col_heights = heights[valid_mask]
                result[i, j] = np.sum(weights * col_heights) / np.sum(weights)
    return result

def number_of_layers(radar_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Number of cloud layers (connected reflectivity regions) in each column."""
    valid_mask = _get_valid_mask(radar_cube, threshold=-18.0)
    
    result = np.zeros(radar_cube.shape[1:], dtype=int)
    for i in range(radar_cube.shape[1]):
        for j in range(radar_cube.shape[2]):
            col_mask = valid_mask[:, i, j]
            result[i, j] = _find_connected_regions(col_mask)
    return result

def echo_top_0dBZ(radar_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Height where reflectivity exceeds 10 dBZ."""
    heights = _get_heights(height_levels, radar_cube.shape[0])
    valid_mask = radar_cube > 0.0
    
    result = np.full(radar_cube.shape[1:], np.nan)
    for i in range(radar_cube.shape[1]):
        for j in range(radar_cube.shape[2]):
            col_valid = valid_mask[:, i, j]
            if np.any(col_valid):
                valid_indices = np.where(col_valid)[0]
                result[i, j] = heights[valid_indices[-1]]  # Highest level > 10 dBZ
    return result

def bright_band_height(radar_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Height of melting layer (sharp increase in dBZ)."""
    heights = _get_heights(height_levels, radar_cube.shape[0])
    
    result = np.full(radar_cube.shape[1:], np.nan)
    for i in range(radar_cube.shape[1]):
        for j in range(radar_cube.shape[2]):
            col_data = radar_cube[:, i, j]
            valid_mask = ~np.isnan(col_data) & (col_data > -18)
            
            if np.sum(valid_mask) > 3:  # Need at least 4 points for gradient
                # Compute vertical gradient
                dz = np.diff(heights)
                if len(dz) > 0:
                    avg_dz = np.mean(dz)
                    gradient = np.gradient(col_data, avg_dz)
                    
                    # Find maximum positive gradient (bright band signature)
                    max_grad_idx = np.nanargmax(gradient)
                    result[i, j] = heights[max_grad_idx]
    return result

def radar_precipitation_proxy(radar_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Binary proxy for precipitating columns (dBZ > 0 near base)."""
    heights = _get_heights(height_levels, radar_cube.shape[0])
    
    # Look at bottom 20% of atmosphere for precipitation signature
    bottom_levels = int(0.2 * len(heights))
    bottom_radar = radar_cube[:bottom_levels, :, :]
    
    return np.any(bottom_radar > 0.0, axis=0).astype(int)

def graupel_or_hail_flag(radar_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Flag for dBZ > 5 at upper levels — hail/graupel indication."""
    heights = _get_heights(height_levels, radar_cube.shape[0])
    
    # Look at upper 50% of atmosphere for high reflectivity
    upper_levels = int(0.5 * len(heights))
    upper_radar = radar_cube[upper_levels:, :, :]
    
    return np.any(upper_radar > 5.0, axis=0).astype(int)

# =============================================================================
# ICE WATER CONTENT VARIABLES
# =============================================================================

def max_iwc(iwc_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Maximum IWC value in each column."""
    return np.nanmax(iwc_cube, axis=0)

def mean_iwc(iwc_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Mean IWC in each column."""
    return np.nanmean(iwc_cube, axis=0)

def iwp(iwc_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Ice Water Path (∑ IWC × dz), in g/m² or kg/m²."""
    heights = _get_heights(height_levels, iwc_cube.shape[0])
    
    # Compute layer thickness
    if len(heights) > 1:
        dz = np.diff(heights)
        # Extend to match iwc dimensions (assume layer-centered heights)
        dz = np.concatenate([[dz[0]], dz])
    else:
        dz = np.ones(1)
    
    # Convert to proper units (assume km heights, need m for integration)
    dz_m = dz * 1000  # km to m
    
    # Integrate IWC over height
    iwc_integrated = iwc_cube * dz_m[:, np.newaxis, np.newaxis]
    return np.nansum(iwc_integrated, axis=0)

def iwc_centroid(iwc_cube: np.ndarray, height_levels: Optional[np.ndarray] = None) -> np.ndarray:
    """Height of IWC-weighted centroid."""
    heights = _get_heights(height_levels, iwc_cube.shape[0])
    
    result = np.full(iwc_cube.shape[1:], np.nan)
    for i in range(iwc_cube.shape[1]):
        for j in range(iwc_cube.shape[2]):
            col_data = iwc_cube[:, i, j]
            valid_mask = (~np.isnan(col_data)) & (col_data > 0)
            
            if np.any(valid_mask):
                weights = col_data[valid_mask]
                col_heights = heights[valid_mask]
                result[i, j] = np.sum(weights * col_heights) / np.sum(weights)
    return result

def iwc_max_height(iwc_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Height of the maximum IWC value."""
    heights = _get_heights(height_levels, iwc_cube.shape[0])
    
    result = np.full(iwc_cube.shape[1:], np.nan)
    max_indices = np.nanargmax(iwc_cube, axis=0)
    
    for i in range(iwc_cube.shape[1]):
        for j in range(iwc_cube.shape[2]):
            if not np.isnan(iwc_cube[max_indices[i, j], i, j]):
                result[i, j] = heights[max_indices[i, j]]
    return result

##todo
def iwc_above_8km_fraction(iwc_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Fraction of total IWC above 8 km."""
    heights = _get_heights(height_levels, iwc_cube.shape[0])
    
    # Find levels above 8 km
    high_levels = heights > 8.0
    
    total_iwc = np.nansum(iwc_cube, axis=0)
    high_iwc = np.nansum(iwc_cube[high_levels, :, :], axis=0)
    
    # Avoid division by zero
    result = np.full(iwc_cube.shape[1:], np.nan)
    valid_mask = total_iwc > 0
    result[valid_mask] = high_iwc[valid_mask] / total_iwc[valid_mask]
    
    return result

def gradient_iwc(iwc_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Vertical gradient of IWC."""
    heights = _get_heights(height_levels, iwc_cube.shape[0])
    
    result = np.full(iwc_cube.shape[1:], np.nan)
    
    if len(heights) > 1:
        avg_dz = np.mean(np.diff(heights))
        for i in range(iwc_cube.shape[1]):
            for j in range(iwc_cube.shape[2]):
                col_data = iwc_cube[:, i, j]
                valid_mask = ~np.isnan(col_data)
                if np.sum(valid_mask) > 1:
                    gradient = np.gradient(col_data, avg_dz)
                    result[i, j] = np.nanmean(gradient)
    
    return result

# =============================================================================
# EFFECTIVE RADIUS VARIABLES
# =============================================================================

def mean_re(re_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Mean value of effective radius in each column."""
    return np.nanmean(re_cube, axis=0)

def max_re(re_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Maximum value of effective radius."""
    return np.nanmax(re_cube, axis=0)

def re_max_height(re_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Height at which maximum effective radius occurs."""
    heights = _get_heights(height_levels, re_cube.shape[0])
    
    result = np.full(re_cube.shape[1:], np.nan)
    max_indices = np.nanargmax(re_cube, axis=0)
    
    for i in range(re_cube.shape[1]):
        for j in range(re_cube.shape[2]):
            if not np.isnan(re_cube[max_indices[i, j], i, j]):
                result[i, j] = heights[max_indices[i, j]]
    return result

def gradient_re(re_cube: np.ndarray, height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Vertical gradient of effective radius."""
    heights = _get_heights(height_levels, re_cube.shape[0])
    
    result = np.full(re_cube.shape[1:], np.nan)
    
    if len(heights) > 1:
        avg_dz = np.mean(np.diff(heights))
        for i in range(re_cube.shape[1]):
            for j in range(re_cube.shape[2]):
                col_data = re_cube[:, i, j]
                valid_mask = ~np.isnan(col_data)
                if np.sum(valid_mask) > 1:
                    gradient = np.gradient(col_data, avg_dz)
                    result[i, j] = np.nanmean(gradient)
    
    return result

# =============================================================================
# COMBINED VARIABLES (IWC + RE)
# =============================================================================

def eiwr(iwc_cube: np.ndarray, re_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Effective Ice Water Radius: IWC-weighted effective radius."""
    result = np.full(iwc_cube.shape[1:], np.nan)
    
    for i in range(iwc_cube.shape[1]):
        for j in range(iwc_cube.shape[2]):
            iwc_col = iwc_cube[:, i, j]
            re_col = re_cube[:, i, j]
            
            valid_mask = (~np.isnan(iwc_col)) & (~np.isnan(re_col)) & (iwc_col > 0)
            
            if np.any(valid_mask):
                weights = iwc_col[valid_mask]
                values = re_col[valid_mask]
                result[i, j] = np.sum(weights * values) / np.sum(weights)
    
    return result

def re_weighted_by_iwc(iwc_cube: np.ndarray, re_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Same as EIWR (alias)."""
    return eiwr(iwc_cube, re_cube, **kwargs)

def mass_re_product(iwc_cube: np.ndarray, re_cube: np.ndarray, **kwargs) -> np.ndarray:
    """Pixelwise IWC × re — proxy for ice crystal bulk mass."""
    return np.nansum(iwc_cube * re_cube, axis=0)

def ice_crystal_mode_height(iwc_cube: np.ndarray, re_cube: np.ndarray, 
                          height_levels: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Height where IWC × re peaks."""
    heights = _get_heights(height_levels, iwc_cube.shape[0])
    product = iwc_cube * re_cube
    
    result = np.full(iwc_cube.shape[1:], np.nan)
    max_indices = np.nanargmax(product, axis=0)
    
    for i in range(iwc_cube.shape[1]):
        for j in range(iwc_cube.shape[2]):
            if not np.isnan(product[max_indices[i, j], i, j]):
                result[i, j] = heights[max_indices[i, j]]
    return result

def high_re_low_iwc_flag(iwc_cube: np.ndarray, re_cube: np.ndarray, 
                        re_threshold: float = 50.0, iwc_threshold: float = 0.01, **kwargs) -> np.ndarray:
    """Flag where effective radius is large but IWC is small (growth zones)."""
    high_re = np.any(re_cube > re_threshold, axis=0)
    low_iwc = np.all((iwc_cube < iwc_threshold) | np.isnan(iwc_cube), axis=0)
    return (high_re & low_iwc).astype(int)

# =============================================================================
# MIXED VARIABLES
# =============================================================================

def iwc_without_reflectivity_flag(iwc_cube: np.ndarray, radar_cube: np.ndarray, 
                                dBZ_threshold: float = -30.0, **kwargs) -> np.ndarray:
    """Flag where IWC > 0 but dBZ < threshold — small ice crystals."""
    has_iwc = np.any((iwc_cube > 0) & (~np.isnan(iwc_cube)), axis=0)
    low_radar = np.all((radar_cube < dBZ_threshold) | np.isnan(radar_cube), axis=0)
    return (has_iwc & low_radar).astype(int)

def total_column_condensed_water(iwc_cube: np.ndarray, lwc_cube: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """Sum of all condensed water content in column."""
    total_water = np.nansum(iwc_cube, axis=0)
    
    if lwc_cube is not None:
        total_water += np.nansum(lwc_cube, axis=0)
    
    return total_water

# =============================================================================
# VARIABLE REGISTRY AND DISPATCHER
# =============================================================================

# Registry mapping variable names to functions and requirements
VARIABLE_REGISTRY = {
    # Radar reflectivity variables
    'max_reflectivity': {
        'func': max_reflectivity,
        'requires': ['radar_cube'],
        'description': 'Maximum dBZ value in the column'
    },
    'mean_reflectivity': {
        'func': mean_reflectivity,
        'requires': ['radar_cube'],
        'description': 'Mean reflectivity of valid values'
    },
    'integrated_reflectivity': {
        'func': integrated_reflectivity,
        'requires': ['radar_cube'],
        'description': 'Total (summed) reflectivity — proxy for hydrometeor loading'
    },
    'cloud_top_height': {
        'func': cloud_top_height,
        'requires': ['radar_cube'],
        'description': 'Height of the highest valid dBZ'
    },
    'cloud_base_height': {
        'func': cloud_base_height,
        'requires': ['radar_cube'],
        'description': 'Height of the lowest valid dBZ'
    },
    'cloud_thickness': {
        'func': cloud_thickness,
        'requires': ['radar_cube'],
        'description': 'Cloud depth: top - base'
    },
    'reflectivity_centroid_height': {
        'func': reflectivity_centroid_height,
        'requires': ['radar_cube'],
        'description': 'Reflectivity-weighted vertical centroid'
    },
    'number_of_layers': {
        'func': number_of_layers,
        'requires': ['radar_cube'],
        'description': 'Number of cloud layers (via connected reflectivity regions)'
    },
    'echo_top_0dBZ': {
        'func': echo_top_0dBZ,
        'requires': ['radar_cube'],
        'description': 'Height where reflectivity exceeds 20 dBZ'
    },
    'bright_band_height': {
        'func': bright_band_height,
        'requires': ['radar_cube'],
        'description': 'Height of melting layer (sharp increase in dBZ)'
    },
    'radar_precipitation_proxy': {
        'func': radar_precipitation_proxy,
        'requires': ['radar_cube'],
        'description': 'Binary proxy for precipitating columns'
    },
    'graupel_or_hail_flag': {
        'func': graupel_or_hail_flag,
        'requires': ['radar_cube'],
        'description': 'Flag for dBZ > 45 at upper levels'
    },
    
    # IWC variables
    'max_iwc': {
        'func': max_iwc,
        'requires': ['iwc_cube'],
        'description': 'Maximum IWC value'
    },
    'mean_iwc': {
        'func': mean_iwc,
        'requires': ['iwc_cube'],
        'description': 'Mean IWC in the column'
    },
    'iwp': {
        'func': iwp,
        'requires': ['iwc_cube'],
        'description': 'Ice Water Path (∑ IWC × dz)'
    },
    'iwc_centroid': {
        'func': iwc_centroid,
        'requires': ['iwc_cube'],
        'description': 'Height of IWC-weighted centroid'
    },
    'iwc_max_height': {
        'func': iwc_max_height,
        'requires': ['iwc_cube'],
        'description': 'Height of the maximum IWC value'
    },
    'iwc_above_8km_fraction': {
        'func': iwc_above_8km_fraction,
        'requires': ['iwc_cube'],
        'description': 'Fraction of total IWC above 8 km'
    },
    'gradient_iwc': {
        'func': gradient_iwc,
        'requires': ['iwc_cube'],
        'description': 'Vertical gradient of IWC'
    },
    
    # Effective radius variables
    'mean_re': {
        'func': mean_re,
        'requires': ['re_cube'],
        'description': 'Mean value of re in the column'
    },
    'max_re': {
        'func': max_re,
        'requires': ['re_cube'],
        'description': 'Maximum value of re'
    },
    're_max_height': {
        'func': re_max_height,
        'requires': ['re_cube'],
        'description': 'Height at which max re occurs'
    },
    'gradient_re': {
        'func': gradient_re,
        'requires': ['re_cube'],
        'description': 'Vertical gradient of re'
    },
    
    # Combined variables
    'eiwr': {
        'func': eiwr,
        'requires': ['iwc_cube', 're_cube'],
        'description': 'Effective Ice Water Radius: IWC-weighted effective radius'
    },
    're_weighted_by_iwc': {
        'func': re_weighted_by_iwc,
        'requires': ['iwc_cube', 're_cube'],
        'description': 'Same as EIWR (alias)'
    },
    'mass_re_product': {
        'func': mass_re_product,
        'requires': ['iwc_cube', 're_cube'],
        'description': 'Pixelwise IWC × re — proxy for ice crystal bulk mass'
    },
    'ice_crystal_mode_height': {
        'func': ice_crystal_mode_height,
        'requires': ['iwc_cube', 're_cube'],
        'description': 'Height where IWC × re peaks'
    },
    'high_re_low_iwc_flag': {
        'func': high_re_low_iwc_flag,
        'requires': ['iwc_cube', 're_cube'],
        'description': 'Flag where re is large but IWC is small'
    },
    'iwc_without_reflectivity_flag': {
        'func': iwc_without_reflectivity_flag,
        'requires': ['iwc_cube', 'radar_cube'],
        'description': 'Flag where IWC > 0 but dBZ < threshold'
    },
    'total_column_condensed_water': {
        'func': total_column_condensed_water,
        'requires': ['iwc_cube'],
        'description': 'Sum of all condensed water content in column'
    }
}

def compute_descriptor(variable_name: str, 
                      radar_cube: Optional[np.ndarray] = None,
                      iwc_cube: Optional[np.ndarray] = None, 
                      re_cube: Optional[np.ndarray] = None,
                      height_levels: Optional[np.ndarray] = None,
                      **kwargs) -> np.ndarray:
    """
    Compute a single atmospheric descriptor variable.
    
    Args:
        variable_name: Name of the variable to compute
        radar_cube: Radar reflectivity cube (C, H, W)
        iwc_cube: Ice Water Content cube (C, H, W)
        re_cube: Effective radius cube (C, H, W)
        height_levels: Height levels array (C,)
        **kwargs: Additional parameters for specific variables
        
    Returns:
        Computed descriptor array of shape (H, W)
        
    Raises:
        ValueError: If variable not found or required inputs missing
    """
    if variable_name not in VARIABLE_REGISTRY:
        available = list(VARIABLE_REGISTRY.keys())
        raise ValueError(f"Unknown variable '{variable_name}'. Available: {available}")
    
    var_info = VARIABLE_REGISTRY[variable_name]
    required_inputs = var_info['requires']
    
    # Build input dictionary
    inputs = {'height_levels': height_levels}
    
    # Check required inputs and add to inputs dict
    for req_input in required_inputs:
        if req_input == 'radar_cube' and radar_cube is not None:
            inputs['radar_cube'] = radar_cube
        elif req_input == 'iwc_cube' and iwc_cube is not None:
            inputs['iwc_cube'] = iwc_cube
        elif req_input == 're_cube' and re_cube is not None:
            inputs['re_cube'] = re_cube
        elif req_input in ['radar_cube', 'iwc_cube', 're_cube']:
            raise ValueError(f"Variable '{variable_name}' requires {req_input} but it was not provided")
    
    # Add any additional kwargs
    inputs.update(kwargs)
    
    # Call the function
    return var_info['func'](**inputs)

def compute_multiple_descriptors(variable_names: List[str],
                               radar_cube: Optional[np.ndarray] = None,
                               iwc_cube: Optional[np.ndarray] = None,
                               re_cube: Optional[np.ndarray] = None,
                               height_levels: Optional[np.ndarray] = None,
                               **kwargs) -> Dict[str, np.ndarray]:
    """
    Compute multiple atmospheric descriptors efficiently.
    
    Args:
        variable_names: List of variable names to compute
        radar_cube: Radar reflectivity cube (C, H, W)
        iwc_cube: Ice Water Content cube (C, H, W)
        re_cube: Effective radius cube (C, H, W)
        height_levels: Height levels array (C,)
        **kwargs: Additional parameters
        
    Returns:
        Dictionary mapping variable names to computed arrays
    """
    results = {}
    
    for var_name in variable_names:
        try:
            results[var_name] = compute_descriptor(
                var_name, radar_cube, iwc_cube, re_cube, height_levels, **kwargs
            )
        except Exception as e:
            warnings.warn(f"Failed to compute '{var_name}': {str(e)}")
            results[var_name] = None
    
    return results

def get_variable_info(variable_name: Optional[str] = None) -> Union[Dict, List[str]]:
    """
    Get information about available variables.
    
    Args:
        variable_name: Specific variable to get info for, or None for all
        
    Returns:
        Variable info dict or list of all variable names
    """
    if variable_name is None:
        return list(VARIABLE_REGISTRY.keys())
    
    if variable_name not in VARIABLE_REGISTRY:
        raise ValueError(f"Unknown variable '{variable_name}'")
    
    return VARIABLE_REGISTRY[variable_name]

def validate_inputs(radar_cube: Optional[np.ndarray] = None,
                   iwc_cube: Optional[np.ndarray] = None,
                   re_cube: Optional[np.ndarray] = None,
                   height_levels: Optional[np.ndarray] = None) -> Dict[str, Any]:
    """
    Validate input data cubes for consistency.
    
    Args:
        radar_cube: Radar reflectivity cube
        iwc_cube: Ice Water Content cube  
        re_cube: Effective radius cube
        height_levels: Height levels array
        
    Returns:
        Dictionary with validation results and cube info
    """
    info = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'shapes': {},
        'n_levels': None
    }
    
    cubes = {}
    if radar_cube is not None:
        cubes['radar_cube'] = radar_cube
    if iwc_cube is not None:
        cubes['iwc_cube'] = iwc_cube
    if re_cube is not None:
        cubes['re_cube'] = re_cube
    
    if not cubes:
        info['errors'].append("No input cubes provided")
        info['valid'] = False
        return info
    
    # Check shapes are consistent
    shapes = {name: cube.shape for name, cube in cubes.items()}
    info['shapes'] = shapes
    
    reference_shape = list(shapes.values())[0]
    info['n_levels'] = reference_shape[0]
    
    for name, shape in shapes.items():
        if shape != reference_shape:
            info['errors'].append(f"Shape mismatch: {name} has shape {shape}, expected {reference_shape}")
            info['valid'] = False
    
    # Check height levels if provided
    if height_levels is not None:
        if len(height_levels) != reference_shape[0]:
            info['errors'].append(f"Height levels length ({len(height_levels)}) doesn't match vertical dimension ({reference_shape[0]})")
            info['valid'] = False
        
        # Check if heights are monotonic
        if len(height_levels) > 1:
            if not (np.all(np.diff(height_levels) > 0) or np.all(np.diff(height_levels) < 0)):
                info['warnings'].append("Height levels are not monotonic")
    
    # Check for reasonable data ranges
    if radar_cube is not None:
        radar_range = (np.nanmin(radar_cube), np.nanmax(radar_cube))
        if radar_range[0] < -80 or radar_range[1] > 80:
            info['warnings'].append(f"Radar reflectivity range {radar_range} seems unusual (typical: -40 to 60 dBZ)")
    
    if iwc_cube is not None:
        iwc_range = (np.nanmin(iwc_cube), np.nanmax(iwc_cube))
        if iwc_range[0] < 0:
            info['warnings'].append("Negative IWC values found")
        if iwc_range[1] > 10:
            info['warnings'].append(f"Very high IWC values found (max: {iwc_range[1]})")
    
    if re_cube is not None:
        re_range = (np.nanmin(re_cube), np.nanmax(re_cube))
        if re_range[0] < 0:
            info['warnings'].append("Negative effective radius values found")
        if re_range[1] > 1000:
            info['warnings'].append(f"Very large effective radius values found (max: {re_range[1]})")
    
    return info

# =============================================================================
# EXAMPLE USAGE AND TESTING
# =============================================================================

def create_example_data(n_levels: int = 50, n_lat: int = 20, n_lon: int = 30) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Create example atmospheric data for testing.
    
    Returns:
        Tuple of (radar_cube, iwc_cube, re_cube, height_levels)
    """
    # Height levels (km)
    height_levels = np.linspace(0, 20, n_levels)
    
    # Create realistic-looking radar reflectivity
    np.random.seed(42)  # For reproducibility
    radar_cube = np.random.normal(-35, 15, (n_levels, n_lat, n_lon))
    
    # Add some cloud layers
    for i in range(n_lat):
        for j in range(n_lon):
            # Random cloud base and top
            cloud_base = np.random.randint(5, 25)
            cloud_top = cloud_base + np.random.randint(5, 20)
            if cloud_top < n_levels:
                # Add cloud signature
                radar_cube[cloud_base:cloud_top, i, j] += np.random.normal(20, 10, cloud_top - cloud_base)
    
    # Clip to reasonable range
    radar_cube = np.clip(radar_cube, -50, 60)
    radar_cube[radar_cube < -40] = np.nan  # Below detection threshold
    
    # Create IWC data (correlated with radar)
    iwc_cube = np.zeros_like(radar_cube)
    valid_radar = ~np.isnan(radar_cube)
    # Simple relationship: higher reflectivity -> higher IWC
    iwc_cube[valid_radar] = np.maximum(0, (radar_cube[valid_radar] + 30) / 100 * np.random.exponential(0.1, np.sum(valid_radar)))
    iwc_cube[~valid_radar] = np.nan
    
    # Create effective radius data
    re_cube = np.full_like(radar_cube, np.nan)
    re_cube[valid_radar] = np.random.gamma(2, 15)  # Gamma distribution, typical ice crystal sizes
    re_cube = np.clip(re_cube, 1, 200)  # Reasonable range for ice crystals
    
    return radar_cube, iwc_cube, re_cube, height_levels

def run_example():
    """Run example computation of all descriptors."""
    print("Creating example atmospheric data...")
    radar_cube, iwc_cube, re_cube, height_levels = create_example_data()
    
    print(f"Data shapes: {radar_cube.shape}")
    print(f"Height range: {height_levels[0]:.1f} - {height_levels[-1]:.1f} km")
    
    # Validate inputs
    validation = validate_inputs(radar_cube, iwc_cube, re_cube, height_levels)
    print(f"\nValidation: {'PASSED' if validation['valid'] else 'FAILED'}")
    if validation['warnings']:
        print("Warnings:", validation['warnings'])
    if validation['errors']:
        print("Errors:", validation['errors'])
    
    # Get list of all available variables
    all_variables = get_variable_info()
    print(f"\nComputing {len(all_variables)} descriptors...")
    
    # Compute all descriptors
    results = compute_multiple_descriptors(
        all_variables,
        radar_cube=radar_cube,
        iwc_cube=iwc_cube,
        re_cube=re_cube,
        height_levels=height_levels
    )
    
    # Print summary of results
    print("\nResults summary:")
    print("-" * 60)
    for var_name, result in results.items():
        if result is not None:
            var_info = get_variable_info(var_name)
            mean_val = np.nanmean(result)
            print(f"{var_name:30s} | Mean: {mean_val:8.3f} | {var_info['description']}")
        else:
            print(f"{var_name:30s} | FAILED")
    
    return results

if __name__ == "__main__":
    # Run example
    example_results = run_example()
    
    # Example of computing individual variables
    print("\n" + "="*60)
    print("Individual variable computation example:")
    
    radar_cube, iwc_cube, re_cube, height_levels = create_example_data(20, 5, 5)
    
    # Compute cloud top height for a single column
    cloud_tops = compute_descriptor('cloud_top_height', radar_cube=radar_cube, height_levels=height_levels)
    print(f"Cloud top heights (km):\n{cloud_tops}")
    
    # Compute IWP
    iwp_values = compute_descriptor('iwp', iwc_cube=iwc_cube, height_levels=height_levels)
    print(f"\nIce Water Path (g/m²):\n{iwp_values}")
    
    # Compute combined variable
    eiwr_values = compute_descriptor('eiwr', iwc_cube=iwc_cube, re_cube=re_cube)
    print(f"\nEffective Ice Water Radius:\n{eiwr_values}")