import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from db.config import create_db
from router import router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - '
           '[%(levelname)s] - '
           '%(name)s - '
           '(%(filename)s).%(funcName)s(%(lineno)d) - '
           '%(message)s',
)

app = FastAPI(
    title='sentinelsat_fastapi',
    description='An API for calculating NDVI of Sentinel satellite images.',
    version='1.0.0')

app.include_router(router)


@app.get('/')
async def root() -> RedirectResponse:
    '''
    Redirects from root to the docs page.

    Parameters:
        None

    Returns:
        RedirectResponse
    '''
    return RedirectResponse(url='/docs')


@app.on_event('startup')
def create_db_on_startup():
    '''
    Creates database on startup.

    Parameters:
        None

    Returns:
        None
    '''
    create_db()


if __name__ == '__main__':
    uvicorn.run(app)
