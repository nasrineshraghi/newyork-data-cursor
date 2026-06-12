"""Streamlit dashboard for Citi Bike BigQuery data."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bigquery_client import create_bigquery_client, get_project_id, run_query  # noqa: E402
from citibike.queries import (  # noqa: E402
    REPORT_YEAR,
    busiest_day_sql,
    get_table_name,
    top_stations_sql,
    trips_by_month_sql,
    trips_by_weekday_sql,
)


def query_to_dataframe(client, sql: str) -> pd.DataFrame:
    return run_query(client, sql).to_dataframe()


@st.cache_data(ttl=3600, show_spinner="Loading data from BigQuery...")
def load_dashboard_data() -> dict[str, pd.DataFrame]:
    client = create_bigquery_client()
    table = get_table_name(get_project_id())

    return {
        "busiest_day": query_to_dataframe(client, busiest_day_sql(table)),
        "top_stations": query_to_dataframe(client, top_stations_sql(table, limit=10)),
        "trips_by_weekday": query_to_dataframe(client, trips_by_weekday_sql(table)),
        "trips_by_month": query_to_dataframe(client, trips_by_month_sql(table)),
    }


def main() -> None:
    st.set_page_config(page_title="Citi Bike Dashboard", layout="wide")
    st.title("Citi Bike Dashboard")
    st.caption(f"Live data from BigQuery · {REPORT_YEAR}")

    try:
        data = load_dashboard_data()
    except Exception as exc:
        st.error(f"Could not load data from BigQuery: {exc}")
        st.info("Check your `.env` file and service account credentials.")
        return

    busiest = data["busiest_day"].iloc[0]
    total_trips = int(data["trips_by_month"]["total_trips"].sum())
    top_station = data["top_stations"].iloc[0]["start_station_name"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total trips in 2018", f"{total_trips:,}")
    col2.metric("Busiest day", str(busiest["trip_date"]))
    col3.metric("Trips on busiest day", f"{int(busiest['total_trips']):,}")

    st.subheader("Top start stations")
    st.bar_chart(
        data["top_stations"].set_index("start_station_name")["total_trips"],
        height=350,
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Trips by weekday")
        st.bar_chart(
            data["trips_by_weekday"].set_index("weekday")["total_trips"],
            height=300,
        )

    with right:
        st.subheader("Trips by month")
        st.line_chart(
            data["trips_by_month"].set_index("month")["total_trips"],
            height=300,
        )

    with st.expander("View raw data"):
        st.dataframe(data["top_stations"], use_container_width=True)


if __name__ == "__main__":
    main()
