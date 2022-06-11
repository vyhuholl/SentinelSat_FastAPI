import logging
import os
from shutil import rmtree
from typing import Dict
from zipfile import ZipFile

from celery import Celery
from dotenv import load_dotenv
from sentinelsat import SentinelAPI, geojson_to_wkt

from db.crud import CRUD
from file_structure import FileStructure
from ndvi import calculate_image
from sentinel_client import SentinelClient
from utils import find_base_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - '
           '[%(levelname)s] - '
           '%(name)s - '
           '(%(filename)s).%(funcName)s(%(lineno)d) - '
           '%(message)s',
)

load_dotenv()

app = Celery('background_tasks', broker=os.environ.get('BROKER_URI'))

api = SentinelAPI(
    os.environ.get('SENTINEL_USERNAME'), os.environ.get('SENTINEL_PASSWORD'),
    'https://apihub.copernicus.eu/apihub'
)

client = SentinelClient(api)
crud = CRUD()

file_structure = FileStructure(os.environ.get(
    'FILESYSTEM_BASE_PATH', default='STORAGE'
    ))


@app.task()
def get_sentinel_data(field_id: int, geojson: Dict[str, str | Dict]) -> None:
    '''
    Downloads zipped field data from API and unzips it.

    Parameters:
        field_id: int
        geojson: Dict[str, str | Dict]

    Returns:
        None
    '''
    try:
        crud.change_status(field_id, 'Started download')
        zipped_dir = file_structure.get_path_to_satellite_data(field_id)

        zipped_path = client.get_data(
            geojson_to_wkt(geojson), output_dir=zipped_dir
            )

        with ZipFile(zipped_path, 'r') as zip_file:
            zip_file.extractall(
                file_structure.get_path_to_satellite_data(
                    field_id, zipped=False
                    )
                )

        rmtree(zipped_dir)
        crud.change_status(field_id, 'Finished download')
    except Exception as e:
        crud.change_status(field_id, 'Error on download')
        raise e


@app.task
def calculate_ndvi(field_id: int) -> None:
    '''
    Calculates NDVI and creates NDVI images (TIF and PNG) for the field.

    Parameters:
        field_id: int

    Returns:
        None
    '''
    try:
        crud.change_status(field_id, 'Started calculation')

        path = file_structure.get_path_to_satellite_data(
            field_id, zipped=False
            )

        base_path = find_base_path(path)

        nir = os.path.join(
            base_path[0],
            [elem for elem in base_path[2] if 'B08' in elem][0]
            )

        red = os.path.join(
            base_path[0],
            [elem for elem in base_path[2] if 'B04' in elem][0]
            )

        tif = file_structure.get_ndvi_path(field_id)
        png = file_structure.get_ndvi_path(field_id, is_png=True)
        geojson = crud.get_field(field_id)
        logging.info(f'Started NDVI calculation for the field {field_id}')
        calculate_image(nir, red, tif, png, geojson)
        crud.save_ndvi_path(field_id, tif)
        crud.save_ndvi_path(field_id, png, is_png=True)
        crud.change_status(field_id, 'Finished calculation')
    except Exception as e:
        crud.change_status(field_id, 'Error on calculation')
        raise e
