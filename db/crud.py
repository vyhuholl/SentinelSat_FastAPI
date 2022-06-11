import logging
from typing import Dict

from geojson_pydantic import FeatureCollection

from .config import SessionLocal
from .models import Field

logger = logging.getLogger()


class CRUD:
    '''
    A class for operating on a database.
    '''
    def __init__(self):
        '''
        Creates a new database connection on init.

        Parameters:
            self

        Returns:
            None
        '''
        self.db = SessionLocal()

    def get_status(self, field_id: int) -> str:
        '''
        Gets field status from the database.

        Parameters:
            self
            field_id: int

        Returns:
            str
        '''
        logger.info(f'Getting status of the field {field_id}...')
        field = self.db.query(Field).where(Field.id == field_id)
        return field.status

    def change_status(self, field_id: int, status: str) -> None:
        '''
        Changes the status of the field in the database.

        Parameters:
            self
            field_id: int
            status: str

        Returns:
            None
        '''
        logger.info(f'Changing status of the field {field_id} to {status}...')

        self.db.query(Field).where(Field.id == field_id).update(
            {'status': status}
            )

        self.db.commit()
        self.db.close()

    def add_field(self, field: FeatureCollection) -> int:
        '''
        Adds a new field to the database.  new field ID.

        Parameters:
            self
            field: FeatureCollection

        Returns:
            Integer
        '''
        logger.info('Adding new field to the database...')
        new_field = Field(geojson=field.dict(), status='Created')
        self.db.add(new_field)
        self.db.commit()
        self.db.refresh(new_field)
        new_field_id = new_field.id
        self.db.close()
        return new_field_id

    def get_field(self, field_id: int) -> Dict[str, str | Dict]:
        '''
        Gets GeoJSON image from the database by field id.

        Parameters:
            self
            field_id: int

        Returns:
            JSON
        '''
        logger.info(f'Getting GeoJSON image for the field {field_id}...')
        field = self.db.query(Field).where(Field.id == field_id)
        return field.geojson

    def save_ndvi_path(
        self, field_id: int, path: str, is_png: bool = False
            ) -> None:
        '''
        Saves path to the NDVI file (TIF or PNG) to the database.

        Parameters:
            self
            field_id: int
            path: str
            is_png: bool

        Returns:
            None
        '''
        logger.info(
            f'Saving path to the NDVI image for the field {field_id}...'
            )

        logger.info(f'Format of the NDVI image: {"PNG" if is_png else "TIF"}.')

        if is_png:
            self.db.query(Field).where(Field.id == field_id).update(
                {'ndvi_png': path, 'status': 'PNG ready'}
                )
        else:
            self.db.query(Field).where(Field.id == field_id).update(
                {'ndvi_tif': path, 'status': 'TIF ready'}
                )

        self.db.commit()
        self.db.close()

    def delete_field(self, field_id: int) -> None:
        '''
        Deletes the field and all associated information from the database.

        Parameters:
            self
            field_id: int

        Returns:
            None
        '''
        logger.info(f'Deleting the field {field_id} from the database...')
        self.db.query(Field).where(Field.id == field_id).delete()
        self.db.close()
