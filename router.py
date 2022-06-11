import logging
import os
from shutil import rmtree

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse
from geojson_pydantic import FeatureCollection

from background_tasks import calculate_ndvi, get_sentinel_data
from db.crud import CRUD
from file_structure import FileStructure

load_dotenv()

router = APIRouter(
    prefix='/field',
    tags=['field'],
    )

file_structure = FileStructure(os.environ.get(
    'FILESYSTEM_BASE_PATH', default='STORAGE'
    ))

logger = logging.getLogger()


@router.post('/')
def add_field(
    field: FeatureCollection, conn: CRUD = Depends(CRUD)
        ) -> JSONResponse:
    '''
    Adds field (in GeoJSON format) to the database.

    Parameters:
        field: FeatureCollection
        conn: CRUD

    Returns:
        JSONResponse
    '''
    logger.info('Adding a new field to the database...')
    field_id = conn.add_field(field)
    logger.info(f'Added field {field_id} to the database')

    return JSONResponse({
        'field_id': field_id
    })


@router.post('/image')
def download_image(
    field_id: int, conn: CRUD = Depends(CRUD),
    max_days: int = 1, max_cloud_cover: int = 30
        ) -> JSONResponse:
    '''
    Downloads satellite image for the field.

    Parameters:
        field_id: int
        conn: CRUD
        max_days: int
        max_cloud_cover: int

    Returns:
        JSONResponse
    '''
    logger.info(f'Downloading satellite image for the field {field_id}...')
    geojson = conn.get_field(field_id)
    get_sentinel_data.delay(field_id, geojson, max_days, max_cloud_cover)
    logger.info(f'Downloaded satellite image for the field {field_id}')

    return JSONResponse({
        'status': 'Started download',
        'message': 'Started satellite data download.'
    })


@router.post('/ndvi')
def create_ndvi(
    field_id: int, is_png: bool = False, conn: CRUD = Depends(CRUD)
        ) -> JSONResponse:
    '''
    Calculates NDVI for the field and saves NDVI image.

    Parameters:
        field_id: int
        is_png: bool
        conn: CRUD

    Returns:
        JSONResponse
    '''
    messages = {
        'Started download': 'The data is not downloaded yet',
        'Error on download': 'An error happened during image download.',
        'Finished download': 'Started NDVI calculation.'
    }

    status = conn.get_status(field_id)

    if status == 'Finished download':
        calculate_ndvi.delay(field_id)

    return JSONResponse({
        'status': status,
        'message': messages[status]
    })


@router.get('/ndvi')
def get_ndvi(
    field_id: int, is_png: bool = False, conn: CRUD = Depends(CRUD)
        ) -> FileResponse | JSONResponse:
    '''
    Returns NDVI image by the field id.

    Parameters:
        field_id: int
        is_png: bool
        conn: CRUD

    Returns:
        FileResponse | JSONResponse
    '''
    messages = {
        'Created': 'Image download has not started yet',
        'Started download': 'Image download has not finished yet',
        'Error on download': 'An error happened during image download.',
        'Started calculation': 'NDVI is not calculated yet',
        'Error on calculation': 'An error happened during NDVI calculation.',
    }

    status = conn.get_status(field_id)

    if status == 'Finished calculation':
        return FileResponse(
            file_structure.get_ndvi_path(field_id, is_png=is_png)
            )

    return JSONResponse({
        'status': status,
        'message': messages[status]
    })


@router.delete('/')
def delete_field(field_id: int, conn: CRUD = Depends(CRUD)) -> None:
    '''
    Deletes field from the database by id.

    Parameters:
        field_id: int
        conn: CRUD

    Returns:
        None
    '''
    logger.info(f'Deleting field {field_id} from the database...')
    conn.delete_field(field_id)
    rmtree(file_structure.get_base_path(field_id))
    logger.info(f'Deleted field {field_id} from the database')
