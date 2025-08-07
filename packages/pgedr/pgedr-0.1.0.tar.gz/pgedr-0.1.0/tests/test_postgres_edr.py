# Copyright 2025 Lincoln Institute of Land Policy
# SPDX-License-Identifier: MIT

from sqlalchemy.orm import Session, InstrumentedAttribute
import datetime
import pytest

from pygeoapi.provider.base import ProviderInvalidDataError

from pg_edr.edr import PostgresEDRProvider
from pg_edr.lib import get_column_from_qualified_name as gqname
from pg_edr.lib import recursive_getattr as rgetattr


@pytest.fixture(params=["tables", "views"])
def config(request):
    pygeoapi_config = {
        "name": "PostgresEDRProvider",
        "type": "edr",
        "data": {
            "host": "localhost",
            "dbname": "edr",
            "user": "postgres",
            "password": "changeMe",
            "search_path": ["capture"],
        },
        "table": "waterservices_daily",
        "edr_fields": {
            "id_field": "id",
            "geom_field": "geometry",
            "time_field": "time",
            "location_field": "monitoring_location_id",
            "result_field": "value",
            "parameter_id": "waterservices_timeseries_metadata.parameter_code",
            "parameter_name": "waterservices_timeseries_metadata.parameter_name",  # noqa
            "parameter_unit": "unit_of_measure",
        },
        "external_tables": {
            "waterservices_timeseries_metadata": {
                "foreign": "parameter_code",
                "remote": "parameter_code",
            }
        },
    }

    if request.param == "tables":
        return pygeoapi_config

    if request.param == "views":
        pygeoapi_config["table"] = "waterservices_daily_vw"
        pygeoapi_config["edr_fields"]["parameter_name"] = (
            "waterservices_timeseries_metadata_vw.parameter_name"
        )
        pygeoapi_config["edr_fields"]["parameter_id"] = (
            "waterservices_timeseries_metadata_vw.parameter_code"
        )
        pygeoapi_config["external_tables"] = {
            "waterservices_timeseries_metadata_vw": {
                "foreign": "parameter_code",
                "remote": "parameter_code",
            }
        }
        return pygeoapi_config

    return None


def test_invalid_config(config):
    config["edr_fields"]["parameter_id"] = "invalid_parameter_id"
    with pytest.raises(ProviderInvalidDataError):
        PostgresEDRProvider(config)


def test_external_table_relationships(config):
    p = PostgresEDRProvider(config)

    assert p.table in p.table_models
    assert len(p.table_models) == 2

    for table in p.external_tables:
        assert hasattr(p.model, table)


def test_can_query_single_edr_cols(config):
    p = PostgresEDRProvider(config)
    edr_attrs = [p.tc, p.pic, p.pnc, p.puc, p.lc, p.rc]
    assert all([isinstance(f, InstrumentedAttribute) for f in edr_attrs])
    assert gqname(p.model, p.parameter_id) == p.pic

    edr_names = [
        p.time_field,
        p.parameter_id,
        p.parameter_name,
        p.parameter_unit,
        p.location_field,
        p.result_field,
    ]
    edr_vals = [
        datetime.date(1925, 4, 10),
        "00060",
        "Discharge",
        "ft^3/s",
        "USGS-11281500",
        129.0,
    ]
    with Session(p._engine) as session:
        result = session.query(p.model).first()
        for edr_name, edr_val in zip(edr_names, edr_vals):
            assert rgetattr(result, edr_name) == edr_val

    with Session(p._engine) as session:
        query = session.query(p.model)
        for j in p.joins:
            query = query.join(*j)

        for edr_attr, edr_val in zip(edr_attrs, edr_vals):
            result = query.with_entities(edr_attr).limit(1).scalar()
            assert result == edr_val


def test_fields(config):
    """Testing query for a valid JSON object with geometry"""
    p = PostgresEDRProvider(config)

    assert len(p.fields) == 7
    for k, v in p.fields.items():
        assert len(k) == 5
        assert [k_ in ["title", "type", "x-ogc-unit"] for k_ in v]

    selected_mappings = {
        "00010": {
            "type": "number",
            "title": "Temperature, water",
            "x-ogc-unit": "degC",
        },
        "00060": {
            "type": "number",
            "title": "Discharge",
            "x-ogc-unit": "ft^3/s",
        },
        "00065": {
            "type": "number",
            "title": "Gage height",
            "x-ogc-unit": "ft",
        },
    }
    for k, v in selected_mappings.items():
        assert p.fields[k] == v


def test_locations(config):
    p = PostgresEDRProvider(config)

    locations = p.locations()

    assert locations["type"] == "FeatureCollection"
    assert len(locations["features"]) == 23

    feature = locations["features"][0]
    assert feature["id"] == "USGS-01465798"
    assert not feature.get("properties")


def test_locations_with_prop(config):
    config["properties"] = [
        "timeseries_id",
    ]
    p = PostgresEDRProvider(config)

    locations = p.locations()

    assert locations["type"] == "FeatureCollection"
    assert len(locations["features"]) == 23

    feature = locations["features"][0]
    assert feature["id"] == "USGS-01465798"
    assert feature.get("properties")
    assert "timeseries_id" in feature.get("properties")


def test_locations_limit(config):
    p = PostgresEDRProvider(config)

    locations = p.locations(limit=1)
    assert locations["type"] == "FeatureCollection"
    assert len(locations["features"]) == 1

    locations = p.locations(limit=500)
    assert locations["type"] == "FeatureCollection"
    assert len(locations["features"]) == 23

    locations = p.locations(limit=5)
    assert locations["type"] == "FeatureCollection"
    assert len(locations["features"]) == 5


def test_locations_bbox(config):
    p = PostgresEDRProvider(config)

    locations = p.locations(bbox=[-109, 31, -103, 37])
    assert len(locations["features"]) == 3


def test_locations_select_param(config):
    p = PostgresEDRProvider(config)

    locations = p.locations()
    print(locations["parameters"])
    assert len(locations["parameters"]) == 7

    locations = p.locations(select_properties=["00010"])
    assert len(locations["features"]) == 4
    assert len(locations["parameters"]) == 1

    locations = p.locations(select_properties=["00060"])
    assert len(locations["features"]) == 9
    assert len(locations["parameters"]) == 1

    locations = p.locations(select_properties=["00010", "00060"])
    assert len(locations["features"]) == 13
    assert len(locations["parameters"]) == 2


def test_get_location(config):
    p = PostgresEDRProvider(config)

    location = p.locations(location_id="USGS-01465798")
    assert [k in location for k in ["type", "domain", "parameters", "ranges"]]

    assert location["type"] == "Coverage"

    domain = location["domain"]
    assert domain["type"] == "Domain"
    assert domain["domainType"] == "PointSeries"

    print(domain["axes"]["t"])
    assert domain["axes"]["x"]["values"] == [-74.98516031202179]
    assert domain["axes"]["y"]["values"] == [40.05695572943445]
    assert domain["axes"]["t"]["values"] == [
        datetime.date(2024, 12, 8),
        datetime.date(2024, 12, 5),
        datetime.date(2024, 12, 2),
        datetime.date(2024, 11, 20),
        datetime.date(2024, 11, 17),
    ]

    t_len = len(domain["axes"]["t"]["values"])
    assert t_len == 5
    assert t_len == len(set(domain["axes"]["t"]["values"]))

    assert [k in location for k in ["type", "domain", "parameters", "ranges"]]

    for param in location["parameters"]:
        assert param in location["ranges"]

    for range in location["ranges"].values():
        assert range["axisNames"][0] in domain["axes"]
        assert range["shape"][0] == t_len
        assert len(range["values"]) == t_len
        assert range["values"] == [5.08, 5.22, 4.5, 6.94, 8.39]


def test_locations_time(config):
    p = PostgresEDRProvider(config)

    locations = p.locations(datetime_="2024-11-17")
    assert len(locations["features"]) == 1
    assert len(locations["parameters"]) == 1
