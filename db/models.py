from sqlalchemy import JSON, Column, Integer, String

from .config import Base


class Field(Base):  # type: ignore
    __tablename__ = 'fields'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    status = Column(String)
    geojson = Column(JSON)
    ndvi_tif = Column(String, default=None)
    ndvi_png = Column(String, default=None)
