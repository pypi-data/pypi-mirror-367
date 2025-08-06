import ee
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def get_track_by_sid(sid: str) -> gpd.GeoDataFrame:
    """
    Fetches the track (points) of a storm from IBTrACS dataset given a SID.

    Parameters:
        sid (str): Storm Identifier (SID) as defined in NOAA/IBTrACS/v4

    Returns:
        geopandas.GeoDataFrame: Track points with timestamp and geometry.
    """
    # Filtra la colección IBTrACS por SID
    collection = ee.FeatureCollection("NOAA/IBTrACS/v4").filter(ee.Filter.eq('SID', sid))

    # Selecciona los campos que necesitamos
    collection = collection.select(['SID', 'ISO_TIME'])

    # Obtiene los datos como GeoJSON
    features = collection.getInfo()['features']

    # Extrae datos y geometría
    data = []
    for f in features:
        props = f['properties']
        coords = f['geometry']['coordinates']
        data.append({
            'SID': props.get('SID'),
            'ISO_TIME': props.get('ISO_TIME'),
            'geometry': Point(coords)
        })

    # Crea GeoDataFrame
    df = pd.DataFrame(data)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
    gdf['ISO_TIME'] = pd.to_datetime(gdf['ISO_TIME'])
    gdf = gdf.sort_values(by="ISO_TIME")
    gdf = gdf.reset_index(drop=True)

    # get the bbox of the track
    bbox = gdf.total_bounds.tolist()  # [minx, miny, maxx, maxy]

    # get the date range
    start_date = gdf['ISO_TIME'].min().strftime('%Y-%m-%dT%H:%M:%S')
    end_date = gdf['ISO_TIME'].max().strftime('%Y-%m-%dT%H:%M:%S')
    time_range = [start_date, end_date]

    return gdf, bbox, time_range
