"""
Data contract for CityBikes API response (Pandera model).
Acts as a "bouncer" for ingestion—only data being valid by passing this schema.
"""
import pandera.polars as pa

class CityBikeSchema(pa.DataFrameModel):
    """Schema for station data: name, free_bikes, empty_slots, latitude, longitude."""

    name: str
    free_bikes: int = pa.Field(ge=0)
    empty_slots: int = pa.Field(ge=0)
    latitude: float = pa.Field(in_range={"min_value": 42.2, "max_value": 42.6})
    longitude: float = pa.Field(in_range={"min_value": -71.3, "max_value": -70.8})
