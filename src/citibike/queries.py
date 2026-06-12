"""Shared Citi Bike SQL queries for scripts and dashboard."""

from __future__ import annotations

REPORT_YEAR = 2018
DEFAULT_TABLE = "{project}.data_engineering_int.newyork_citibike_trips"


def get_table_name(project_id: str) -> str:
    return DEFAULT_TABLE.format(project=project_id)


def busiest_day_sql(table: str) -> str:
    return f"""
        SELECT
          DATE(starttime) AS trip_date,
          COUNT(*) AS total_trips
        FROM `{table}`
        WHERE EXTRACT(YEAR FROM starttime) = {REPORT_YEAR}
        GROUP BY trip_date
        ORDER BY total_trips DESC
        LIMIT 1
    """


def top_stations_sql(table: str, limit: int = 10) -> str:
    return f"""
        SELECT
          start_station_name,
          COUNT(*) AS total_trips
        FROM `{table}`
        WHERE EXTRACT(YEAR FROM starttime) = {REPORT_YEAR}
          AND start_station_name IS NOT NULL
        GROUP BY start_station_name
        ORDER BY total_trips DESC
        LIMIT {limit}
    """


def trips_by_weekday_sql(table: str) -> str:
    return f"""
        SELECT
          FORMAT_DATE('%A', DATE(starttime)) AS weekday,
          EXTRACT(DAYOFWEEK FROM DATE(starttime)) AS day_number,
          COUNT(*) AS total_trips
        FROM `{table}`
        WHERE EXTRACT(YEAR FROM starttime) = {REPORT_YEAR}
        GROUP BY weekday, day_number
        ORDER BY day_number
    """


def trips_by_month_sql(table: str) -> str:
    return f"""
        SELECT
          FORMAT_DATE('%Y-%m', DATE(starttime)) AS month,
          COUNT(*) AS total_trips
        FROM `{table}`
        WHERE EXTRACT(YEAR FROM starttime) = {REPORT_YEAR}
        GROUP BY month
        ORDER BY month
    """
