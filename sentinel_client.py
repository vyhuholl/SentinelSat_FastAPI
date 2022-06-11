import os
from typing import Dict

from sentinelsat import SentinelAPI


class SentinelClient:
    '''
    A client for working with Sentinel data.
    '''
    def __init__(self, api: SentinelAPI) -> None:
        '''
        Initializes the client.

        Parameters:
            self
            api: SentinelAPI

        Returns:
            None
        '''
        self.api = api

    def get_data(
        self, footprint: Dict[str, str | Dict], output_dir: str,
        max_day: int = 1, max_cloud_cover: int = 30
            ) -> str:
        '''
        Downloads data from Copernicus Open Access Hub by footprint.
        Returns path to the downloaded data.

        Parameters:
            self
            footprint: Dict[str, str | Dict]
            output_dir: str
            max_day: int
            max_cloud_cover: int

        Returns:
            str
        '''
        results = self.api.query(
            footprint, date=f'NOW-{max_day}DAY', platformname='Sentinel-2',
            cloudcoverpercentage=(0, max_cloud_cover)
            )

        best_result = self.api.to_dataframe(results).sort_values(
            ['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True]
            ).iloc[0]

        self.api.download(best_result['uuid'], directory_path=output_dir)
        return os.path.join(output_dir, f"{best_result['title']}.zip")
