import numpy as np
from tqdm import tqdm
import numpy as np
import itertools


def getimportance(chunk=512, overlap=128, border_position='none'):
    """
    Generate importance mask for overlapping chunks in semantic segmentation.
    Uses cosine decay for smoother blending than linear decay.
    
    Args:
        chunk (int): Size of the square chunk (default: 512)
        overlap (int): Size of overlap region (default: 128)
        border_position (str): Position of border - 'top', 'bottom', 'left', 'right', 
                              'top-left', 'top-right', 'bottom-left', 'bottom-right', 'none'
    
    Returns:
        numpy.ndarray: 2D importance mask with values between 0 and 1
    """
    
    def cosine_decay(x, start, end, reverse=False):
        """
        Create smooth cosine decay from start to end position.
        More gradual than linear, less sharp than sigmoid.
        
        Args:
            x (array): Position array
            start (int): Start position of decay
            end (int): End position of decay  
            reverse (bool): If True, decay from 1 to 0, else from 0 to 1
        """
        # Normalize to [0, 1] range
        normalized = (x - start) / (end - start)
        normalized = np.clip(normalized, 0, 1)
        
        # Apply cosine function for smooth transition
        # cos(π * (1 - x)) maps [0,1] -> [0,1] smoothly
        cosine = 0.5 * (1 + np.cos(np.pi * (1 - normalized)))
        
        if reverse:
            cosine = 1 - cosine
            
        return cosine
    
    # Create coordinate arrays
    y_coords, x_coords = np.meshgrid(np.arange(chunk), np.arange(chunk), indexing='ij')
    
    # Initialize importance mask with ones
    importance = np.ones((chunk, chunk), dtype=np.float32)
    
    # Calculate decay boundaries
    decay_start = chunk - overlap
    
    # Handle different border positions
    if border_position == 'none':
        # Internal chunk: decay on both sides of both axes
        # X direction: decay from 0→1 (left) and 1→0 (right)
        left_mask = x_coords < overlap
        importance[left_mask] *= cosine_decay(x_coords[left_mask], 0, overlap, reverse=False)
        
        right_mask = x_coords >= decay_start
        importance[right_mask] *= cosine_decay(x_coords[right_mask], decay_start, chunk, reverse=True)
        
        # Y direction: decay from 0→1 (top) and 1→0 (bottom)
        top_mask = y_coords < overlap
        importance[top_mask] *= cosine_decay(y_coords[top_mask], 0, overlap, reverse=False)
        
        bottom_mask = y_coords >= decay_start
        importance[bottom_mask] *= cosine_decay(y_coords[bottom_mask], decay_start, chunk, reverse=True)
        
    else:
        # Border chunk: decay only on the inner side (towards image center)
        
        # Handle X direction based on border position
        if 'left' in border_position:
            # At left border: decay only from right (decay_start to chunk)
            right_mask = x_coords >= decay_start
            importance[right_mask] *= cosine_decay(x_coords[right_mask], decay_start, chunk, reverse=True)
            
        elif 'right' in border_position:
            # At right border: decay only from left (0 to overlap)
            left_mask = x_coords < overlap
            importance[left_mask] *= cosine_decay(x_coords[left_mask], 0, overlap, reverse=False)
            
        else:
            # Not at x border: decay on both sides
            left_mask = x_coords < overlap
            importance[left_mask] *= cosine_decay(x_coords[left_mask], 0, overlap, reverse=False)
            
            right_mask = x_coords >= decay_start
            importance[right_mask] *= cosine_decay(x_coords[right_mask], decay_start, chunk, reverse=True)
        
        # Handle Y direction based on border position
        if 'top' in border_position:
            # At top border: decay only from bottom (decay_start to chunk)
            bottom_mask = y_coords >= decay_start
            importance[bottom_mask] *= cosine_decay(y_coords[bottom_mask], decay_start, chunk, reverse=True)
            
        elif 'bottom' in border_position:
            # At bottom border: decay only from top (0 to overlap)
            top_mask = y_coords < overlap
            importance[top_mask] *= cosine_decay(y_coords[top_mask], 0, overlap, reverse=False)
            
        else:
            # Not at y border: decay on both sides
            top_mask = y_coords < overlap
            importance[top_mask] *= cosine_decay(y_coords[top_mask], 0, overlap, reverse=False)
            
            bottom_mask = y_coords >= decay_start
            importance[bottom_mask] *= cosine_decay(y_coords[bottom_mask], decay_start, chunk, reverse=True)
    
    return importance

def generate_overlapping_chunks(image_dimensions, chunk_size, overlap=0):
    """
    Generate overlapping chunks for processing large images with semantic segmentation.
    
    This function creates a grid of overlapping chunks that cover the entire image,
    ensuring proper boundary handling and returning border position information
    for importance mask generation.
    
    Args:
        image_dimensions (tuple): Dimensions of the image (height, width).
        chunk_size (int): Size of square chunks to generate.
        overlap (int, optional): Overlap size between adjacent chunks. Defaults to 0.
    
    Returns:
        list: List of chunk information dictionaries containing:
            - 'coordinates': (y, x) top-left coordinates of the chunk
            - 'border_position': Position relative to image borders 
            - 'chunk_size': Size of the chunk
            - 'overlap': Overlap size used
    """
    image_height, image_width = image_dimensions
    
    # Handle case where chunk is larger than image
    if chunk_size > max(image_width, image_height):
        return [{
            'coordinates': (0, 0),
            'border_position': _determine_border_position(0, 0, image_dimensions, chunk_size),
            'chunk_size': chunk_size,
            'overlap': overlap
        }]
    
    # Calculate step size accounting for overlap
    step_y = chunk_size - overlap
    step_x = chunk_size - overlap
    
    # Generate grid of potential chunk starting positions
    potential_positions = list(itertools.product(
        range(0, image_height, step_y), 
        range(0, image_width, step_x)
    ))
    
    # Adjust edge chunks to ensure they fit within image boundaries
    adjusted_chunks = _adjust_boundary_chunks(
        chunk_positions=potential_positions, 
        image_dimensions=image_dimensions, 
        chunk_size=chunk_size
    )
    
    # Create detailed chunk information with border position detection
    chunks_info = []
    for y, x in adjusted_chunks:
        chunk_info = {
            'coordinates': (y, x),
            'border_position': _determine_border_position(y, x, image_dimensions, chunk_size),
            'chunk_size': chunk_size,
            'overlap': overlap
        }
        chunks_info.append(chunk_info)
    
    return chunks_info


def _adjust_boundary_chunks(chunk_positions, image_dimensions, chunk_size):
    """
    Adjust chunk positions to ensure they stay within image boundaries.
    
    Args:
        chunk_positions (list): List of initial chunk positions (y, x).
        image_dimensions (tuple): Image dimensions (height, width).
        chunk_size (int): Size of square chunks.
    
    Returns:
        list: List of adjusted chunk positions that fit within boundaries.
    """
    image_height, image_width = image_dimensions
    adjusted_positions = []
    
    for y, x in chunk_positions:
        # Adjust Y coordinate if chunk extends beyond bottom boundary
        if y + chunk_size > image_height:
            y = max(image_height - chunk_size, 0)
        
        # Adjust X coordinate if chunk extends beyond right boundary  
        if x + chunk_size > image_width:
            x = max(image_width - chunk_size, 0)
        
        adjusted_positions.append((y, x))
    
    return adjusted_positions


def _determine_border_position(chunk_y, chunk_x, image_dimensions, chunk_size):
    """
    Determine the border position of a chunk relative to the image boundaries.
    
    Args:
        chunk_y (int): Y coordinate of chunk top-left corner.
        chunk_x (int): X coordinate of chunk top-left corner.
        image_dimensions (tuple): Image dimensions (height, width).
        chunk_size (int): Size of the square chunk.
    
    Returns:
        str: Border position string for importance mask generation.
    """
    image_height, image_width = image_dimensions
    
    # Determine if chunk touches each boundary
    at_top = chunk_y == 0
    at_bottom = chunk_y + chunk_size >= image_height
    at_left = chunk_x == 0  
    at_right = chunk_x + chunk_size >= image_width
    
    # Determine border position based on which boundaries are touched
    if at_top and at_left:
        return 'top-left'
    elif at_top and at_right:
        return 'top-right'
    elif at_bottom and at_left:
        return 'bottom-left'
    elif at_bottom and at_right:
        return 'bottom-right'
    elif at_top:
        return 'top'
    elif at_bottom:
        return 'bottom'
    elif at_left:
        return 'left'
    elif at_right:
        return 'right'
    else:
        return 'none'


def predict_large(
    X, model,
    overlap: int = 32,
    chunk_size: int = 128,
    output_num_channels: int = 4,
    device: str = 'cuda'
):
    """
    Process large images using overlapping chunks with seamless blending.
    
    This function handles large images by:
    1. Dividing them into overlapping chunks
    2. Processing each chunk through the model
    3. Seamlessly blending results using importance masks with proper normalization
    4. Supporting non-square images and different upscaling factors
    
    Args:
        X (torch.Tensor): Input tensor of shape (C, H, W) where:
                         C = channels, H = height, W = width
        model (torch.nn.Module): PyTorch model that processes image chunks
        overlap (int): Overlap size between adjacent chunks in pixels
        chunk_size (int): Size of square chunks to process
        device (str): Device to run inference on ('cuda' or 'cpu')
    
    Returns:
        torch.Tensor: Processed output tensor with potentially different spatial dimensions
                     depending on the model's upscaling factor
    
    Notes:
        - Automatically handles non-square images (e.g., 512x1024)
        - Determines upscaling factor from first chunk processing
        - Uses importance masks for seamless blending in overlap regions
        - Properly normalizes overlapping regions to prevent brightness artifacts
        - Memory efficient - processes one chunk at a time
    """
    try:
        import torch
        import torch.nn.functional as F
    except ImportError:
        raise ImportError("Please install PyTorch to use this function.")
    
    # Validate input tensor dimensions
    if len(X.shape) != 3:
        raise ValueError(f"Input tensor must have 3 dimensions (C, H, W), got {X.shape}")
    
    # Extract image dimensions (note: X is in C, H, W format)
    num_channels, img_height, img_width = X.shape
    
    # Generate overlapping chunks with metadata
    chunk_metadata_list = generate_overlapping_chunks(
        image_dimensions=(img_height, img_width),  # (height, width)
        chunk_size=chunk_size,
        overlap=overlap,
    )
    
    # Pre-compute all importance masks for different border positions
    importance_masks = {}
    for border_pos in ['top-left', 'top-right', 'bottom-left', 'bottom-right',
                      'left', 'right', 'top', 'bottom', 'none']:
        importance_masks[border_pos] = getimportance(
            chunk=chunk_size,
            overlap=overlap,
            border_position=border_pos,
        )

    # Initialize output tensor and normalization map (will be created after first chunk processing)
    output = None
    normalization_map = None
    upscale_factor = None
    
    # Process each chunk
    for chunk_idx, metadata in enumerate(tqdm(chunk_metadata_list, desc="Processing chunks")):

        # Extract chunk coordinates and border position
        chunk_y, chunk_x = metadata["coordinates"]  # (row, col) coordinates
        border_position = metadata["border_position"]
        
        # Extract chunk from input image
        # Note: X is (C, H, W), so we slice [channels, y:y+size, x:x+size]
        chunk_end_y = chunk_y + chunk_size
        chunk_end_x = chunk_x + chunk_size
        
        input_chunk = X[:, chunk_y:chunk_end_y, chunk_x:chunk_end_x]
        
        # Move chunk to processing device and add batch dimension
        input_chunk = input_chunk.to(device).unsqueeze(0)  # Add batch dimension: (1, C, H, W)
        
        # Process chunk through model
        with torch.no_grad():
            processed_chunk = model(input_chunk)
        
        # Remove batch dimension and move to CPU
        processed_chunk = processed_chunk.squeeze(0).detach().cpu()  # (C, H, W)
        
        # Determine upscaling factor from first chunk
        if upscale_factor is None:
            upscale_factor = processed_chunk.shape[-1] // chunk_size
            
            # Validate that the model output is cleanly divisible by input chunk size
            processed_height, processed_width = processed_chunk.shape[-2:]
            if processed_height % chunk_size != 0 or processed_width % chunk_size != 0:
                raise ValueError(
                    f"Model output size ({processed_height}x{processed_width}) is not evenly "
                    f"divisible by chunk_size ({chunk_size}). This will cause misalignment "
                    f"in the reconstructed image. Consider adjusting chunk_size or using a "
                    f"model with predictable scaling."
                )


            # Initialize output tensor and normalization map based on upscaled dimensions
            output_height = img_height * upscale_factor
            output_width = img_width * upscale_factor
            output = torch.zeros(
                (output_num_channels, output_height, output_width),
                dtype=processed_chunk.dtype,
                device='cpu'
            )
            # Normalization map tracks the sum of importance weights for each pixel
            normalization_map = torch.zeros(
                (output_height, output_width),
                dtype=torch.float32,
                device='cpu'
            )
        
        # Apply importance mask for seamless blending
        importance_mask = importance_masks[border_position]
        
        # Handle different chunk sizes due to upscaling
        mask_upscaled = torch.from_numpy(importance_mask).float()
        if upscale_factor > 1:
            # Upscale the importance mask to match processed chunk size
            mask_upscaled = torch.nn.functional.interpolate(
                mask_upscaled.unsqueeze(0).unsqueeze(0),  # Add batch and channel dims
                size=(processed_chunk.shape[-2], processed_chunk.shape[-1]),
                mode='bilinear',
                antialias=True
            ).squeeze(0).squeeze(0)  # Remove added dimensions
        
        # Apply mask to processed chunk
        processed_chunk = processed_chunk * mask_upscaled.unsqueeze(0)  # Broadcast across channels        
                
        # Calculate output coordinates
        output_y = chunk_y * upscale_factor
        output_x = chunk_x * upscale_factor
        output_end_y = min(output_y + processed_chunk.shape[-2], output_height)
        output_end_x = min(output_x + processed_chunk.shape[-1], output_width)
        
        # Handle potential size mismatches due to edge chunks
        actual_output_h = output_end_y - output_y
        actual_output_w = output_end_x - output_x
        
        chunk_to_add = processed_chunk[:, :actual_output_h, :actual_output_w]
        mask_to_add = mask_upscaled[:actual_output_h, :actual_output_w]
        
        # Accumulate both the processed chunk and the importance weights
        output[:, output_y:output_end_y, output_x:output_end_x] += chunk_to_add
        normalization_map[output_y:output_end_y, output_x:output_end_x] += mask_to_add
    
    # Normalize the output by dividing by the accumulated importance weights
    # Add small epsilon to avoid division by zero
    eps = 1e-8
    normalization_map = torch.clamp(normalization_map, min=eps)
    
    # Apply normalization across all channels
    for c in range(output_num_channels):
        output[c] = output[c] / normalization_map
    
    return output