from .geojson import GeoJSON
from .geoparquet import GeoParquet
from .geoframe import GeoFrame

import json
from urllib.request import urlopen
import pyarrow.parquet as pq
import pyarrow.feather as pf
from shapely import wkb, wkt
import pyarrow as pa
from fastkml.utils import find, find_all
from fastkml import KML
from fastkml import Placemark
import polars as pl


unpack = pl.col('features').struct.unnest()
unpack_features = pl.col('geometry').struct.unnest(), pl.col('properties').struct.unnest()



def read_geojson(file_path: str) -> GeoFrame:
    """Reads a GeoJSON file and returns a GeoFrame object."""
    with open(file_path) as response:
        geo_json_data = json.load(response)
        data = pl.DataFrame(geo_json_data)
        df = data.with_columns(unpack)\
        .with_columns(unpack_features)\
        .drop(['features','properties'])\
            # .with_columns(pl.col('coordinates').geo_ext.coords_to_wkt())
        # print(df)
        gdf = GeoFrame(
                df=df,
                coordinates_column='coordinates',
                raw=GeoJSON.from_dict(geo_json_data),
                read_format='geojson',
                )
        return gdf


def read_geojson_url(url: str) -> GeoJSON:
    with urlopen(url) as response:
        geo_json_data = json.load(response)
        data = pl.DataFrame(geo_json_data)
        exploded = data.with_columns(pl.col('features').struct.unnest())
        df = exploded.with_columns(unpack).drop(['features','properties'])
        # .geo.coords_to_wkt(col='coordinates')

        gdf = GeoFrame(
                df=df,
                coordinates_column='coordinates',
                raw=GeoJSON.from_dict(geo_json_data),
                read_format='geojson',
                )

    return gdf


# def read_kml(file_path, validate: bool = False) -> GeoFrame:
#     """Reads a KML file and returns a GeoFrame object."""
#     kml = KML.parse(file=file_path, validate=validate)

#     features = []

#     placemarks = list(find_all(kml, of_type=Placemark))
#     for placemark in placemarks:
#         features.append({
#                 "name": placemark.name,
#                 "description": placemark.description,
#                 "geometry_type": placemark.geometry.geom_type if placemark.geometry else None,
#                 "coordinates": placemark.geometry.coords,
#                 "wkt": placemark.geometry.wkt,
#                 # "extended_data": placemark.extended_data
#                 })

#     gdf = GeoFrame(
#         df=pl.DataFrame(features,schema_overrides={'coordinates':pl.Struct}),
#         crs="EPSG:4326"
#         ,wkt_column='wkt'
#         ,raw=kml
#         ,read_format='kml'
#     )
#     return gdf



def read_geoarrow(file_path: str, geometry_format: str ='wkb') -> GeoFrame:
    arrow_table = pf.read_table(file_path)    
    if geometry_format == 'wkb':
        gdf = GeoFrame(
                df=pl.from_pandas(arrow_table.to_pandas())
                ,raw=arrow_table
                ,read_format='geoarrow-wkb'
                )
        
    elif geometry_format == 'wkt':
        gdf = GeoFrame(
                df=pl.from_pandas(arrow_table.to_pandas())
                ,raw=arrow_table
                ,read_format='geoarrow-wkt'
                )


    elif geometry_format == 'interleaved':
        gdf = GeoFrame(
                df=pl.from_pandas(arrow_table.to_pandas())
                ,raw=arrow_table
                ,read_format='geoarrow-interleaved'
                )

    elif geometry_format == 'arrow':
        gdf = GeoFrame(
                df=pl.from_pandas(arrow_table.to_pandas())
                ,raw=arrow_table
                ,read_format='geoarrow'
                )

    return gdf


def read_parquet(file_path: str) -> GeoFrame:
    arrow_table = pq.read_table(file_path)
    gdf = GeoFrame(
                df=pl.from_pandas(arrow_table.to_pandas())
                ,raw=arrow_table
                ,read_format='geoparquet'
                )

    return gdf


def write_geojson(geojson: GeoJSON, filename: str, indent=None):
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(geojson.to_dict(), f, indent=indent)

