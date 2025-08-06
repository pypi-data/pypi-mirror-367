import pathlib
import urllib.request
import cloud3d.ibtracs_utils

from cloud3d.goes import get_GOES, download
from cloud3d.model_utils import inverse_min_max_normalize, min_max_normalize
from cloud3d.predict import predict_large
from cloud3d.cloudsat_products import compute_descriptor, compute_multiple_descriptors, get_variable_info


def load(model_url_or_name: str, model_path: str = None, device: str = "cpu"):
    """
    Download and load a TorchScript model from a URL or local file.

    Args:
        model_url_or_name (str): URL to the .jit.pt model or local filename.
        model_path (str, optional): Directory to store/load the model. Defaults to './models'.

    Returns:
        torch.jit.ScriptModule: The loaded model.
    """

    # Check if PyTorch is installed
    try:
        import torch
    except ImportError:
        raise ImportError("Please install PyTorch to use this function.")

    model_dir = pathlib.Path(model_path or "models")
    model_dir.mkdir(parents=True, exist_ok=True)

    if model_url_or_name.startswith(("http://", "https://")):
        filename = model_url_or_name.rsplit("/", 1)[-1]
        local_path = model_dir / filename

        if not local_path.exists():
            print(f"Downloading model from {model_url_or_name} to {local_path}")
            urllib.request.urlretrieve(model_url_or_name, local_path)
            print("Download complete.")
    else:
        local_path = model_dir / model_url_or_name
        if not local_path.exists():
            raise FileNotFoundError(f"Model not found at {local_path}")

    print(f"Loading model from {local_path}")
    model = torch.jit.load(str(local_path), map_location=device)        
    for param in model.parameters():
        param.requires_grad = False
    model.eval()
    return model