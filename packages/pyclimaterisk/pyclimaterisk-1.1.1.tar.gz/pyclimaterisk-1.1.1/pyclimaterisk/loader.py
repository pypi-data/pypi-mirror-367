import polars as pl
import importlib.resources as pkg_resources
from . import data

def get_monthly_data():
    with pkg_resources.path(data, 'monthly.pq') as p:
        return pl.read_parquet(p)

def get_daily_data():
    with pkg_resources.path(data, 'daily.pq') as p:
        return pl.read_parquet(p)

def get_events():
    with pkg_resources.path(data, 'events.pq') as p:
        return pl.read_parquet(p)