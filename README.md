# About
A web app for calculating [NDVI](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index) of [Sentinel](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/The_Sentinel_missions) satellite images (from the [Copernicus Open Access Hub](https://scihub.copernicus.eu), built with FastAPI. It provides an API that can:
* Add GeoJSON field to the database;
* Download satellite image of the field stored in the database;
* Calculate NDVI for the field (is calculated in the background) and store the NDVI image (as TIF and PNG files) in the file system;
* Get NDVI image (as TIF or PNG file) for the field;
* Delete field from the database and the corresponding images from the file system.
The file `example.geojson` contains a Moscow map in the GeoJSON format which you can use to test the app.
# REST API examples
