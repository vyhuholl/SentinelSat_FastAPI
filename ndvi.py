import logging
from typing import Dict

import rasterio
from geopandas import GeoDataFrame
from matplotlib import image
from rasterio.mask import mask

logger = logging.getLogger()


def calculate_image(
    nir_path: str, red_path: str, tif_path: str, png_path: str,
    geojson: Dict[str, str | Dict]
        ) -> None:
    '''
    Calculates NDVI by the formula NDVI = (NIR - red) / (NIR + red)
    and stores the resulting NDVI image to the file system
    (in PNG and TIF formats).

    Parameters:
        nir: str
        red: str
        tif_path: str
        png_path: str,
        geojson: Dict[str, str | Dict]

    Returns:
        None
    '''
    logger.info('Transforming coordinates...')

    crs = GeoDataFrame.from_features(
        geojson['features'], crs='EPSG:4326'
        ).to_crs(epsg=32637).geometry

    logger.info('Opening and cropping b4 image...')

    with rasterio.open(red_path) as img:
        red, _, _ = mask(img, crs, crop=True)

    logger.info('Opening and cropping b8 image...')

    with rasterio.open(nir_path) as img:
        nir, _, _ = mask(img, crs, crop=True)

    logger.info('Calculating NDVI...')
    ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)

    logger.info('Saving TIF file...')

    with rasterio.open(tif_path) as img:
        img.write(ndvi.astype(rasterio.float32))

    logger.info('Saving PNG file...')
    image.imsave(png_path, ndvi, cmap='RdYlGn', vmin=0, vmax=1)
