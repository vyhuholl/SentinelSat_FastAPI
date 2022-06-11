import os
from pathlib import Path

ZIPPED_DIR = 'zipped'
UNZIPPED_DIR = 'unzipped'
NDVI_DIR = 'ndvi'
TIF_FILENAME = 'NDVI.tif'
PNG_FILENAME = 'NDVI.png'


class FileStructure:
    '''
    A class for accessing files within a file system.

    Used format:
        base_path/
            field_id/
                ZIPPED_DIR/
                UNZIPPED_DIR/
                NDVI_DIR/
    '''
    def __init__(self, base_path: str) -> None:
        '''
        Creates an instance of the class.

        Parameters:
            self
            base_path: str

        Returns:
            None
        '''
        self.base_path = base_path

    def create_if_not_exists(self, field_id: int, dir_type: str = '') -> None:
        '''
        Creates a directory for a given field and the given type
        (zipped, unzipped, ndvi, or none) if the directory does not exists.
        '''
        try:
            Path(os.path.join(self.base_path, str(field_id), dir_type)).mkdir(
                parents=True, exist_ok=True
                )
        except FileExistsError:
            return

    def get_base_path(self, field_id: int) -> str:
        '''
        Gets path to the base field directory.

        Parameters:
            self
            field_id: int

        Returns:
            str
        '''
        self.create_if_not_exists(field_id)
        return os.path.join(self.base_path, str(field_id))

    def get_path_to_satellite_data(
        self, field_id: int, zipped: bool = True
            ) -> str:
        '''
        Gets path to the directory containing satellite data for the field.

        Parameters:
            self
            field_id: int
            zipped: bool

        Returns:
            str
        '''
        dir_type = ZIPPED_DIR if zipped else UNZIPPED_DIR
        self.create_if_not_exists(field_id, dir_type=dir_type)
        return os.path.join(self.base_path, str(field_id), dir_type)

    def get_ndvi_path(self, field_id: int, is_png: bool = False) -> str:
        '''
        Gets path to the NDVI image for the field.

        Parameters:
            self
            field_id: int
            is_png: bool

        Returns:
            str
        '''
        self.create_if_not_exists(field_id, dir_type=NDVI_DIR)
        filename = PNG_FILENAME if is_png else TIF_FILENAME
        return os.path.join(self.base_path, str(field_id), NDVI_DIR, filename)
