import pandera as pa
from pandera import Column, DataFrameSchema
from pandera.typing import Series

OPD_INCIDENTS_SCHEMA = DataFrameSchema(
    {
        "occurred_on": Column(pa.DateTime, nullable=False),
        "crime_type": Column(pa.String, nullable=False),
        "lat": Column(pa.Float, nullable=True),
        "lon": Column(pa.Float, nullable=True),
    },
    name="opd_incidents_schema",
)

def validate(df):
    """Validate a DataFrame against the OPD schema. Raises `pandera.errors.SchemaErrors` on failure."""
    return OPD_INCIDENTS_SCHEMA.validate(df, lazy=True)
