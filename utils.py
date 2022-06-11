import os
import re


def find_base_path(path: str, resolution: str = 'R10m') -> str:
    '''
    Finds base path for NIR and red files.

    Parameters:
        path: str
        resolution: str

    Returns:
        str
    '''
    is_resolution = len(
        [elem for elem in os.walk(path) if re.search(r'R[126]0m', elem)]
        ) > 0

    if is_resolution:
        result = [
            elem for elem in os.walk(path)
            if 'GRANULE' in elem[0] and 'IMG_DATA' in elem[0]
            and resolution in elem[0]
            ]
    else:
        result = [
            elem for elem in os.walk(path)
            if 'GRANULE' in elem[0] and 'IMG_DATA' in elem[0]
            ]

    if not result:
        raise ValueError(f'Impossible to parse folder {path}.')

    return result[0]
