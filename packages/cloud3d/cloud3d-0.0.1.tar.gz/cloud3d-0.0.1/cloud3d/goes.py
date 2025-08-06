import ee
from cloud3d.constant import GOES_METADATA
from concurrent.futures import ThreadPoolExecutor
import pathlib

GOEST_DEFAULT_BANDS = ["CMI_C01", "CMI_C02", "CMI_C03", "CMI_C05", "CMI_C07", "CMI_C08", "CMI_C10", "CMI_C11", "CMI_C12", "CMI_C14", "CMI_C15", "CMI_C16"]

def apply_scale_and_offset(image):
    """Apply scale and offset to GOES-16 CMI_Cxx bands."""
    bands = []
    for i in range(1, 17):
        band = f'CMI_C{str(i).zfill(2)}'
        scale = GOES_METADATA[band]['scale']
        offset = GOES_METADATA[band]['offset']
        corrected = image.select(band).float().multiply(scale).add(offset).rename(band)
        bands.append(corrected)
    return ee.Image(bands).copyProperties(image, image.propertyNames())


def download(manifests, output_folder, max_workers=8):
    """
    Downloads an image from the manifest and saves it to a local directory.

    Parameters:
        manifest (dict): The manifest containing the image export request.
        output_folder (str): The folder where the images will be saved.
    """
    # Create a request to compute pixels
    fn_request = lambda req: ee.data.computePixels(req)

    # Create a folder with the SID name
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fn_request, request): image_id for image_id, request in manifests.items()}
        for future in futures:
            image_id = futures[future]
            try:
                result = future.result()
                with open(f"{output_folder}/{image_id}.tif", "wb") as f:
                    f.write(result)
                print(f"Downloaded {image_id} successfully.")
            except Exception as e:
                print(f"Failed to download {image_id}: {e}")
        
    return [f"{output_folder}/{image_id}.tif" for image_id in manifests.keys()]


def get_GOES(
    bbox: list,
    time_range: list,
    resolution: int = 2000,
    bands: list = GOEST_DEFAULT_BANDS
) -> dict:
    """
    Fetches GOES-16 images for a given bounding box and time range.

    Parameters:
        bbox (list): Bounding box in the format [minx, miny, maxx, maxy].
        time_range (list): Time range in the format [start_time, end_time].

    Returns:
        ee.ImageCollection: Collection of GOES-16 images.
    """
    
    # Define the region and resolution
    goes = ee.ImageCollection("NOAA/GOES/16/MCMIPF") \
        .filterBounds(ee.Geometry.Rectangle(bbox)) \
        .filterDate(time_range[0], time_range[1])
    
    # Gest the list of all images ids
    image_ids = goes.aggregate_array("system:id").getInfo()
    

    # Iterate over all the rows and add the manifest
    container = {}
    for idx, image_id in enumerate(image_ids):
        # Create a ee.Image object
        img = ee.Image(image_id)

        # Apply scale and offset
        img_corrected = apply_scale_and_offset(img)

        # Create the manifest entry
        # Build export request
        request = {
            "expression": ee.Image(img_corrected),
            "fileFormat": "GeoTIFF",
            "bandIds": bands,
            "grid": {
                "affineTransform": {
                    "scaleX": resolution/111320,  # Convert meters to degrees
                    "shearX": 0,
                    "translateX": bbox[0],
                    "shearY": 0,
                    "scaleY": resolution/111320,
                    "translateY": bbox[1]
                },
                'dimensions': {
                    'width': int((bbox[2] - bbox[0]) / resolution * 111320),
                    'height': int((bbox[3] - bbox[1]) / resolution * 111320)
                },
                "crsCode": "EPSG:4326"
            }
        }

        # Compute pixels
        container[pathlib.Path(image_id).stem] = request
    
    return container
